import json, sys, os
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
sys.path.append('../')
from tools.constants import asesToAvoid, communitiesToAvoid, ixpRegex, ixpNameMapping,snapshotDates
from tools.help_functions import human_format, readASesInRS, readASInfo

def plot(stackedDataV4, stackedDataV6, totalV4, totalV6, ipv, ixps, date):

    X = np.arange(len(ixps))
    fig = plt.figure(figsize=(9/2.54, 5/2.54))
    ax = plt.subplot(111)

    stackedV4 = [
        [stackedDataV4[i][0] for i in stackedDataV4.keys() if i in ixps],
        [stackedDataV4[i][1] for i in stackedDataV4.keys() if i in ixps]
    ]
    
    stackedV6 = [
        [stackedDataV6[i][0] for i in stackedDataV6.keys() if i in ixps],
        [stackedDataV6[i][1] for i in stackedDataV6.keys() if i in ixps]
    ]

    totalV4IXPs = [totalV4[i] for i in totalV4.keys() if i in ixps]
    totalV6IXPs = [totalV6[i] for i in totalV6.keys() if i in ixps]

    if ipv == 'ipv4':
        plt.bar(X-0.2, stackedV4[0], color = '#481567FF', width = 0.35)
        plt.bar(X-0.2, stackedV4[1], color = '#2D708EFF', width = 0.35, bottom=stackedV4[0])
    elif ipv == 'ipv6':
        plt.bar(X+0.2, stackedV6[0], color = '#481567FF', width = 0.35)
        plt.bar(X+0.2, stackedV6[1], color = '#2D708EFF', width = 0.35, bottom=stackedV6[0])
    else:
        plt.bar(X-0.2, stackedV4[0], color = '#481567FF', width = 0.35)
        plt.bar(X-0.2, stackedV4[1], color = '#2D708EFF', width = 0.35, bottom=stackedV4[0])
        plt.bar(X+0.2, stackedV6[0], color = '#481567FF', width = 0.35)
        plt.bar(X+0.2, stackedV6[1], color = '#2D708EFF', width = 0.35, bottom=stackedV6[0])

    #print(data)
    ixpsNames = [ixpNameMapping[i] for i in ixps]
    plt.ylabel('% of communities', fontsize='6')
    #plt.title(str(date))
    plt.xticks(X, ixpsNames)
    plt.tick_params(axis='x', pad=10, labelsize='6')
    plt.tick_params(axis='y', labelsize='6')


    plt.ylim([0,1.07])
    plt.ticklabel_format(style='plain', axis='y')
    plt.legend(labels=['IXP-defined BGP communities', 'Unknown BGP communities'], ncol=2, loc='upper center', bbox_to_anchor=(0.5, 1.16), fontsize=5)
    plt.text(-0.33, -0.09, 'IPv4', color='black', fontsize='6')
    plt.text(0.07, -0.09, 'IPv6', color='black', fontsize='6')
    plt.text(0.68, -0.09, 'IPv4', color='black', fontsize='6')
    plt.text(1.07, -0.09, 'IPv6', color='black', fontsize='6')
    plt.text(1.68, -0.09, 'IPv4', color='black', fontsize='6')
    plt.text(2.07, -0.09, 'IPv6', color='black', fontsize='6')
    plt.text(2.68, -0.09, 'IPv4', color='black', fontsize='6')
    plt.text(3.07, -0.09, 'IPv6', color='black', fontsize='6')

    if ipv == 'ipv4' or ipv == 'all':
        plt.text(-0.32, 1.015, human_format(round(totalV4IXPs[0], 2)), color='black', fontsize='4.4')
        plt.text(0.62, 1.015, human_format(round(totalV4IXPs[1], 2)), color='black', fontsize='4.4')
        plt.text(1.65, 1.015, human_format(round(totalV4IXPs[2], 2)), color='black', fontsize='4.4')
        plt.text(2.65, 1.015, human_format(round(totalV4IXPs[3], 2)),color='black', fontsize='4.4')

        plt.text(-0.35, 0.94, str(round(stackedV4[1][0] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
        plt.text(-0.34, 0.02, str(round(stackedV4[0][0] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
        plt.text(0.65, 0.94, str(round(stackedV4[1][1] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
        plt.text(0.64, 0.02, str(round(stackedV4[0][1] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
        plt.text(1.65, 0.94, str(round(stackedV4[1][2] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
        plt.text(1.65, 0.02, str(round(stackedV4[0][2] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
        plt.text(2.65, 0.94, str(round(stackedV4[1][3] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
        plt.text(2.65, 0.02, str(round(stackedV4[0][3] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')

    if ipv == 'ipv6' or ipv == 'all':

        plt.text(0.07, 1.015, human_format(round(totalV6IXPs[0], 2)), color='black', fontsize='4.4')
        plt.text(1.07, 1.015, human_format(round(totalV6IXPs[1], 2)), color='black', fontsize='4.4')
        plt.text(2.07, 1.015, human_format(round(totalV6IXPs[2], 2)), color='black', fontsize='4.4')
        plt.text(3.07, 1.015, human_format(round(totalV6IXPs[3], 2)), color='black', fontsize='4.4')

        plt.text(0.07, 0.94, str(round(stackedV6[1][0] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
        plt.text(0.06, 0.02, str(round(stackedV6[0][0] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
        plt.text(1.05, 0.94, str(round(stackedV6[1][1] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
        plt.text(1.05, 0.02, str(round(stackedV6[0][1] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
        plt.text(2.05, 0.94, str(round(stackedV6[1][2] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
        plt.text(2.05, 0.02, str(round(stackedV6[0][2] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
        plt.text(3.07, 0.94, str(round(stackedV6[1][3] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
        plt.text(3.05, 0.02, str(round(stackedV6[0][3] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')

    
    if not os.path.isdir("./output_data/"):
        os.makedirs("./output_data/")

    plt.tight_layout()
    plt.savefig('./output_data/ixpCommvsNonIxpComm' + '_' + str(date) + '_' + '_'.join(ixps) + '.pdf')
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

    allCommunitiesData = {}
    ixpCommunitiesData = {}

    dataV4 = {}
    dataV6 = {}
    stackedDataV4 = {}
    stackedDataV6 = {}
    totalV4 = {}
    totalV6 = {}

    print(date)
    for ixp in tqdm(['ixbr', 'decix', 'linx', 'amsix', 'decixmad', 'decixnyc', 'bcix', 'netnodstocb']):

        allCommunitiesData[ixp] = {}
        ixpCommunitiesData[ixp] = {}

        dataV4[ixp] = []
        dataV6[ixp] = []
        stackedDataV4[ixp] = []
        stackedDataV6[ixp] = []
        totalV4[ixp] = 0
        totalV6[ixp] = 0

        allCommunitiesFile = os.path.join(path, 'allCommunitiesSeenAt' + ixp + '.json')
        ixpCommunitiesFile = os.path.join(path, 'ixpCommunitiesSeenAt' + ixp + '.json')

        with open(allCommunitiesFile) as f:
            allCommunitiesData[ixp] = json.load(f)

        with open(ixpCommunitiesFile) as f:
            ixpCommunitiesData[ixp] = json.load(f)

        for rs in allCommunitiesData[ixp].keys():
            communityNumbersDict = {
                'ixp': 0,
                'nonIXP': 0
            }

            ixpComm = 0
            nonIxpComm = 0

            if 'v4' in rs:
                ipv = 'v4'
            elif 'v6' in rs:
                ipv = 'v6'

            if 'snap' in date:
                dateIXP = snapshotDates[ipv][date][ixp]
            else:
                dateIXP = date

            if dateIXP in allCommunitiesData[ixp][rs].keys():
                for comm in allCommunitiesData[ixp][rs][dateIXP].keys():

                    if comm != "communitiesPerASNsUsage":

                        if comm in ixpCommunitiesData[ixp][rs][dateIXP].keys():
                            ixpComm += allCommunitiesData[ixp][rs][dateIXP][comm]
                        else:
                            nonIxpComm += allCommunitiesData[ixp][rs][dateIXP][comm]

                communityNumbersDict['ixp'] = ixpComm
                communityNumbersDict['nonIXP'] = nonIxpComm

            if 'v4' in rs:
                dataV4[ixp].append(communityNumbersDict['ixp'])
                dataV4[ixp].append(communityNumbersDict['nonIXP'])
                try:
                    stackedDataV4[ixp].append(communityNumbersDict['ixp'] / (communityNumbersDict['ixp']+communityNumbersDict['nonIXP']))
                except ZeroDivisionError:
                    stackedDataV4[ixp].append(0)
                
                try:
                    stackedDataV4[ixp].append(communityNumbersDict['nonIXP'] / (communityNumbersDict['ixp']+communityNumbersDict['nonIXP']))
                except ZeroDivisionError:
                    stackedDataV4[ixp].append(0)

            elif 'v6' in rs:
                dataV6[ixp].append(communityNumbersDict['ixp'])
                dataV6[ixp].append(communityNumbersDict['nonIXP'])

                try:
                    stackedDataV6[ixp].append(communityNumbersDict['ixp'] / (communityNumbersDict['ixp']+communityNumbersDict['nonIXP']))
                except ZeroDivisionError:
                    stackedDataV6[ixp].append(0)
                try:
                    stackedDataV6[ixp].append(communityNumbersDict['nonIXP'] / (communityNumbersDict['ixp']+communityNumbersDict['nonIXP']))
                except ZeroDivisionError:
                    stackedDataV6[ixp].append(0)


        totalV4[ixp] = dataV4[ixp][0] + dataV4[ixp][1]
        totalV6[ixp] = dataV6[ixp][0] + dataV6[ixp][1]
        
    if not os.path.isdir("./output_data/"):
        os.makedirs("./output_data/")

    with open(os.path.join('output_data', date + '.txt'), 'w') as f:
        for ixp in ['ixbr', 'decix', 'linx', 'amsix', 'decixmad', 'decixnyc', 'bcix', 'netnodstocb']:
            f.write(ixp + '|' + str(dataV4[ixp][0]) + '|' + str(dataV4[ixp][1]) + '|' + str(stackedDataV4[ixp][0]) + '|' + str(stackedDataV4[ixp][1]) + '|' + \
                    str(dataV6[ixp][0]) + '|' + str(dataV6[ixp][1]) + '|' + str(stackedDataV6[ixp][0]) + '|' + str(stackedDataV6[ixp][1]) + '|' + \
                    str(totalV4[ixp]) + '|' + str(totalV6[ixp]) + '\n')


    if plotData == 'y':
        plot(stackedDataV4, stackedDataV6, totalV4, totalV6, 'all', ['ixbr', 'decix', 'linx', 'amsix'], date)
        plot(stackedDataV4, stackedDataV6, totalV4, totalV6, 'all', ['decixmad', 'decixnyc', 'bcix', 'netnodstocb'], date)


if __name__ == '__main__':
    main()
