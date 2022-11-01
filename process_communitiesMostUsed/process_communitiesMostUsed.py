import json, re, sys, os
import matplotlib.pyplot as plt
from tqdm import tqdm
import matplotlib.ticker as tkr
import matplotlib.lines as mlines

sys.path.append('../')
from tools.constants import asesToAvoid, communitiesToAvoid, ixpRegex, ixpNameMapping,snapshotDates
from tools.help_functions import human_format, readASesInRS, readASInfo


def plot(data, markers, totalComm, ipv, ixps, date):

    fig = plt.figure(figsize=(9/2.54, 6.75/2.54))
    ax = plt.axes()

    axisX = range(0,101)

    dataIXPs = [data[ixp][:101] for ixp in ixps]
    markersIXPs = [markers[ixp][:101] for ixp in ixps]
    totalCommIXPs = [totalComm[ixp] for ixp in ixps]

    colors = ['#481567FF','#2D708EFF','#3CBB75FF','#FDE725FF']

    for count, value in enumerate(ixps):
        #print(type(count), value, colors[count], min(101,len(dataIXPs[count])), len(dataIXPs[count]))
        
        plt.plot(range(0,min(101,len(dataIXPs[count]))), dataIXPs[count], label=value, color=colors[count])
    
        for xp, yp, m in zip(range(0,min(101,len(dataIXPs[count]))), dataIXPs[count], markersIXPs[count]):
            ax.scatter([xp],[yp], marker=m, color = colors[count], s=20, zorder=2)#, edgecolor='black')

    plt.axis([-1, 20, 0, max([max(q) for q in dataIXPs]) + max([max(q) for q in dataIXPs]) * 0.3])

    lines = ax.get_lines()
    
    legend1 = plt.legend([lines[i] for i in range(len(ixps))], [ixpNameMapping[value] + ' - ' + human_format(totalCommIXPs[count]) for count, value in enumerate(ixps)], loc=1, fontsize=5.2)

    blue_star = mlines.Line2D([], [], color='black', marker='x', linestyle='None',
                            markersize=2, label='Do not announce to')
    red_square = mlines.Line2D([], [], color='black', marker='o', linestyle='None',
                            markersize=2, label='Announce to')
    purple_triangle = mlines.Line2D([], [], color='black', marker='<', linestyle='None',
                            markersize=2, label='Add prepending')
    black_triangle = mlines.Line2D([], [], color='black', marker='^', linestyle='None',
                            markersize=2, label='Blackholing')

    legend2 = plt.legend(handles=[blue_star, red_square, purple_triangle, black_triangle], loc=9, fontsize=5.2, bbox_to_anchor=(0.15, 0.5, 0.5, 0.5))


    ax.add_artist(legend1)
    ax.add_artist(legend2)

    plt.xlabel('BGP communities sorted by # of times seen at IXP routes', fontsize=6.5)
    plt.ylabel('# of BGP communities seen at IXP routes', fontsize=7)
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

    def func(x, pos):  # formatter function takes tick label and tick position
        s = '%d' % x
        groups = []
        while s and s[-1].isdigit():
            groups.append(s[-3:])
            s = s[:-3]
        return s + ','.join(reversed(groups))

    y_format = tkr.FuncFormatter(func)
    ax.yaxis.set_major_formatter(y_format)

    if not os.path.isdir("./output_data/"):
        os.makedirs("./output_data/")

    #plt.title(date)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('./output_data/commWithHighestUsage' + '_' + str(date) + '_' + '_'.join(ixps) +  '_' + ipv + '.pdf')
    #plt.show()

def readASInfo():
    
    asInfo = {}

    with open('../tools/asnInfo.txt') as f:
        d = f.readlines()
        d = [i.strip() for i in d]

    for i in d:
        line = i.split("|")
        asInfo[line[0]] = line[2]

    return asInfo 


def main():

    if len(sys.argv) != 5:
        print("""\
        This script will process all the IXP BGP communities seen at IXPs and 
        it will output pre-processed info about action BGP communities

        Usage: process_communitiesMostUsed.py  preprocessed_bgp_communities_data_dir/ dateOrSnap v4OrV6 plotData

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

    actionCommunitiesData = {}
    communitiesMeaningIXPs = {}
    communitiesMeaningRegexIXPs = {}
    keysIXPs = {}

    actionCommunitiesFile = os.path.join(path, 'actionCommunitiesSeenAtall.json')
    with open(actionCommunitiesFile) as f:
        actionCommunitiesData = json.load(f)

    asInfo = readASInfo()

    communityNumbersList = {}

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
        
        
        for rs in actionCommunitiesData[ixp]:
            communityNumbersDict = {}
            if v4Orv6 in rs:
                communityNumbersList[ixp] = {}

                if 'snap' in date:
                    dateIXP = snapshotDates[v4Orv6][date][ixp]
                else:
                    dateIXP = date

                if dateIXP in actionCommunitiesData[ixp][rs].keys():
                    for comm in actionCommunitiesData[ixp][rs][dateIXP]:
                        if comm != 'communitiesPerASNsUsage' and 'rt' not in comm and 'ro' not in comm and comm.count(':') == 1:
                            communityNumbersDict[comm] = actionCommunitiesData[ixp][rs][dateIXP][comm]

                    communityNumbersList[ixp] = communityNumbersDict
                else:
                    communityNumbersList[ixp] = {-1:0}

                if not communityNumbersList[ixp]:
                    communityNumbersList[ixp] = {-1:0}


    totalComm = {}
    data = {}
    X = {}
    markers = {}

    for ixpDict in communityNumbersList.keys():

        #print(date, ixpDict)

        data[ixpDict] = []
        totalComm[ixpDict] = 0
        markers[ixpDict] = []
        X[ixpDict] = []

        for k in dict(sorted(communityNumbersList[ixpDict].items(), key=lambda item: item[1], reverse=True)):
            totalComm[ixpDict] += int(communityNumbersList[ixpDict][k])

            if k != -1:
                for reg in keysIXPs[ixpDict]:
                    reg = re.compile(reg)
                    match = re.search(reg, k)
                    if match:
                        if match.group():
                            group = match.group().split(":")[1]
                            tempX = communitiesMeaningRegexIXPs[ixpDict][reg].replace("AS", group)

                            if group in asInfo.keys():
                                tempX += ' (' + asInfo[group] + ')'
                        else:
                            tempX = communitiesMeaningRegexIXPs[ixpDict][reg]
            
                        break

                if "do not announce " in tempX.lower() or "block announcement" in tempX.lower() or "no export" in tempX.lower() or "do not redistribute" in tempX.lower():
                    markers[ixpDict].append('x')
                elif "announce to" in tempX.lower() or "announce a" in tempX.lower() or 'all' in tempX.lower() or 'export' in tempX.lower() or "redistribute" in tempX.lower():
                    markers[ixpDict].append('o')
                elif "prepend" in tempX.lower():
                    markers[ixpDict].append('<')
                elif "blackhole" in tempX.lower():
                    markers[ixpDict].append('^')
                else:
                    markers[ixpDict].append('2')

                X[ixpDict].append(tempX)
                data[ixpDict].append(communityNumbersList[ixpDict][k])

            else:
                data[ixpDict] = [0] * 101
                markers[ixpDict] = ['2'] * 101
                totalComm[ixpDict] = 0



    if not os.path.isdir("./output_data/"):
        os.makedirs("./output_data/")

    with open(os.path.join('output_data', v4Orv6 + '_' + date + '.txt'), 'w') as f:
        for ixp in ['ixbr', 'decix', 'linx', 'amsix', 'decixmad', 'decixnyc', 'bcix', 'netnodstocb']:
            tempX = [str(q) for q in X[ixp]]
            tempData = [str(q) for q in data[ixp]]

            f.write(ixp + '|' + ','.join(tempX) + '|' + ','.join(tempData) + '|' + str(totalComm[ixp]) +'\n')


    if plotData == 'y':
        plot(data, markers, totalComm, v4Orv6, ['ixbr', 'decix', 'linx', 'amsix'], date)
        plot(data, markers, totalComm, v4Orv6, ['decixmad', 'decixnyc', 'bcix', 'netnodstocb'], date)

if __name__ == '__main__':
    main()
