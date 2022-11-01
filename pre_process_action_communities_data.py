import json, re, sys, os
from tqdm import tqdm
sys.path.append('../')
from tools.constants import communitiesToAvoid

def main():

    global actionCommunitiesDataWithPerASN

    global communitiesMeaningIXPs
    global communitiesMeaningRegexIXPs
    global keysIXPs 

    

    if len(sys.argv) != 3:
        print("""\
        This script will process all the IXP BGP communities seen at IXPs and 
        it will output pre-processed info about action BGP communities

        Usage:  pre_process_action_communities_data.py ixp preprocessed_bgp_communities_data/
        """)
        sys.exit(0)

    ixpInput = sys.argv[1]
    path = sys.argv[2]

    if ixpInput not in ['ixbr', 'amsix', 'linx', 'decix', 'all', 'ixbrrj', 'ixbrce', 'decixmad', 'decixnyc', 'bcix', 'netnodstocg', 'netnodstocb']:
        print("Argument error: IXPs not among the accepted ones:")
        print("all, linx, decix, amsix, ixbr, ixbrrj, ixbrce, decixmad, decixnyc, bcix, netnodstocg or netnodstocb.")
        sys.exit()

    actionCommunitiesData = {
        'ixbr': {},
        'decix': {},
        'linx': {},
        'amsix': {},
        'decixmad': {},
        'decixnyc': {},
        'bcix': {},
        'netnodstocb': {},
    }

    actionCommunitiesDataWithPerASN = {
        'ixbr': {},
        'decix': {},
        'linx': {},
        'amsix': {},
        'decixmad': {},
        'decixnyc': {},
        'bcix': {},
        'netnodstocb': {},
    }

    #communitiesMeaningIXPs = {}
    #communitiesMeaningRegexIXPs = {}
    #keysIXPs = {}

    ixpCommunitiesData = {}
    
    if ixpInput == 'all':
        ixpList = ['ixbr', 'decix', 'linx', 'amsix', 'decixmad', 'decixnyc', 'bcix', 'netnodstocb']
    else:
        ixpList = [ixpInput]

    for ixp in tqdm(ixpList):
        ixpCommunitiesFile = os.path.join(path, 'ixpCommunitiesSeenAt' + ixp + '.json')

        ixpCommunitiesData[ixp] = {}
        #communitiesMeaningIXPs[ixp] = {}
        #communitiesMeaningRegexIXPs[ixp] = {}
        #keysIXPs[ixp] = []

        with open('tools/communitiesDictionaries/' + ixp + 'ParsedCommunitiesAction.txt') as f:
            d = f.readlines()
            d = [i.strip() for i in d]
            

        with open(ixpCommunitiesFile) as f:
            ixpCommunitiesData[ixp] = json.load(f)


        severalRegex = []
        with open('tools/communitiesDictionaries/' + ixp + 'ParsedCommunitiesAction.txt') as f:
            d = f.readlines()

        d = [i.replace('*', '\d+').strip() for i in d]
        for i in d:
            severalRegex.append('^' + i.split("|")[0] + '$')

            newI = i.replace('AS$1', 'AS')
            newI = newI.replace('AS$2', 'AS')
            line = newI.split("|")
            #communitiesMeaningIXPs[ixp]['^' + line[0] + '$'] = line[1]
            #communitiesMeaningRegexIXPs[ixp][re.compile('^' + line[0] + '$')] = line[1]

        #keysIXPs[ixp]=list(communitiesMeaningIXPs[ixp].keys())
        #keysIXPs[ixp].sort(key=lambda s:'(\\d+)' in s)

        actionCommunitiesRegex = re.compile("|".join(severalRegex))

        for rs in ixpCommunitiesData[ixp].keys():
            if rs not in actionCommunitiesData[ixp].keys():
                actionCommunitiesData[ixp][rs] = {}

            if rs not in actionCommunitiesDataWithPerASN[ixp].keys():
                actionCommunitiesDataWithPerASN[ixp][rs] = {}

            for date in ixpCommunitiesData[ixp][rs].keys():
                if date not in actionCommunitiesData[ixp][rs].keys():
                    actionCommunitiesData[ixp][rs][date] = {}

                if date not in actionCommunitiesDataWithPerASN[ixp][rs].keys():
                    actionCommunitiesDataWithPerASN[ixp][rs][date] = {}

                for comm in ixpCommunitiesData[ixp][rs][date].keys():
                    if re.match(actionCommunitiesRegex, comm) and re.match(actionCommunitiesRegex, comm).string not in communitiesToAvoid[ixp] \
                        and 'rt' not in re.match(actionCommunitiesRegex, comm).string and 'ro' not in re.match(actionCommunitiesRegex, comm).string \
                        and re.match(actionCommunitiesRegex, comm).string.count(':') == 1:

                            actionCommunitiesData[ixp][rs][date][comm] = ixpCommunitiesData[ixp][rs][date][comm]  

                    if comm == 'communitiesPerASNsUsage':
                        actionCommunitiesDataWithPerASN[ixp][rs][date]['communitiesPerASNsUsage'] = {}
                        for asn in ixpCommunitiesData[ixp][rs][date][comm]:                                
                            for asnComm in ixpCommunitiesData[ixp][rs][date][comm][asn]:
                                if re.match(actionCommunitiesRegex, asnComm) and re.match(actionCommunitiesRegex, asnComm).string not in communitiesToAvoid[ixp] \
                                    and 'rt' not in re.match(actionCommunitiesRegex, asnComm).string and 'ro' not in re.match(actionCommunitiesRegex, asnComm).string \
                                        and re.match(actionCommunitiesRegex, asnComm).string.count(':') == 1:

                                        if asn not in actionCommunitiesDataWithPerASN[ixp][rs][date]['communitiesPerASNsUsage'].keys():
                                            actionCommunitiesDataWithPerASN[ixp][rs][date]['communitiesPerASNsUsage'][asn] = {}

                                        actionCommunitiesDataWithPerASN[ixp][rs][date]['communitiesPerASNsUsage'][asn][asnComm] = ixpCommunitiesData[ixp][rs][date]['communitiesPerASNsUsage'][asn][asnComm]

                for asnAction in actionCommunitiesDataWithPerASN[ixp][rs][date]['communitiesPerASNsUsage'].keys():
                    actionCommunitiesDataWithPerASN[ixp][rs][date]['communitiesPerASNsUsage'][asnAction]['announcedPrefixes'] = ixpCommunitiesData[ixp][rs][date]['communitiesPerASNsUsage'][asnAction]['announcedPrefixes']



    if ixpInput == 'all':
        with open(os.path.join(path, 'actionCommunitiesSeenAt' + ixpInput + '.json'), 'w') as f:
            json.dump(actionCommunitiesData, f)

        with open(os.path.join(path, 'actionCommunitiesDataWithPerASN' + ixpInput + '.json'), 'w') as f:
            json.dump(actionCommunitiesDataWithPerASN, f)

    else:
        with open(os.path.join(path, 'actionCommunitiesSeenAt' + ixpInput + '.json'), 'w') as f:
            json.dump(actionCommunitiesData[ixpInput], f)

        with open(os.path.join(path, 'actionCommunitiesDataWithPerASN' + ixpInput + '.json'), 'w') as f:
            json.dump(actionCommunitiesDataWithPerASN[ixpInput], f)



if __name__ == '__main__':
    main()
