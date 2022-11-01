from collections import defaultdict
import json, sys, os, gzip
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from os import listdir
from os.path import isfile, join

sys.path.append('../')
from tools.constants import asesToAvoid, communitiesToAvoid, ixpRegex, ixpNameMapping,snapshotDates
from tools.help_functions import human_format, readASesInRS, readASInfo

def human_format2(num):
    num = float('{:.1f}'.format(num))
    #print(num)
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    #if magnitude == 1:
    #    magnitude += 1
    #    num /= 1000.0
    #print(num, round(num, 2),'\n')
    num = round(num, 1)
    return '{}{}'.format('{:1f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

def getListOfASesInRS():
    ASesInRSV4 = {}
    ASesInRSV6 = {}

    with open('../tools/asesInRS.txt') as f:
        d = f.readlines()
        d = [i.strip() for i in d]

    for i in d:
        splitLine = i.split('|')

        if splitLine[2] == 'v4':
            if splitLine[1] not in ASesInRSV4.keys():
                ASesInRSV4[splitLine[1]] = defaultdict(set)

            tempASes = set(splitLine[3].split(","))
            ASesInRSV4[splitLine[1]][splitLine[0]].update(tempASes)

        elif splitLine[2] == 'v6':
            if splitLine[1] not in ASesInRSV6.keys():
                ASesInRSV6[splitLine[1]] = defaultdict(set)

            tempASes = set(splitLine[3].split(","))
            ASesInRSV6[splitLine[1]][splitLine[0]].update(tempASes)

    return ASesInRSV4,ASesInRSV6


def getRoutesWithActionComm(actionCommunitiesDataWithPerASN, date, ixp, rs, ipv):

    routesWithComm = set()
    actionCommDate = set()

    #print(actionCommunitiesDataWithPerASN[ixp][rs][date].keys())
    for k in actionCommunitiesDataWithPerASN[ixp][rs][date]['communitiesPerASNsUsage'].keys():
        for q in actionCommunitiesDataWithPerASN[ixp][rs][date]['communitiesPerASNsUsage'][k].keys():
            if q != 'announcedPrefixes':
                actionCommDate.add(q)

    if ixp == 'decixmad' or ixp == 'decixnyc':
        ixpFile = 'decixothers'
    elif ixp == 'netnodstocb':
        ixpFile = 'netnod'
    else:
        ixpFile = ixp

    #print(rs)
    file = "../BGPFiles/" + ixpFile + '/' + date + "/" + rs + '_received_' + date + '.csv.gz'

    #print(file)
    rows = []
    try:
        with gzip.open(file,'rb') as f:
            file_content=f.readlines()
        
        for row in file_content:
            rows.append(row.decode('utf8'))

    except:
        print("Problem open gzip file")
        return set()

    
    for i in tqdm(rows):
        prefix, gateway, ASPath, commList, largeCommList, extCommList, age, cached, neighbor = i.split("|")

        if (ixp == 'amsix' and neighbor.strip() == 'RS1v4') or (ixp == 'amsix' and neighbor.strip() == 'RS1v6') \
            or ixp in ['ixbr', 'decix', 'linx', 'decixmad', 'decixnyc', 'bcix','netnodstocb']:

            for k in actionCommDate:
                if k in commList:
                    routesWithComm.add(i)
                    break

    return routesWithComm


def plot(dataV4, dataV6, totalASesV4, totalASesV6, routesWithCommV4, routesWithCommV6, ipv, ixps, date):

    X = np.arange(len(ixps))
    fig = plt.figure(figsize=(9/2.54, 6.75/2.54))
    ax = plt.subplot(111)

    
    dataV4IXPs = [dataV4[i][1] for i in dataV4.keys() if i in ixps]
    dataV6IXPs = [dataV6[i][1] for i in dataV6.keys() if i in ixps]

    totalV4IXPs = [totalASesV4[i] for i in totalASesV4.keys() if i in ixps]
    totalV6IXPs = [totalASesV6[i] for i in totalASesV6.keys() if i in ixps]

    routesWithCommV4IXPs = [routesWithCommV4[i] for i in ixps]
    routesWithCommV6IXPs = [routesWithCommV6[i] for i in ixps]

    #print(dataV4IXPs, totalASesV4)

    if ipv =='v4' or ipv == 'all':
        ax.bar(X - 0.2, dataV4IXPs, color='#2D708EFF', width = 0.35)
    
    if ipv =='v6' or ipv == 'all':
        ax.bar(X + 0.2, dataV6IXPs, color='#481567FF', width = 0.35)

    ax.set_ylabel('# of ASes', fontsize='8')
    ticksIXPs = [ixpNameMapping[q] for q in ixps]
    plt.xticks(X, ticksIXPs)
    ax.tick_params(axis='x', pad=2, labelsize='8')
    ax.tick_params(axis='y', labelsize='8')

    plt.ylim([0, max([dataV4[i][1] for i in dataV4.keys() if i in ixps]) + 50])

    plt.ticklabel_format(style='plain', axis='y')
    ax.legend(labels=['IPv4', 'IPv6'], ncol=2, loc='upper center', bbox_to_anchor=(0.5, 1.01), fontsize=7)

    plt.text(-0.42, dataV4IXPs[0] + 10, human_format2(routesWithCommV4IXPs[0]), color='black', fontsize='6.5')
    plt.text(0.64, dataV4IXPs[1] + 10, human_format2(routesWithCommV4IXPs[1]), color='black', fontsize='6.5')
    plt.text(1.57, dataV4IXPs[2] + 10, human_format2(routesWithCommV4IXPs[2]), color='black', fontsize='6.5')
    plt.text(2.57, dataV4IXPs[3] + 10, human_format2(routesWithCommV4IXPs[3]), color='black', fontsize='6.5')

    plt.text(0.06, dataV6IXPs[0] + 10, human_format2(routesWithCommV6IXPs[0]), color='black', fontsize='6.5')
    plt.text(1.01, dataV6IXPs[1] + 10, human_format2(routesWithCommV6IXPs[1]), color='black', fontsize='6.5')
    plt.text(2.02, dataV6IXPs[2] + 10, human_format2(routesWithCommV6IXPs[2]), color='black', fontsize='6.5')
    plt.text(3.02, dataV6IXPs[3] + 10, human_format2(routesWithCommV6IXPs[3]), color='black', fontsize='6.5')


    if ipv == 'v4' or ipv == 'all':
        if dataV4IXPs[0] > 0 and totalV4IXPs[0] > 0:
            plt.text(-0.23, 2 + max([dataV4[i][1] for i in dataV4.keys() if i in ixps])/100, str(round((dataV4IXPs[0]/totalV4IXPs[0]) * 100, 1)) + '%', color='white', fontsize='5.3', rotation=90)
        
        if dataV4IXPs[1] > 0 and totalV4IXPs[1] > 0:
            plt.text(0.78, 2 + max([dataV4[i][1] for i in dataV4.keys() if i in ixps])/100, str(round((dataV4IXPs[1]/totalV4IXPs[1]) * 100, 1)) + '%', color='white', fontsize='5.3', rotation=90)
        
        if dataV4IXPs[2] > 0 and totalV4IXPs[2] > 0:
            plt.text(1.78, 2 + max([dataV4[i][1] for i in dataV4.keys() if i in ixps])/100, str(round((dataV4IXPs[2]/totalV4IXPs[2]) * 100, 1)) + '%', color='white', fontsize='5.3', rotation=90)
        
        if dataV4IXPs[3] > 0 and totalV4IXPs[3] > 0:
            plt.text(2.78, 2 + max([dataV4[i][1] for i in dataV4.keys() if i in ixps])/100, str(round((dataV4IXPs[3]/totalV4IXPs[3]) * 100, 1)) + '%', color='white', fontsize='5.3', rotation=90)

        
    
    if ipv == 'v6' or ipv == 'all':
        if dataV6IXPs[0] > 0 and totalV6IXPs[0] > 0:
            plt.text(0.12, 2 + max([dataV4[i][1] for i in dataV4.keys() if i in ixps])/100, str(round((dataV6IXPs[0]/totalV6IXPs[0]) * 100, 1)) + '%', color='white', fontsize='5.3', rotation=90)
        
        if dataV6IXPs[1] > 0 and totalV6IXPs[1] > 0:
            plt.text(1.14, 2 + max([dataV4[i][1] for i in dataV4.keys() if i in ixps])/100, str(round((dataV6IXPs[1]/totalV6IXPs[1]) * 100, 1)) + '%', color='white', fontsize='5.3', rotation=90)
        
        if dataV6IXPs[2] > 0 and totalV6IXPs[2] > 0:
            plt.text(2.14, 2 + max([dataV4[i][1] for i in dataV4.keys() if i in ixps])/100, str(round((dataV6IXPs[2]/totalV6IXPs[2]) * 100, 1)) + '%', color='white', fontsize='5.3', rotation=90)
        
        if dataV6IXPs[3] > 0 and totalV6IXPs[3] > 0:
            plt.text(3.14, 2 + max([dataV4[i][1] for i in dataV4.keys() if i in ixps])/100, str(round((dataV6IXPs[3]/totalV6IXPs[3]) * 100, 1)) + '%', color='white', fontsize='5.3', rotation=90)

    if not os.path.isdir("./output_data/"):
        os.makedirs("./output_data/")

    plt.tight_layout()
    plt.savefig('./output_data/asesUsingAction' + '_' + str(date) + '_' + '_'.join(ixps) + '.pdf')
    #plt.show()


def main():

    if len(sys.argv) != 4:
        print("""\
        This script will process all the IXP BGP communities seen at IXPs and 
        it will output pre-processed info about action BGP communities

        Usage:  process_communityPerType.py  preprocessed_bgp_communities_data_dir/ dateOrSnap plotData

        preprocessed_bgp_communities_data_dir - dir with preprocessed data for bgp communities
        dateOrSnap - input date in YYYY-MM-DD format or desired snapshot (snap1, snap2, ..., snap12)
        plotData - y or n
        """)
        sys.exit(0)

    path = sys.argv[1]
    date = sys.argv[2]
    plotData = sys.argv[3]

    ASesInRSV4 = {}
    ASesInRSV6 = {}
    ASesInRSV4, ASesInRSV6 = getListOfASesInRS()

    ixpCommunitiesData = {}
    actionCommunitiesDataWithPerASN = {}

    actionCommunitiesFileWithPerASN = os.path.join(path, 'actionCommunitiesDataWithPerASNall.json')
    with open(actionCommunitiesFileWithPerASN) as f:
        actionCommunitiesDataWithPerASN = json.load(f)

    dataV4 = defaultdict(list)
    dataV6 = defaultdict(list)
    totalASesV4 = {}
    totalASesV6 = {}
    routesWithCommV4 = {}
    routesWithCommV6 = {}
    
    print(date)
    for ixp in tqdm(['ixbr', 'decix', 'linx', 'amsix', 'decixmad', 'decixnyc', 'bcix', 'netnodstocb']):
        ixpCommunitiesData[ixp] = {}

        dataV4[ixp] = []
        dataV6[ixp] = []
        totalASesV4[ixp] = 0
        totalASesV6[ixp] = 0

        routesWithCommV4[ixp] = 0
        routesWithCommV6[ixp] = 0


        ixpCommunitiesFile = os.path.join(path, 'ixpCommunitiesSeenAt' + ixp + '.json')

        with open(ixpCommunitiesFile) as f:
            ixpCommunitiesData[ixp] = json.load(f)

        for rs in ixpCommunitiesData[ixp].keys():
            #print(ixp,rs)
            communityNumbersDict = {
                'informational': 0,
                'action': 0,
            }

            tempASes = set()

            if 'v4' in rs:
                ipv = 'v4'
            elif 'v6' in rs:
                ipv = 'v6'

            if 'snap' in date:
                dateIXP = snapshotDates[ipv][date][ixp]
            else:
                dateIXP = date

            #print(dateIXP)
            if dateIXP in ixpCommunitiesData[ixp][rs].keys():
                
                actionRoutes = getRoutesWithActionComm(actionCommunitiesDataWithPerASN, dateIXP, ixp, rs, ipv)
                if ipv == 'v4':
                    routesWithCommV4[ixp] = len(actionRoutes)
                else:
                    routesWithCommV6[ixp] = len(actionRoutes)
                
                #print(routesWithCommV4[ixp])

                for asn in ixpCommunitiesData[ixp][rs][dateIXP]['communitiesPerASNsUsage']:

                    if asn in actionCommunitiesDataWithPerASN[ixp][rs][dateIXP]['communitiesPerASNsUsage']:
                        communityNumbersDict['action'] += 1

                    else:
                        communityNumbersDict['informational'] += 1
                        
                    tempASes.add(asn)
                        
            if 'v4' in rs:
                dataV4[ixp].append(communityNumbersDict['informational'])
                dataV4[ixp].append(communityNumbersDict['action'])
                totalASesV4[ixp] = len(ASesInRSV4[ixp][dateIXP])

            if 'v6' in rs:
                dataV6[ixp].append(communityNumbersDict['informational'])
                dataV6[ixp].append(communityNumbersDict['action'])
                totalASesV6[ixp] = len(ASesInRSV6[ixp][dateIXP])

    if not os.path.isdir("./output_data/"):
        os.makedirs("./output_data/")

    print(routesWithCommV4)
    print(routesWithCommV6)

    with open(os.path.join('output_data', date + '.txt'), 'w') as f:
        for ixp in ['ixbr', 'decix', 'linx', 'amsix', 'decixmad', 'decixnyc', 'bcix', 'netnodstocb']:
            f.write(ixp + '|' + str(dataV4[ixp][0]) + '|' + str(dataV4[ixp][1]) \
                        + '|' + str(dataV6[ixp][0]) + '|' + str(dataV6[ixp][1]) \
                        + '|' + str(totalASesV4[ixp]) + '|' + str(totalASesV6[ixp]) + '\n')

    if plotData == 'y':
        plot(dataV4, dataV6, totalASesV4, totalASesV6, routesWithCommV4, routesWithCommV6, 'all', ['ixbr', 'decix', 'linx', 'amsix'], date)
        plot(dataV4, dataV6, totalASesV4, totalASesV6, routesWithCommV4, routesWithCommV6, 'all', ['decixmad', 'decixnyc', 'bcix', 'netnodstocb'], date)


if __name__ == '__main__':
    main()