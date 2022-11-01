import json, sys, os
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.ticker import ScalarFormatter
sys.path.append('../')
from tools.constants import asesToAvoid, communitiesToAvoid, ixpRegex, ixpNameMapping, snapshotDates
from tools.help_functions import human_format, readASesInRS, readASInfo

def generateCDF(latencyDifferenceList, logScale, ccdf, sum, ipv, ixps, date):

    #fig = plt.figure()
    fig = plt.figure(figsize=(8/2.54, 6.75/2.54))
    ax1 = fig.add_subplot(111)

    dashStyle = [(0, ()), (0, (1, 1)), '--',  '-.', (0, (1, 10)), (0, (5, 10)), (0, (3, 5, 1, 5, 1, 5)), (0, (3, 1, 1, 1, 1, 1)), (0, (3, 10, 1, 10, 1, 10))]
    dashCount = 0

    color = ['#481567FF', '#2D708EFF', '#3CBB75FF', '#FDE725FF']
    colorCount = 0

    latencyDifferenceListIXPs = [latencyDifferenceList[ixp] for ixp in ixps]

    for i in tqdm(latencyDifferenceListIXPs):
        if len(i) != 0:
            hopDistance = i

            hopDistance = list(filter(lambda a: a != '-', hopDistance))
            hopDistance = [float(a) for a in hopDistance]

            ser = pd.Series(hopDistance)
            ser = ser.sort_values()
            #print(ser)
            ser[len(ser)] = ser.iloc[-1]
            cum_dist = np.linspace(0.,1.,len(ser))

            if ccdf:
                cum_dist = 1 - cum_dist

            ser_cdf = pd.Series(cum_dist, index=ser)
            #print(ser_cdf.to_string())
            #print("\n\n")
            #if colorCount == 0:
            #    print(ser_cdf.to_string())

            if logScale:
                ser_cdf.plot(drawstyle='default', logx=True, ls=dashStyle[dashCount], color=color[colorCount])
            else:
                ser_cdf.plot(drawstyle='default', logx=False, ls=dashStyle[dashCount], color=color[colorCount])

            dashCount+=1
            colorCount+=1

    axes = plt.gca()
    #axes.xaxis.set_minor_formatter(mticker.ScalarFormatter())
    for axis in [axes.xaxis, axes.yaxis]:
        formatter = ScalarFormatter()
        formatter.set_scientific(False)
        axis.set_major_formatter(formatter)
    
    plt.ylabel('Fraction of BGP communities at IXP routes',fontsize=6.5)
    plt.xlabel('Fraction of ASes at RS', fontsize=6.5)
    
    plt.ylim([0,1])
    
    #plt.ticklabel_format(style='plain', useOffset=False, axis='x')
    plt.xticks(fontsize=6, rotation = 0)
    plt.yticks(fontsize=6)
    plt.grid(True)
    
    plt.legend([ixpNameMapping[ixps[0]] + " - " + human_format(sum[ixps[0]]), ixpNameMapping[ixps[1]] + " - " + human_format(sum[ixps[1]]), \
        ixpNameMapping[ixps[2]] + " - " + human_format(sum[ixps[2]]), ixpNameMapping[ixps[3]] + " - " + human_format(sum[ixps[3]])], loc='lower right', fontsize=5)

    if not os.path.isdir("./output_data/"):
        os.makedirs("./output_data/")

    plt.tight_layout()
    plt.savefig('./output_data/asesApplyingMoreActionCommunitiesBar_' + ipv + '_' + str(date) + '_' + '_'.join(ixps) + '.pdf')
    #plt.show()


def main():

    if len(sys.argv) != 5:
        print("""\
        This script will process all the IXP BGP communities seen at IXPs and 
        it will output pre-processed info about action BGP communities

        Usage:  process_aSesApplyingMoreActionCommunities.py  preprocessed_bgp_communities_data_dir/ dateOrSnap v4OrV6 plotData

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

    data = {}
    dataCDF = {}
    sumCDF = {}

    X = []

    print(date)
    for ixp in tqdm(['ixbr', 'decix', 'linx', 'amsix', 'decixmad', 'decixnyc', 'bcix', 'netnodstocb']):

        data[ixp] = []
        dataCDF[ixp] = []
        sumCDF[ixp] = 0
        
        for rs in actionCommunitiesDataWithPerASN[ixp].keys():

            communitiesUsagePerAS = {}
            if v4Orv6 in rs:

                if 'snap' in date:
                    dateIXP = snapshotDates[v4Orv6][date][ixp]
                else:
                    dateIXP = date

                #print(ixp, dateIXP)

                if dateIXP in actionCommunitiesDataWithPerASN[ixp][rs].keys():
                    
                    for asn in list(actionCommunitiesDataWithPerASN[ixp][rs][dateIXP]['communitiesPerASNsUsage'].keys()):
                        for comm in actionCommunitiesDataWithPerASN[ixp][rs][dateIXP]['communitiesPerASNsUsage'][asn]:
                            if comm != 'announcedPrefixes' and comm not in communitiesToAvoid[ixp] and 'rt' not in comm and 'ro' not in comm and comm.count(':') == 1:
                                
                                if asn not in communitiesUsagePerAS.keys():
                                    communitiesUsagePerAS[asn] = actionCommunitiesDataWithPerASN[ixp][rs][dateIXP]['communitiesPerASNsUsage'][asn][comm]
                                else:
                                    communitiesUsagePerAS[asn] += actionCommunitiesDataWithPerASN[ixp][rs][dateIXP]['communitiesPerASNsUsage'][asn][comm]
                
                asnCount = 1


                for k in dict(sorted(communitiesUsagePerAS.items(), key=lambda item: item[1], reverse=True)):

                    #print(ixp, k, communitiesUsagePerAS[k], sumCDF[ixp])

                    X.append(k)
                    data[ixp].append(communitiesUsagePerAS[k])

                    #tempData = [asnCount/(len(communitiesUsagePerAS.keys()))] * communitiesUsagePerAS[k]
                    tempData = [asnCount/(len(communitiesUsagePerAS.keys()))] * communitiesUsagePerAS[k]

                    #print(k, tempData)
                    
                    dataCDF[ixp].extend(tempData)
                    sumCDF[ixp] += communitiesUsagePerAS[k]

                    asnCount += 1
                
                if dateIXP not in actionCommunitiesDataWithPerASN[ixp][rs].keys():
                    data[ixp].append(0)
                    dataCDF[ixp] = [0]
                    sumCDF[ixp] = 0

    if not os.path.isdir("./output_data/"):
        os.makedirs("./output_data/")

    #with open(os.path.join('output_data', date + '.txt'), 'w') as f:
    #    for ixp in ['ixbr', 'decix', 'linx', 'amsix', 'decixmad', 'decixnyc', 'bcix', 'netnodstocb']:
    #        data[ixp] = [str(q) for q in data[ixp]]
    #        dataCDF[ixp] = [str(q) for q in dataCDF[ixp]]

    #        f.write(ixp + '|' + ','.join(data[ixp]) + '|' + ','.join(dataCDF[ixp]) + '|' + str(sumCDF[ixp]) + '\n')

    if plotData == 'y':
        generateCDF(dataCDF, True, False, sumCDF, v4Orv6, ['ixbr', 'decix', 'linx', 'amsix'], date)
        generateCDF(dataCDF, True, False, sumCDF, v4Orv6, ['decixmad', 'decixnyc', 'bcix', 'netnodstocb'], date)



if __name__ == '__main__':
    main()