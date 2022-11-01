from collections import defaultdict
import json, sys, os, re
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

sys.path.append('../')
from tools.constants import asesToAvoid, communitiesToAvoid, ixpRegex, ixpNameMapping,snapshotDates
from tools.help_functions import human_format, readASesInRS, readASInfo

def main():
    if len(sys.argv) != 3:
        print("""\
        This script will process all the IXP BGP communities seen at IXPs and 
        it will output pre-processed info about action BGP communities

        Usage:  process_communityPerType.py  preprocessed_bgp_communities_data_dir/ dateOrSnap plotData

        preprocessed_bgp_communities_data_dir - dir with preprocessed data for bgp communities
        dateOrSnap - input date in YYYY-MM-DD format or desired snapshot (snap1, snap2, ..., snap12)
        """)
        sys.exit(0)

    path = sys.argv[1]
    date = sys.argv[2]

    actionCommunitiesDataWithPerASN = {}
    actionCommunitiesData = {}

    actionCommunitiesFile = os.path.join(path, 'actionCommunitiesSeenAtall.json')
    with open(actionCommunitiesFile) as f:
        actionCommunitiesData = json.load(f)

    actionCommunitiesFile = os.path.join(path, 'actionCommunitiesDataWithPerASNall.json')
    with open(actionCommunitiesFile) as f:
        actionCommunitiesDataWithPerASN = json.load(f)

    communityNumbersDictV4 = {}
    communityNumbersDictV6 = {}

    print(date)
    for ixp in tqdm(['ixbr', 'decix', 'linx', 'amsix', 'decixmad', 'decixnyc', 'bcix', 'netnodstocb']):

        communityNumbersDictV4[ixp] = {}
        communityNumbersDictV6[ixp] = {}

        for rs in actionCommunitiesDataWithPerASN[ixp].keys():

            if 'v4' in rs:
                ipv = 'v4'
            elif 'v6' in rs:
                ipv = 'v6'

            if 'snap' in date:
                dateIXP = snapshotDates[ipv][date][ixp]
            else:
                dateIXP = date

            #print(dateIXP)
            if dateIXP in actionCommunitiesDataWithPerASN[ixp][rs].keys():
                commSum = {
                    'allow': set(),
                    'avoid': set(),
                    'prepend': set(),
                    'blackhole': set(),
                }

                for asn in list(actionCommunitiesDataWithPerASN[ixp][rs][dateIXP]['communitiesPerASNsUsage'].keys()):
                    for comm in actionCommunitiesDataWithPerASN[ixp][rs][dateIXP]['communitiesPerASNsUsage'][asn]:
                        if comm != 'announcedPrefixes' and comm not in communitiesToAvoid[ixp] and comm in actionCommunitiesData[ixp][rs][dateIXP].keys() \
                            and 'rt' not in comm and 'ro' not in comm and comm.count(':') == 1:
                            
                            found = False
                            #for type in ['avoidPlusAll', 'allowPlusAll', 'prepend', 'blackhole']:
                            for type in ['avoid', 'allow', 'prepend', 'blackhole']:
                                match = re.search(ixpRegex[type][ixp], comm)
                                
                                #if match:
                                #   print(asn, match, type)

                                if match and type == 'avoid':
                                    commSum['avoid'].add(asn)
                                    found = True
                                    break
                                elif match and type == 'allow':
                                    commSum['allow'].add(asn)
                                    found = True
                                    break
                                elif match and type == 'prepend':
                                    commSum['prepend'].add(asn)
                                    found = True
                                    break
                                elif match and type == 'blackhole':
                                    commSum['blackhole'].add(asn)
                                    found = True
                                    break
                        
                            #if not found:
                            #    print(comm, 'NOT FOUND') 
                
                if 'v4' in rs:
                    for comm in commSum.keys():
                        communityNumbersDictV4[ixp][comm] = len(commSum[comm])
                elif 'v6' in rs:
                    for comm in commSum.keys():
                        communityNumbersDictV6[ixp][comm] = len(commSum[comm])

    print(communityNumbersDictV4)
    print('\n')
    print(communityNumbersDictV6)

    if not os.path.isdir("./output_data/"):
        os.makedirs("./output_data/")

    with open(os.path.join('output_data', date + '.txt'), 'w') as f:
        f.write(ixp + '|avoid_v4|allow_v4|prepend_v4|blackhole_v4|avoid_v6|allow_v6|prepend_v6|blackhole_v6\n')
        for ixp in ['ixbr', 'decix', 'linx', 'amsix', 'decixmad', 'decixnyc', 'bcix', 'netnodstocb']:
            f.write(ixp + '|' + str(communityNumbersDictV4[ixp]['avoid']) + '|' + str(communityNumbersDictV6[ixp]['avoid']) \
                + '|' + str(communityNumbersDictV4[ixp]['allow']) + '|' + str(communityNumbersDictV6[ixp]['allow']) \
                + '|' + str(communityNumbersDictV4[ixp]['prepend']) + '|' + str(communityNumbersDictV6[ixp]['prepend']) \
                + '|' + str(communityNumbersDictV4[ixp]['blackhole']) + '|' + str(communityNumbersDictV6[ixp]['blackhole']) + '\n')



if __name__ == '__main__':
    main()