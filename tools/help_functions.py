from collections import defaultdict
import os,sys

def human_format(num):
    num = float('{:.1f}'.format(num))
    #print(num)
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    if magnitude == 1:
        magnitude += 1
        num /= 1000.0
    #print(num, round(num, 2),'\n')
    num = round(num, 2)
    return '{}{}'.format('{:1f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

def readASesInRS():
    
    ASesInRS = {
        'v4': {
            'ixbr': defaultdict(set),
            'decix': defaultdict(set),
            'linx': defaultdict(set),
            'ixbrce': defaultdict(set),
            'ixbrrj': defaultdict(set),
            'decixmad': defaultdict(set),
            'decixnyc': defaultdict(set),
            'bcix': defaultdict(set),
            'netnodstocb': defaultdict(set),
            'netnodstocg': defaultdict(set),
            'amsix': defaultdict(set),
        },
        'v6': {
            'ixbr': defaultdict(set),
            'decix': defaultdict(set),
            'linx': defaultdict(set),
            'ixbrce': defaultdict(set),
            'ixbrrj': defaultdict(set),
            'decixmad': defaultdict(set),
            'decixnyc': defaultdict(set),
            'bcix': defaultdict(set),
            'netnodstocb': defaultdict(set),
            'netnodstocg': defaultdict(set),
            'amsix': defaultdict(set),
        }
    }

    with open('../tools/asesInRS.txt') as f:
        d = f.readlines()
        d = [i.strip() for i in d]

    for i in d:
        line = i.split("|")
        ASesInRS[line[2]][line[1]][line[0]] = [w.strip() for w in line[3].split(",")]

    return ASesInRS

def readASInfo():
    
    asInfo = {}

    with open('../tools/asnInfo.txt') as f:
        d = f.readlines()
        d = [i.strip() for i in d]

    for i in d:
        line = i.split("|")
        asInfo[line[0]] = line[2]

    return asInfo
