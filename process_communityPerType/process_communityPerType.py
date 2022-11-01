from collections import defaultdict
import json, sys, os
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

sys.path.append('../')
from tools.constants import asesToAvoid, communitiesToAvoid, ixpRegex, ixpNameMapping, snapshotDates
from tools.help_functions import human_format, readASesInRS, readASInfo


def plot(stackedDataV4, stackedDataV6, totalV4, totalV6, ixps, date):

    X = np.arange(len(ixps))
    fig = plt.figure(figsize=(9/2.54, 5/2.54))
    ax = plt.subplot(111)

    YToPlotv40 = [stackedDataV4[ixp][0] for ixp in ixps]
    YToPlotv41 = [stackedDataV4[ixp][1] for ixp in ixps]
    YToPlotv42 = [stackedDataV4[ixp][2] for ixp in ixps]

    YToPlotv60 = [stackedDataV6[ixp][0] for ixp in ixps]
    YToPlotv61 = [stackedDataV6[ixp][1] for ixp in ixps]
    YToPlotv62 = [stackedDataV6[ixp][2] for ixp in ixps]

    totalV4IXPs = [totalV4[i] for i in totalV4.keys() if i in ixps]
    totalV6IXPs = [totalV6[i] for i in totalV6.keys() if i in ixps]

    plt.bar(X-0.2, YToPlotv40, color = '#481567FF', width = 0.35)
    plt.bar(X-0.2, YToPlotv41, color = '#2D708EFF', width = 0.35, bottom=YToPlotv40)
    plt.bar(X-0.2, YToPlotv42, color = '#3CBB75FF', width = 0.35, bottom=[i + j for i,j in zip(YToPlotv40, YToPlotv41)])

    plt.bar(X+0.2, YToPlotv60, color = '#481567FF', width = 0.35)
    plt.bar(X+0.2, YToPlotv61, color = '#2D708EFF', width = 0.35, bottom=YToPlotv60)
    plt.bar(X+0.2, YToPlotv62, color = '#3CBB75FF', width = 0.35, bottom=[i + j for i,j in zip(YToPlotv60, YToPlotv61)])

    ixpsNames = [ixpNameMapping[i] for i in ixps]
    plt.ylabel('% of communities', fontsize='6')
    plt.xticks(X, ixpsNames)
    plt.tick_params(axis='x', pad=7, labelsize='6')
    plt.tick_params(axis='y', labelsize='6')
    #plt.tick_params(axis="x",which="minor", color="r")

    plt.ylim([0,1.07])
    plt.ticklabel_format(style='plain', axis='y')
    #ax.set_yticks(np.arange(0, 81, 10))
    plt.legend(labels=['Extended', 'Large', 'Standard'], ncol=3, loc='upper center', bbox_to_anchor=(0.5, 1.16), fontsize=5)

    plt.text(-0.33, -0.09, 'IPv4', color='black', fontsize='6')
    plt.text(0.07, -0.09, 'IPv6', color='black', fontsize='6')
    plt.text(0.68, -0.09, 'IPv4', color='black', fontsize='6')
    plt.text(1.07, -0.09, 'IPv6', color='black', fontsize='6')
    plt.text(1.68, -0.09, 'IPv4', color='black', fontsize='6')
    plt.text(2.07, -0.09, 'IPv6', color='black', fontsize='6')
    plt.text(2.68, -0.09, 'IPv4', color='black', fontsize='6')
    plt.text(3.07, -0.09, 'IPv6', color='black', fontsize='6')

    shift = -0.32
    for ixp in ixps:
        plt.text(shift, 1.015, human_format(round(totalV4[ixp], 2)), color='black', fontsize='4.4')
        shift += 1.0

    shift = 0.07
    for ixp in ixps:
        plt.text(shift, 1.015, human_format(round(totalV6[ixp], 2)), color='black', fontsize='4.4')
        shift += 1.0

    plt.text(-0.35, 0.94, str(round(YToPlotv42[0] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
    plt.text(-0.34, 0.02, str(round(YToPlotv40[0] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
    plt.text(0.65, 0.94, str(round(YToPlotv42[1] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
    plt.text(0.64, 0.02, str(round(YToPlotv41[1] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
    plt.text(1.65, 0.94, str(round(YToPlotv42[2] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
    plt.text(1.65, 0.02, str(round(YToPlotv41[2] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
    plt.text(2.65, 0.94, str(round(YToPlotv42[3] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')

    plt.text(0.06, 0.94, str(round(YToPlotv62[0] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
    plt.text(0.06, 0.02, str(round(YToPlotv60[0] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
    plt.text(1.05, 0.94, str(round(YToPlotv62[1] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
    plt.text(1.05, 0.02, str(round(YToPlotv61[1] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
    plt.text(2.05, 0.94, str(round(YToPlotv62[2] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
    plt.text(2.05, 0.02, str(round(YToPlotv61[2] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')
    plt.text(3.05, 0.94, str(round(YToPlotv62[3] * 100, 1)) + '%', color='white', fontsize='4.4', fontweight='bold')

    if not os.path.isdir("./output_data/"):
        os.makedirs("./output_data/")

    plt.tight_layout()
    plt.savefig('./output_data/commPerType' + '_' + str(date) + '_' + '_'.join(ixps) + '.pdf')


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

    ixpCommunitiesData = {}

    dataV4 = defaultdict(list)
    dataV6 = defaultdict(list)
    stackedDataV4 = defaultdict(list)
    stackedDataV6 = defaultdict(list)
    totalAllV4 = {}
    totalAllV6 = {}

    print(date)
    for ixp in tqdm(['ixbr', 'decix', 'linx', 'amsix', 'decixmad', 'decixnyc', 'bcix', 'netnodstocb']):
        ixpCommunitiesData[ixp] = {}

        dataV4[ixp] = []
        dataV6[ixp] = []
        stackedDataV4[ixp] = []
        stackedDataV6[ixp] = []
        totalAllV4[ixp] = 0
        totalAllV6[ixp] = 0

        ixpCommunitiesFile = os.path.join(path, 'ixpCommunitiesSeenAt' + ixp + '.json')

        with open(ixpCommunitiesFile) as f:
            ixpCommunitiesData[ixp] = json.load(f)
    
        for rs in ixpCommunitiesData[ixp].keys():
            communityNumbersDict = {'standard': 0,'large': 0,'extended': 0}

            if 'v4' in rs:
                ipv = 'v4'
            elif 'v6' in rs:
                ipv = 'v6'

            if 'snap' in date:
                dateIXP = snapshotDates[ipv][date][ixp]
            else:
                dateIXP = date

            if dateIXP in ixpCommunitiesData[ixp][rs].keys():
                for comm in ixpCommunitiesData[ixp][rs][dateIXP].keys():

                    if comm != "communitiesPerASNsUsage":

                        if 'rt' in comm or 'ro' in comm:
                            communityNumbersDict['extended'] += ixpCommunitiesData[ixp][rs][dateIXP][comm]
                        elif comm.count(':') == 2:
                            communityNumbersDict['large'] += ixpCommunitiesData[ixp][rs][dateIXP][comm]
                        else:
                            communityNumbersDict['standard'] += ixpCommunitiesData[ixp][rs][dateIXP][comm]

            if 'v4' in rs:
                dataV4[ixp].append(communityNumbersDict['extended'])
                dataV4[ixp].append(communityNumbersDict['large'])
                dataV4[ixp].append(communityNumbersDict['standard'])

                total = (communityNumbersDict['extended']+communityNumbersDict['large']+communityNumbersDict['standard'])
                totalAllV4[ixp] = total

                if total > 0:
                    stackedDataV4[ixp].append(communityNumbersDict['extended'] / total)
                    stackedDataV4[ixp].append(communityNumbersDict['large'] / total)
                    stackedDataV4[ixp].append(communityNumbersDict['standard'] / total)
                else:
                    stackedDataV4[ixp].append(0.0)
                    stackedDataV4[ixp].append(0.0)
                    stackedDataV4[ixp].append(0.0)

            elif 'v6' in rs:
                dataV6[ixp].append(communityNumbersDict['extended'])
                dataV6[ixp].append(communityNumbersDict['large'])
                dataV6[ixp].append(communityNumbersDict['standard'])

                total = (communityNumbersDict['extended']+communityNumbersDict['large']+communityNumbersDict['standard'])
                totalAllV6[ixp] = total

                if total > 0:
                    stackedDataV6[ixp].append(communityNumbersDict['extended'] / total)
                    stackedDataV6[ixp].append(communityNumbersDict['large'] / total)
                    stackedDataV6[ixp].append(communityNumbersDict['standard'] / total)
                else:
                    stackedDataV6[ixp].append(0.0)
                    stackedDataV6[ixp].append(0.0)
                    stackedDataV6[ixp].append(0.0)


    if not os.path.isdir("./output_data/"):
        os.makedirs("./output_data/")

    with open(os.path.join('output_data', date + '.txt'), 'w') as f:
        for ixp in ['ixbr', 'decix', 'linx', 'amsix', 'decixmad', 'decixnyc', 'bcix', 'netnodstocb']:
            f.write(ixp + '|' + str(dataV4[ixp][0]) + '|' + str(dataV4[ixp][1]) + '|' + str(dataV4[ixp][2]) + '|' + str(stackedDataV4[ixp][0]) + '|' + str(stackedDataV4[ixp][1]) + '|' + str(stackedDataV4[ixp][2]) \
                + '|' + str(dataV6[ixp][0]) + '|' + str(dataV6[ixp][1]) + '|' + str(dataV6[ixp][2]) + '|' + str(stackedDataV6[ixp][0]) + '|' + str(stackedDataV6[ixp][1]) + '|' + str(stackedDataV6[ixp][2]) \
                + '|' + str(totalAllV4[ixp]) + '|' + str(totalAllV6[ixp]) + '\n')

    if plotData == 'y':
        plot(stackedDataV4, stackedDataV6, totalAllV4, totalAllV6, ['ixbr', 'decix', 'linx', 'amsix'], date)
        plot(stackedDataV4, stackedDataV6, totalAllV4, totalAllV6, ['decixmad', 'decixnyc', 'bcix', 'netnodstocb'], date)


if __name__ == '__main__':
    main()



    

