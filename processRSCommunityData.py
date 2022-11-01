import json, re, sys, os
from os import listdir
from os.path import isfile, join, isdir
from collections import defaultdict
import io, gzip
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from cycler import cycler
from tqdm import tqdm

rsToConsider = {
    'v4': {
        'ixbr': 'SP-rs1-v4',
        'decix': 'rs1_fra_ipv4',
        'linx': 'rs1-in2-lon1-linx-net-v4',
        'amsix': 'nl-rc-v4',
        'ixbrrj': 'RJ-rs1-v4',
        'ixbrce': 'CE-rs1-v4',
        'decixmad': 'rs1_mad_ipv4',
        'decixnyc': 'rs1_nyc_ipv4',
        'bcix': 'rs01-bcix-v4',
        'netnodstocb': 'stoc_blue_mtu1500_v4',
        'netnodstocg': 'stoc_green_mtu1500_v4'
    },
    'v6':{
        'ixbr': 'SP-rs1-v6',
        'decix': 'rs1_fra_ipv6',
        'linx': 'rs1-in2-lon1-linx-net-v6',
        'amsix': 'nl-rc-v6',
        'ixbrrj': 'RJ-rs1-v6',
        'ixbrce': 'CE-rs1-v6',
        'decixmad': 'rs1_mad_ipv6',
        'decixnyc': 'rs1_nyc_ipv6',
        'bcix': 'rs01-bcix-v6',
        'netnodstocb': 'stoc_blue_mtu1500_v6',
        'netnodstocg': 'stoc_green_mtu1500_v6'
    }
}

ixpToRS = {
    'linx': 'lon1',
    'decix': 'fra',
    'amsix': 'nl',
    'ixbr': 'SP',
    'ixbrrj': 'RJ',
    'ixbrce': 'CE',
    'decixmad': 'mad',
    'decixnyc': 'nyc',
    'bcix': 'bcix',
    'netnodstocg':'stoc_green_mtu1500',
    'netnodstocb':'stoc_blue_mtu1500'
}

def pretty(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))


def readCommunitiesDict(ixp):

    communities = {}

    with open('tools/communitiesDictionaries/' + ixp + 'ParsedCommunities.txt') as f:
        d = f.readlines()

    d = [i.strip() for i in d]

    for i in d:
        line = i.split("|")
        communities[line[0]] = line[1]

    print(communities)

    return communities

def generateRegexCommunitiesDict(d):

    communities = {
        'comm': {},
        'largeComm': {},
        'extComm': {}
    }

    for i in d.keys():
        if 'rt' in i or 'ro' in i:
            communities['extComm'][i.replace('*', '\d+')] = {}
        elif i.count(':') == 2:
            communities['largeComm'][i.replace('*', '\d+')] = {}
        else:
            communities['comm'][i.replace('*', '\d+')] = {}

    return communities

def getAllDaysDir(path):
    return [f for f in listdir(path) if isdir(join(path, f)) and re.match(r'\d+\-\d+\-\d+', f) ]

def getAllFilesForDir(path, ixp):

    regexV4 = r".*" + re.escape(ixpToRS[ixp]) + ".*v4.*"
    regexV6 = r".*" + re.escape(ixpToRS[ixp]) + ".*v6.*"

    return [f for f in listdir(path) if isfile(join(path, f)) and re.match(regexV4, f)], \
        [f for f in listdir(path) if isfile(join(path, f)) and re.match(regexV6, f)]

def getRSFileFromDir(path):
    return [f for f in listdir(path) if isfile(join(path, f)) and re.match(r'.*routeServers.*', f)]

def processFiles(v4Orv6, files, day, path, regexCommunities, specificCommunityCountDict, allCommunityCountDict):

    global rsToConsider
    global ixp

    rsDict = {}

    for file in tqdm(sorted(files)):

        rsName = file.split("_received_")[0]
        rsShorterName = file.split("BGPFile")[0]
        rows = []

        if rsShorterName == rsToConsider[v4Orv6][ixp]:
            print(rsName, rsShorterName)
            
            #sys.exit(0)

            if rsName not in rsDict.keys():
                rsDict[rsName] = {}

            if rsName not in specificCommunityCountDict.keys():
                specificCommunityCountDict[rsName] = {}

            if day not in rsDict[rsName].keys():
                rsDict[rsName][day] = {}
                rsDict[rsName][day]['asns'] = {}
                rsDict[rsName][day]['prefixes'] = set()
                rsDict[rsName][day]['routes'] = set()
                rsDict[rsName][day]['uniqueComm'] = set()
                rsDict[rsName][day]['uniqueLargeComm'] = set()
                rsDict[rsName][day]['uniqueExtendedComm'] = set()
                rsDict[rsName][day]['allComm'] = []
                rsDict[rsName][day]['allLargeComm'] = []
                rsDict[rsName][day]['allExtendedComm'] = []

            if day not in specificCommunityCountDict[rsName].keys():
                specificCommunityCountDict[rsName][day] = {}
                specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'] = {}

            if rsName not in allCommunityCountDict.keys():
                allCommunityCountDict[rsName] = {}

            if day not in allCommunityCountDict[rsName].keys():
                allCommunityCountDict[rsName][day] = {}
                allCommunityCountDict[rsName][day]['communitiesPerASNsUsage'] = {}

            if file.split(".")[-1] == 'gz':
                try:
                    with gzip.open(path + "/" + day + "/" + file,'rb') as f:
                        file_content=f.readlines()
                    
                    for row in file_content:
                        rows.append(row.decode('utf8'))

                except:
                    print("Problem open gzip file")
                    continue
            else:
                try:
                    with open(path + "/" + day + "/" + file,'r') as f:
                        file_content=f.readlines()
                        
                        for row in file_content:
                            rows.append(row.decode('utf8'))
                except:
                    print("Problem open file")
                    continue

            for row in tqdm(rows):

                allFoundComm = []
                allFoundLargeComm = []
                allFoundExtComm = []

                prefix, gateway, ASPath, commList, largeCommList, extCommList, age, cached, neighbor = row.split("|")

                if (ixp == 'amsix' and neighbor.strip() == 'RS1v4') or (ixp == 'amsix' and neighbor.strip() == 'RS1v6') \
                    or ixp in ['ixbr', 'decix', 'linx', 'ixbrrj', 'ixbrce', 'decixmad', 'decixnyc', 'bcix', 'netnodstocg','netnodstocb']:

                    #print(rsName, day, prefix, commList)
                    asn = ASPath.split(" ")[0]

                    rsDict[rsName][day]['prefixes'].add(prefix)
                    rsDict[rsName][day]['routes'].add( (prefix, gateway, ASPath, neighbor) )

                    if asn not in rsDict[rsName][day].keys():
                        rsDict[rsName][day]['asns'][asn] = {}

                    if asn not in allCommunityCountDict[rsName][day]['communitiesPerASNsUsage'].keys():
                        allCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn] = {}
                        allCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn]['announcedPrefixes'] = set()

                    if asn not in specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'].keys():
                        specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn] = {}
                        specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn]['announcedPrefixes'] = set()

                    allCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn]['announcedPrefixes'].add(prefix)
                    specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn]['announcedPrefixes'].add(prefix)
                    

                    comm = commList.split(" ")
                    comm = [q for q in comm if q]
                    rsDict[rsName][day]['uniqueComm'].update(comm)
                    rsDict[rsName][day]['allComm'] += comm

                    for k in comm:
                        if k:
                            if k not in allCommunityCountDict[rsName][day].keys():
                                allCommunityCountDict[rsName][day][k] = 1
                            else:
                                allCommunityCountDict[rsName][day][k] += 1

                            if k.strip() not in allCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn].keys():
                                allCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn][k.strip()] = 1
                            else:
                                allCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn][k.strip()] += 1

                            tempFind = re.findall(regexCommunities['comm'], k)
                            tempFind = [q for q in tempFind if q]
                            if tempFind:
                                allFoundComm += tempFind

                    largeComm = largeCommList.split(" ")
                    largeComm = [q for q in largeComm if q]
                    rsDict[rsName][day]['uniqueLargeComm'].update(largeComm)
                    rsDict[rsName][day]['allLargeComm'] += largeComm

                    for k in largeComm:
                        if k:
                            if k not in allCommunityCountDict[rsName][day].keys():
                                allCommunityCountDict[rsName][day][k] = 1
                            else:
                                allCommunityCountDict[rsName][day][k] += 1

                            if k.strip() not in allCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn].keys():
                                allCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn][k.strip()] = 1
                            else:
                                allCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn][k.strip()] += 1

                            tempFind = re.findall(regexCommunities['largeComm'], k)
                            tempFind = [q for q in tempFind if q]
                            if tempFind:
                                allFoundLargeComm += tempFind

                    extComm = extCommList.split(" ")
                    extComm = [q for q in extComm if q]
                    rsDict[rsName][day]['uniqueExtendedComm'].update(extComm)
                    rsDict[rsName][day]['allExtendedComm'] += extComm

                    for k in extComm:
                        if k:
                            if k not in allCommunityCountDict[rsName][day].keys():
                                allCommunityCountDict[rsName][day][k] = 1
                            else:
                                allCommunityCountDict[rsName][day][k] += 1

                            if k.strip() not in allCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn].keys():
                                allCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn][k.strip()] = 1
                            else:
                                allCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn][k.strip()] += 1

                            tempFind = re.findall(regexCommunities['extComm'], k)
                            tempFind = [q for q in tempFind if q]
                            if tempFind:
                                allFoundExtComm += tempFind

                    for k in allFoundComm:
                        if k:
                            if k.strip() not in specificCommunityCountDict[rsName][day].keys():
                                specificCommunityCountDict[rsName][day][k.strip()] = 1
                            else:
                                specificCommunityCountDict[rsName][day][k.strip()] += 1

                            if k.strip() not in specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn].keys():
                                specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn][k.strip()] = 1
                            else:
                                specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn][k.strip()] += 1
                            

                    for k in allFoundLargeComm:
                        if k:
                            if k.strip() not in specificCommunityCountDict[rsName][day].keys():
                                specificCommunityCountDict[rsName][day][k.strip()] = 1
                            else:
                                specificCommunityCountDict[rsName][day][k.strip()] += 1

                            if k.strip() not in specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn].keys():
                                specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn][k.strip()] = 1
                            else:
                                specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn][k.strip()] += 1

                    for k in allFoundExtComm:
                        if k:
                            if k.strip() not in specificCommunityCountDict[rsName][day].keys():
                                specificCommunityCountDict[rsName][day][k.strip()] = 1
                            else:
                                specificCommunityCountDict[rsName][day][k.strip()] += 1

                            if k.strip() not in specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn].keys():
                                specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn][k.strip()] = 1
                            else:
                                specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn][k.strip()] += 1

            for asn in specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'].keys():
                specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn]['announcedPrefixes'] = len(specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn]['announcedPrefixes'])

            for asn in allCommunityCountDict[rsName][day]['communitiesPerASNsUsage'].keys():
                allCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn]['announcedPrefixes'] = len(allCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn]['announcedPrefixes'])

            rsDict[rsName][day]['asns'] = len(rsDict[rsName][day]['asns'].keys())  
            rsDict[rsName][day]['prefixes'] = len(rsDict[rsName][day]['prefixes'])  
            rsDict[rsName][day]['routes'] = len(rsDict[rsName][day]['routes'])  
            rsDict[rsName][day]['uniqueComm'] = len(rsDict[rsName][day]['uniqueComm'])  
            rsDict[rsName][day]['uniqueLargeComm'] = len(rsDict[rsName][day]['uniqueLargeComm'])  
            rsDict[rsName][day]['uniqueExtendedComm'] = len(rsDict[rsName][day]['uniqueExtendedComm'])  
            rsDict[rsName][day]['allComm'] = len(rsDict[rsName][day]['allComm'])  
            rsDict[rsName][day]['allLargeComm'] = len(rsDict[rsName][day]['allLargeComm'])  
            rsDict[rsName][day]['allExtendedComm'] = len(rsDict[rsName][day]['allExtendedComm']) 

            print(
                "\t\t", 
                rsDict[rsName][day]['asns'], 
                rsDict[rsName][day]['prefixes'], 
                rsDict[rsName][day]['routes'], 
                rsDict[rsName][day]['uniqueComm'], 
                rsDict[rsName][day]['uniqueLargeComm'], 
                rsDict[rsName][day]['uniqueExtendedComm'], 
                rsDict[rsName][day]['allComm'], 
                rsDict[rsName][day]['allLargeComm'], 
                rsDict[rsName][day]['allExtendedComm'], 
                "\n"
            )

            with open('infoPerDay_' + ixp + '.txt', 'a') as f:
                f.write(rsName + ',')
                f.write(day + ',')
                f.write(str(rsDict[rsName][day]['asns']) + ',' + \
                    str(rsDict[rsName][day]['prefixes']) + ',' + \
                    str(rsDict[rsName][day]['routes'])  + ',' + \
                    str(rsDict[rsName][day]['uniqueComm']) + ',' + \
                    str(rsDict[rsName][day]['uniqueLargeComm']) + ',' + \
                    str(rsDict[rsName][day]['uniqueExtendedComm']) + ',' + \
                    str(rsDict[rsName][day]['allComm']) + ',' + \
                    str(rsDict[rsName][day]['allLargeComm']) + ',' + \
                    str(rsDict[rsName][day]['allExtendedComm']) + '\n')


def main():

    global ixp
    global path

    ixp = sys.argv[1]
    path = sys.argv[2]

    if len(sys.argv) != 3:
        print("""\
        This script will process the IXP BGP files and it will
        output pre-processed info about seen BGP communities

        Usage:  processRSCommunityData.py ixp bgpFilesPathDir/
        """)
        sys.exit(0)

    if ixp not in ixpToRS.keys():
        print("Argument error: IXPs not among the accepted ones:")
        print("linx, decix, amsix, ixbr, ixbrrj, ixbrce, decixmad, decixnyc, bcix, netnodstocg or netnodstocb.")
        sys.exit()


    communities = readCommunitiesDict(ixp)
    regexCommunities = generateRegexCommunitiesDict(communities)

    finalRegex = {}

    replacedCommunities = []
    for i in regexCommunities['comm'].keys():
        replacedCommunities.append('^' + i + "\s|\s" + i + "\s|\s" + i + "$|^" + i + "$")

    finalRegex['comm'] = re.compile("|".join(replacedCommunities))

    replacedCommunities = []
    for i in regexCommunities['largeComm'].keys():
        replacedCommunities.append('^' + i + "\s|\s" + i + "\s|\s" + i + "$|^" + i + "$")

    finalRegex['largeComm'] = re.compile("|".join(replacedCommunities))

    replacedCommunities = []
    for i in regexCommunities['extComm'].keys():
        replacedCommunities.append('^' + i + "\s|\s" + i + "\s|\s" + i + "$|^" + i + "$")

    finalRegex['extComm'] = re.compile("|".join(replacedCommunities))

    specificCommunityCountDict = {}
    allCommunityCountDict = {}
    percentageCommPerPerAS = {}

    dateDir = getAllDaysDir(path)
    print(sorted(dateDir))

    #process v4 files
    for day in tqdm(sorted(dateDir)):
        print(day)
        v4Files, v6Files = getAllFilesForDir(path + "/" + day, ixp)

        if len(v4Files) > 0:
            processFiles('v4', v4Files, day, path, finalRegex, specificCommunityCountDict, allCommunityCountDict)

            rsName = [k.split("_received_")[0] for k in v4Files if k.split("BGPFile")[0] == rsToConsider['v4'][ixp]][0]

            if rsName not in percentageCommPerPerAS.keys():
                percentageCommPerPerAS[rsName] = {}
            
            if day not in percentageCommPerPerAS[rsName].keys():
                percentageCommPerPerAS[rsName][day] = {}

            for asn in specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'].keys():
                if asn not in percentageCommPerPerAS[rsName][day].keys():
                    percentageCommPerPerAS[rsName][day][asn]= {}

                for comm in specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn].keys():
                    if comm != 'announcedPrefixes':
                        percentageCommPerPerAS[rsName][day][asn][comm] = specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn][comm] / specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn]['announcedPrefixes'] * 100

    #process v6 files
    for day in tqdm(sorted(dateDir)):
        print(day)
        v4Files, v6Files = getAllFilesForDir(path + "/" + day, ixp)
        if len(v6Files) > 0:
            processFiles('v6', v6Files, day, path, finalRegex, specificCommunityCountDict, allCommunityCountDict)

            rsName = [k.split("_received_")[0] for k in v6Files if k.split("BGPFile")[0] == rsToConsider['v6'][ixp]][0]

            if rsName not in percentageCommPerPerAS.keys():
                percentageCommPerPerAS[rsName] = {}
            if day not in percentageCommPerPerAS[rsName].keys():
                percentageCommPerPerAS[rsName][day] = {}

            for asn in specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'].keys():
                if asn not in percentageCommPerPerAS[rsName][day].keys():
                    percentageCommPerPerAS[rsName][day][asn]= {}

                for comm in specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn].keys():
                    if comm != 'announcedPrefixes':
                        percentageCommPerPerAS[rsName][day][asn][comm] = specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn][comm] / specificCommunityCountDict[rsName][day]['communitiesPerASNsUsage'][asn]['announcedPrefixes'] * 100

   
    with open('allCommunitiesSeenAt' + ixp + '.json', 'w') as fp:
        json.dump(allCommunityCountDict, fp)

    with open('ixpCommunitiesSeenAt' + ixp + '.json', 'w') as fp:
        json.dump(specificCommunityCountDict, fp)

if __name__ == '__main__':
    main()
