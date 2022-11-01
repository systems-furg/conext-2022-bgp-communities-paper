#!/usr/bin/python3
import sys, os, json, urllib.request
from tqdm import tqdm


communities = {}

ixpUrl = {
    'linx' : 'http://alice-rs.linx.net/api/v1/config',
    'ixbr': 'https://lg.ix.br/api/v1/config',
    'decix': 'https://lg.de-cix.net/api/v1/config',
    'amsix': 'http://lg.ams-ix.net/api/v1/config',
    'bcix': 'https://lg.bcix.de/api/v1/config',
    'netnod': 'https://lg.netnod.se/api/v1/config'
}

if __name__ == '__main__':

    ixp = sys.argv[1]

    if ixp not in ixpUrl.keys():
        print("Wrong parameter: only accepted IXPs are linx, ixbr, decix or amsix") 
        sys.exit()

    print("Downloading communities json....")
    r = urllib.request.urlopen(ixpUrl[ixp])

    data = json.loads(r.read())

    print("Processing communities json....")
    for reason in tqdm(data['noexport_reasons']):
        # print(reason)
        for code in data['noexport_reasons'][str(reason)]:
            # print(code)
            for comm in data['noexport_reasons'][str(reason)][str(code)]:
                # print(str(reason)+":"+str(code)+":"+str(comm)+"|"+data['noexport_reasons'][str(reason)][str(code)][str(comm)])
                bgpcomm = str(reason)+":"+str(code)+":"+str(comm)
                meaning = data['noexport_reasons'][str(reason)][str(code)][str(comm)]
                try:
                    communities[bgpcomm].add(meaning)
                except KeyError:
                    communities[bgpcomm] = set()
                    communities[bgpcomm].add(meaning)


    for reason in data['bgp_communities']:
        # print(reason)
        for code in data['bgp_communities'][str(reason)]:
            # print(code)
            try:
                for comm in data['bgp_communities'][str(reason)][str(code)]:
                    # print(str(reason)+":"+str(code)+":"+str(comm)+"|"+data['bgp_communities'][str(reason)][str(code)][str(comm)])
                    bgpcomm = str(reason)+":"+str(code)+":"+str(comm)
                    meaning = data['bgp_communities'][str(reason)][str(code)][str(comm)]
                    try:
                        communities[bgpcomm].add(meaning)
                    except KeyError:
                        try:
                            communities[bgpcomm] = set()
                            communities[bgpcomm].add(meaning)
                        except:
                            continue
            except TypeError:
                # print(str(reason)+":"+str(code)+"|"+data['bgp_communities'][str(reason)][str(code)])
                bgpcomm = str(reason)+":"+str(code)
                meaning = data['bgp_communities'][str(reason)][str(code)]
                try:
                    communities[bgpcomm].add(meaning)
                except KeyError:
                    try:
                        communities[bgpcomm] = set()
                        communities[bgpcomm].add(meaning)
                    except:
                        continue

    for comm in communities:
        for meaning in communities[comm]:
            print(str(comm)+"|"+str(meaning))