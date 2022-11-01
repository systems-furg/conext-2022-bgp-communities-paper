import json, re, sys, os
import matplotlib.pyplot as plt
from tqdm import tqdm
import matplotlib.ticker as tkr
import matplotlib.lines as mlines
from collections import defaultdict

sys.path.append('../')
from tools.constants import asesToAvoid, communitiesToAvoid, ixpRegex, ixpNameMapping, snapshotDates
from tools.help_functions import human_format, readASesInRS, readASInfo




def plot(data, markers, totalComm, ipv, ixps, date):

    fig = plt.figure(figsize=(9/2.54, 6.75/2.54))
    ax = plt.axes()

    #X = np.linspace(0, 101, num=101)
    X = range(0,101)

    dataIXPs = [data[ixp][:101] for ixp in ixps]
    markersIXPs = [markers[ixp][:101] for ixp in ixps]
    totalCommIXPs = [totalComm[ixp] for ixp in ixps]

    for q in range(len(dataIXPs)):
        if len(dataIXPs[q]) == 0:
            dataIXPs[q] = [0] * 101

    colors = ['#481567FF','#2D708EFF','#3CBB75FF','#FDE725FF']

    for count, value in enumerate(ixps):
        #print(count, value, colors[count], min(101,len(dataIXPs[count])), len(dataIXPs[count]))
        
        plt.plot(range(0,min(101,len(dataIXPs[count]))), dataIXPs[count], label=value, color=colors[count])
    
        for xp, yp, m in zip(range(0,min(101,len(dataIXPs[count]))), dataIXPs[count], markersIXPs[count]):
            ax.scatter([xp],[yp], marker=m, color = colors[count], s=20, zorder=2)#, edgecolor='black')


    plt.axis([-1, 20, 0, max([max(q) for q in dataIXPs]) + max([max(q) for q in dataIXPs]) * 0.2])

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

    legend2 = plt.legend(handles=[blue_star, red_square, purple_triangle, black_triangle], loc=9, fontsize=5.5, bbox_to_anchor=(0.54, 0.27, 0.5, 0.5))
    #legend2 = plt.legend(handles=[blue_star, red_square, purple_triangle, black_triangle], loc=9, fontsize=5.2, bbox_to_anchor=(0.18, 0.5, 0.5, 0.5))

    ax.add_artist(legend1)
    ax.add_artist(legend2)

    def func(x, pos):  # formatter function takes tick label and tick position
        s = '%d' % x
        groups = []
        while s and s[-1].isdigit():
            groups.append(s[-3:])
            s = s[:-3]
        return s + ','.join(reversed(groups))

    y_format = tkr.FuncFormatter(func)
    ax.yaxis.set_major_formatter(y_format)

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

    if not os.path.isdir("./output_data/"):
        os.makedirs("./output_data/")

    #plt.title(date)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('./output_data/commTargetingAsesNotInRs' + '_' + str(date) + '_' + '_'.join(ixps) +  '_' + ipv + '.pdf')





def main():

    if len(sys.argv) != 5:
        print("""\
        This script will process all the IXP BGP communities seen at IXPs and 
        it will output pre-processed info about action BGP communities

        Usage: process_asesNotMembersMoreTargetted.py  preprocessed_bgp_communities_data_dir/ dateOrSnap v4OrV6 plotData

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
    ASesInRS = readASesInRS()

    communityNumbersDictWithMatch = {}

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
            if v4Orv6 in rs:

                ixpMembership = []

                if 'snap' in date:
                    dateIXP = snapshotDates[v4Orv6][date][ixp]
                else:
                    dateIXP = date

                if dateIXP in actionCommunitiesData[ixp][rs].keys():
                    
                    ixpMembership = list(ASesInRS[v4Orv6][ixp][dateIXP])
                    #print(ixp, rs, v4Orv6, dateIXP, len(ixpMembership))

                    communityNumbersDictWithMatch[ixp] = {}
                    asSumWithMatch = {}

                    for comm in list(actionCommunitiesData[ixp][rs][dateIXP].keys()):
                        if comm != "communitiesPerASNsUsage" and comm not in communitiesToAvoid[ixp] and 'rt' not in comm and 'ro' not in comm and comm.count(':') == 1:
                            for type in ['avoid', 'allow', 'prepend']:
                                match = re.search(ixpRegex[type][ixp], comm)
                                if match:
                                    asnList = [q for q in match.groups() if q]
                                    if len(asnList) > 0:
                                        asn = asnList[0]
                                        
                                        if asn not in ixpMembership and asn not in asesToAvoid[ixp]:
                                            if (match.string, asn) not in asSumWithMatch.keys():
                                                asSumWithMatch[(match.string, asn)] = actionCommunitiesData[ixp][rs][dateIXP][comm]
                                            else:
                                                asSumWithMatch[(match.string, asn)] += actionCommunitiesData[ixp][rs][dateIXP][comm]
                                
                                    break
                    
                    for asn in asSumWithMatch.keys():
                        communityNumbersDictWithMatch[ixp][asn] = asSumWithMatch[asn]

                else:
                    communityNumbersDictWithMatch[ixp] = {-1:0}

                if not communityNumbersDictWithMatch[ixp]:
                    communityNumbersDictWithMatch[ixp] = {-1:0}
                


    markers = {}
    commPerAsType = {}
    data = {}
    X = {}
    sum = {}


    for ixpDict in communityNumbersDictWithMatch.keys():
        X[ixpDict] = []
        sum[ixpDict] = 0
        markers[ixpDict] = []
        data[ixpDict] = []

        for k in dict(sorted(communityNumbersDictWithMatch[ixpDict].items(), key=lambda item: item[1], reverse=True)):

            if k != -1:
                sum[ixpDict] += communityNumbersDictWithMatch[ixpDict][k]

                for reg in keysIXPs[ixpDict]:
                    reg = re.compile(reg)
                    match = re.search(reg, k[0])

                    if match:
                        if match.group():
                            group = match.group().split(':')[-1]
                            tempX = communitiesMeaningRegexIXPs[ixpDict][reg].replace("AS", group)

                        else:
                            tempX = communitiesMeaningRegexIXPs[ixpDict][reg]
                                
                        if group in asInfo.keys():
                            tempX += ' (' + str(asInfo[group]) + ')'
                            #print(k, group)
                            if asInfo[group] not in commPerAsType.keys():
                                commPerAsType[asInfo[group]] = communityNumbersDictWithMatch[ixpDict][k]
                            else:
                                commPerAsType[asInfo[group]] += communityNumbersDictWithMatch[ixpDict][k]
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
                data[ixpDict].append(communityNumbersDictWithMatch[ixpDict][k])

            else:
                data[ixpDict] = [0] * 101
                markers[ixpDict] = ['2'] * 101
                sum[ixpDict] = 0 


    if not os.path.isdir("./output_data/"):
        os.makedirs("./output_data/")
        

    with open(os.path.join('output_data', v4Orv6 + '_' + date + '.txt'), 'w') as f:
        for ixp in ['ixbr', 'decix', 'linx', 'amsix', 'decixmad', 'decixnyc', 'bcix', 'netnodstocb']:
            tempX = [str(q) for q in X[ixp]]
            tempData = [str(q) for q in data[ixp]]

            f.write(ixp + '|' + ','.join(tempX) + '|' + ','.join(tempData) + '|' + str(sum[ixp]) +'\n')


    if plotData == 'y':
        plot(data, markers, sum, v4Orv6, ['ixbr', 'decix', 'linx', 'amsix'], date)
        plot(data, markers, sum, v4Orv6, ['decixmad', 'decixnyc', 'bcix', 'netnodstocb'], date)


if __name__ == '__main__':
    main()
