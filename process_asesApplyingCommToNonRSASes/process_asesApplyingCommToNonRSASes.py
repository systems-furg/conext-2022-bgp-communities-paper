import json, re, sys, os
import matplotlib.pyplot as plt
from tqdm import tqdm
import matplotlib.ticker as tkr
import matplotlib.lines as mlines
from collections import defaultdict

sys.path.append('../')
from tools.constants import asesToAvoid, communitiesToAvoid, ixpRegex, ixpNameMapping,snapshotDates
from tools.help_functions import human_format, readASesInRS, readASInfo


def plot(data, sum, ipv, ixps, date):
    fig = plt.figure(figsize=(9/2.54, 6.75/2.54))
    ax = plt.axes()

    minAll = min([len(q) for q in data])
    X = range(0,101)

    markers = ['.'] * 101
    #print(markers)
    colors = ['#481567FF','#2D708EFF','#3CBB75FF','#FDE725FF']

    dataIXPs = [data[ixp][:101] for ixp in ixps]
    sumIXPs = [sum[ixp] for ixp in ixps]

    for q in range(len(dataIXPs)):
        if len(dataIXPs[q]) == 0:
            dataIXPs[q] = [0] * 101
    
    for count, value in enumerate(ixps):
        #print(count, value, colors[count], min(101,len(dataIXPs[count])), len(dataIXPs[count]))
        
        plt.plot(range(0,min(101,len(dataIXPs[count]))), dataIXPs[count], label=value, color=colors[count])
    
        for xp, yp, m in zip(range(0,min(101,len(dataIXPs[count]))), dataIXPs[count], markers):
            #print(m)
            ax.scatter([xp],[yp], marker=m, color = colors[count], s=20, zorder=2)#, edgecolor='black')


    plt.axis([-1, 10, 0, max([max(q) for q in dataIXPs]) + max([max(q) for q in dataIXPs]) * 0.2])

    lines = ax.get_lines()
    #print(lines)
    
    legend1 = plt.legend([lines[i] for i in range(len(ixps))], [ixpNameMapping[value] + ' - ' + human_format(sumIXPs[count]) for count, value in enumerate(ixps)], loc=1, fontsize=5.2)

    ax.add_artist(legend1)

    def func(x, pos):  # formatter function takes tick label and tick position
        s = '%d' % x
        groups = []
        while s and s[-1].isdigit():
            groups.append(s[-3:])
            s = s[:-3]
        return s + ','.join(reversed(groups))

    y_format = tkr.FuncFormatter(func)
    ax.yaxis.set_major_formatter(y_format)

    plt.xlabel('ASes sorted by # of BGP communities targeting ASes not in RS', fontsize=6.1)
    plt.ylabel('# of BGP communities seen targeting ASes not in RS', fontsize=6.1)
    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False,
        labelsize=6
    )

    plt.tick_params(
        axis='y',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        labelsize=6
    )

    if not os.path.isdir("./output_data/"):
        os.makedirs("./output_data/")

    #plt.title(date)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('./output_data/asesApplyingCommToNonRSAses' + '_' + str(date) + '_' + '_'.join(ixps) +  '_' + ipv + '.pdf')



def main():

    if len(sys.argv) != 5:
        print("""\
        This script will process all the IXP BGP communities seen at IXPs and 
        it will output pre-processed info about action BGP communities

        Usage: process_asesApplyingCommToNonRSASes.py  preprocessed_bgp_communities_data_dir/ dateOrSnap v4OrV6 plotData

        preprocessed_bgp_communities_data_dir - dir with preprocessed data for bgp communities
        dateOrSnap - input date in YYYY-MM-DD format or desired snapshot (snap1, snap2, ..., snap12)
        v4OrV6 - v4 or v6
        plotData - y or n
        """)
        sys.exit(0)

    path = sys.argv[1]
    date = sys.argv[2]
    v4Orv6 = sys.argv[3]
    plotData = sys.argv[4]

    actionCommunitiesDataWithPerASN = {}
    communitiesMeaningIXPs = {}
    communitiesMeaningRegexIXPs = {}
    keysIXPs = {}

    actionCommunitiesFileWithPerASN = os.path.join(path, 'actionCommunitiesDataWithPerASNall.json')
    with open(actionCommunitiesFileWithPerASN) as f:
        actionCommunitiesDataWithPerASN = json.load(f)

    asInfo = readASInfo()
    ASesInRS = readASesInRS()

    communityNumbersDict = {}

    print(date)
    for ixp in tqdm(['ixbr', 'decix', 'linx', 'amsix', 'decixmad', 'decixnyc', 'bcix', 'netnodstocb']):
        
        communitiesMeaningIXPs[ixp] = {}
        communitiesMeaningRegexIXPs[ixp] = {}
        keysIXPs[ixp] = []
        
        severalRegex = []

        with open('../tools/communitiesDictionaries/' + ixp + 'ParsedCommunitiesAction.txt') as f:
            d = f.readlines()

        d = [i.replace('*', '\d+').strip() for i in d]
        for i in d:
            severalRegex.append('^' + i.split("|")[0] + '$')

            newI = i.replace('AS$1', 'AS')
            newI = newI.replace('AS$2', 'AS')
            line = newI.split("|")
            communitiesMeaningIXPs[ixp]['^' + line[0] + '$'] = line[1]
            communitiesMeaningRegexIXPs[ixp][re.compile('^' + line[0] + '$')] = line[1]

        keysIXPs[ixp]=list(communitiesMeaningIXPs[ixp].keys())
        keysIXPs[ixp].sort(key=lambda s:'(\\d+)' in s)

        for rs in actionCommunitiesDataWithPerASN[ixp]:
            if v4Orv6 in rs:
                ixpMembership = []

                if 'snap' in date:
                    dateIXP = snapshotDates[v4Orv6][date][ixp]
                else:
                    dateIXP = date

                if dateIXP in actionCommunitiesDataWithPerASN[ixp][rs].keys():
                    ixpMembership = list(ASesInRS[v4Orv6][ixp][dateIXP])
                    
                    communityNumbersDict[ixp] = {}

                    #dict with AS targeting non member as key and number of communities applied to them as value
                    asTargettingNonRSAS = {}

                    for asn in list(actionCommunitiesDataWithPerASN[ixp][rs][dateIXP]['communitiesPerASNsUsage'].keys()):
                        for comm in actionCommunitiesDataWithPerASN[ixp][rs][dateIXP]['communitiesPerASNsUsage'][asn]:
                            if comm != 'announcedPrefixes' and comm not in communitiesToAvoid[ixp] and 'rt' not in comm and 'ro' not in comm and comm.count(':') == 1:
                                for type in ['avoid', 'allow', 'prepend']:
                                    match = re.search(ixpRegex[type][ixp], comm)
                                    if match:
                                        matchASNList = [q for q in match.groups() if q]

                                        if len(matchASNList) > 0:
                                            matchASN = matchASNList[0]
                                            if matchASN not in ixpMembership and matchASN not in asesToAvoid[ixp]:

                                                if asn not in asTargettingNonRSAS.keys():
                                                    asTargettingNonRSAS[asn] = actionCommunitiesDataWithPerASN[ixp][rs][dateIXP]['communitiesPerASNsUsage'][asn][comm]
                                                else:
                                                    asTargettingNonRSAS[asn] += actionCommunitiesDataWithPerASN[ixp][rs][dateIXP]['communitiesPerASNsUsage'][asn][comm]

                                        break

                        
                    for asn in asTargettingNonRSAS.keys():
                        communityNumbersDict[ixp][asn] = asTargettingNonRSAS[asn]

                else:
                    communityNumbersDict[ixp] = {-1:0}

                if not communityNumbersDict[ixp]:
                    communityNumbersDict[ixp] = {-1:0}

    data = {}
    X = {}
    sum = {}

    #print(date, communityNumbersDict.keys())
    for ixpDict in communityNumbersDict.keys():
        data[ixpDict] = []
        X[ixpDict] = []
        sum[ixpDict] = 0

        for k in dict(sorted(communityNumbersDict[ixpDict].items(), key=lambda item: item[1], reverse=True)):
            if k != -1:
                sum[ixpDict] += communityNumbersDict[ixpDict][k]
                X[ixpDict].append(k)
                data[ixpDict].append(communityNumbersDict[ixpDict][k])
            else:
                data[ixpDict] = [0] * 101
                sum[ixpDict] = 0 


    if not os.path.isdir("./output_data/"):
        os.makedirs("./output_data/")
        

    with open(os.path.join('output_data/' + v4Orv6 + '_' + date + '.txt'), 'w') as f:
        for ixp in ['ixbr', 'decix', 'linx', 'amsix', 'decixmad', 'decixnyc', 'bcix', 'netnodstocb']:
            tempX = [str(q) for q in X[ixp]]
            tempData = [str(q) for q in data[ixp]]

            f.write(ixp + '|' + ','.join(tempX) + '|' + ','.join(tempData) + '|' + str(sum[ixp]) +'\n')


    if plotData == 'y':
        plot(data, sum, v4Orv6, ['ixbr', 'decix', 'linx', 'amsix'], date)
        plot(data, sum, v4Orv6, ['decixmad', 'decixnyc', 'bcix', 'netnodstocb'], date)


if __name__ == '__main__':
    main()



