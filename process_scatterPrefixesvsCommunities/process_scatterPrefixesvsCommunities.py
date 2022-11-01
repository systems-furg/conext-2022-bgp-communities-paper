from collections import defaultdict
import json, sys, os
import matplotlib.pyplot as plt
from tqdm import tqdm
sys.path.append('../')
from tools.constants import asesToAvoid, communitiesToAvoid, ixpRegex, ixpNameMapping,snapshotDates
from tools.help_functions import human_format, readASesInRS, readASInfo

def plot(X, Y, v4OrV6, ixps, date):
    fig = plt.figure(figsize=(9/2.54, 6.75/2.54))
    ax = plt.subplot(111)


    xIXPs = [X[ixp] for ixp in ixps]
    yIXPs = [Y[ixp] for ixp in ixps]

    colors = ['#481567FF', '#2D708EFF','#3CBB75FF','#FDE725FF']

    for count, value in enumerate(ixps):
        plt.scatter(xIXPs[count], yIXPs[count], color = colors[count],label=ixpNameMapping[value], s=2)
    
    plt.ylabel('Fraction of prefixes announced at IXPs', fontsize='6.5')
    plt.xlabel('Fraction of BGP communities used at IXPs routes', fontsize='6.5')

    plt.tick_params(axis='x', labelsize='7')#, rotation=45)
    plt.tick_params(axis='y', labelsize='7')

    plt.yscale('log')
    plt.xscale('log')
    #plt.title(date)

    plt.rcParams["figure.autolayout"] = True

    plt.legend(ncol=4, loc='upper center', bbox_to_anchor=(0.5, 1.11), fontsize=5.3)

    plt.grid(alpha=0.2)
    
    if not os.path.isdir("./output_data/"):
        os.makedirs("./output_data/")

    plt.tight_layout()
    plt.savefig('./output_data/scatterPrefixesvsCommunities' + '_' + str(date) + '_' + '_'.join(ixps) +  '_' + v4OrV6 + '.pdf')


def main():

    if len(sys.argv) != 5:
        print("""\
        This script will process all the IXP BGP communities seen at IXPs and 
        it will output pre-processed info about action BGP communities

        Usage:  process_scatterPrefixesvsCommunities.py  preprocessed_bgp_communities_data_dir/ dateOrSnap v4OrV6 plotData

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

    actionCommunitiesFileWithPerASN = os.path.join(path, 'actionCommunitiesDataWithPerASNall.json')
    with open(actionCommunitiesFileWithPerASN) as f:
        actionCommunitiesDataWithPerASN = json.load(f)

    X = {}
    Y = {}

    print(date)
    for ixp in tqdm(['ixbr', 'decix', 'linx', 'amsix', 'decixmad', 'decixnyc', 'bcix', 'netnodstocb']):
        X[ixp] = []
        Y[ixp] = []

        for rs in actionCommunitiesDataWithPerASN[ixp].keys():
            communityNumbersDict = defaultdict(list)

            commToPrefixTuple = {}
            sumPrefixes = 0

            if v4Orv6 in rs:

                if 'snap' in date:
                    dateIXP = snapshotDates[v4Orv6][date][ixp]
                else:
                    dateIXP = date

                if dateIXP in actionCommunitiesDataWithPerASN[ixp][rs].keys():

                    
                    #dict with AS targeting non member as key and number of communities applied to them as value
                    actionCommPerAS = {}
                    
                    for asn in list(actionCommunitiesDataWithPerASN[ixp][rs][dateIXP]['communitiesPerASNsUsage'].keys()):
                        asnPrefixes = 0
                        for comm in actionCommunitiesDataWithPerASN[ixp][rs][dateIXP]['communitiesPerASNsUsage'][asn]:
                            if comm != 'announcedPrefixes' and comm not in communitiesToAvoid[ixp] and 'rt' not in comm and 'ro' not in comm and comm.count(':') == 1:
                                if asn not in actionCommPerAS.keys():
                                    actionCommPerAS[asn] = actionCommunitiesDataWithPerASN[ixp][rs][dateIXP]['communitiesPerASNsUsage'][asn][comm]
                                else:
                                    actionCommPerAS[asn] += actionCommunitiesDataWithPerASN[ixp][rs][dateIXP]['communitiesPerASNsUsage'][asn][comm]

                            elif comm == 'announcedPrefixes':
                                asnPrefixes = actionCommunitiesDataWithPerASN[ixp][rs][dateIXP]['communitiesPerASNsUsage'][asn][comm]
                                sumPrefixes += actionCommunitiesDataWithPerASN[ixp][rs][dateIXP]['communitiesPerASNsUsage'][asn][comm]

                        commToPrefixTuple[asn] = (actionCommPerAS[asn], asnPrefixes)

                    for asn in actionCommPerAS.keys():
                        communityNumbersDict[asn] = actionCommPerAS[asn]

                    percCommToPrefixTupleList = []
                    sumComm = 0

                    for k in communityNumbersDict.keys():
                        sumComm += communityNumbersDict[k]

                    for i in commToPrefixTuple.values():
                        percCommToPrefixTupleList.append( (i[0]/sumComm, i[1]/sumPrefixes) )
                    
                    X[ixp] = [r[0] for r in percCommToPrefixTupleList]
                    Y[ixp] = [r[1] for r in percCommToPrefixTupleList]

                else:
                    X[ixp] = []
                    Y[ixp] = []
    
    if not os.path.isdir("./output_data/"):
        os.makedirs("./output_data/")

    with open(os.path.join('output_data', v4Orv6 + '_' + date + '.txt'), 'w') as f:
        for ixp in ['ixbr', 'decix', 'linx', 'amsix', 'decixmad', 'decixnyc', 'bcix', 'netnodstocb']:
            tempX = [str(q) for q in X[ixp]]
            tempY = [str(q) for q in Y[ixp]]

            f.write(ixp + '|' + ','.join(tempX) + '|' + ','.join(tempY) + '\n')


    if plotData == 'y':
        plot(X, Y, v4Orv6, ['ixbr', 'decix', 'linx', 'amsix'], date)
        plot(X, Y, v4Orv6, ['decixmad', 'decixnyc', 'bcix', 'netnodstocb'], date)


if __name__ == '__main__':
    main()