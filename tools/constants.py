import re

asesToAvoid = {
    'amsix': ['6777', '0'],
    'ixbr': ['0'],
    'decix': ['6695', '0'],
    'decixmad': ['48793', '0'],
    'decixnyc': ['63034', '0'],
    'linx': ["8714", '0'],
    'bcix': ["16374", "0"],
    'netnodstocb': ["52005", "0"],
}

communitiesToAvoid = {
    'amsix': ['6777:65011','6777:65012','6777:65021','6777:65022','6777:65023','6777:65511','6777:65522'],
    'ixbr': [],
    'decix': [],
    'decixmad': [],
    'decixnyc': [],
    'linx': ["8714:65010","8714:65011","8714:65012","8714:65020","8714:65021","8714:65022","8714:65023","8714:1000:1","8714:1000:2","8714:1000:4","8714:1001:1","8714:1001:2","8714:1001:5","8714:1001:6"],
    'bcix': [],
    'netnodstocb': ['52005:65012', '52005:65022', '52005:65032'],
}

ixpRegex = {
    'avoid' : {
        'ixbr' : re.compile('^65000:0:(\d+)$|^65000:(\d+)$|^ro:65000:(\d+)$|^rt:65000:(\d+)$'),
        'linx': re.compile('^8714:0:(\d+)$|^0:(\d+)$|^rt:0:(\d+)$'),
        'decix': re.compile('^6695:0:(\d+)$|^0:(\d+)$'),
        'decixmad': re.compile('^48793:0:(\d+)$|^0:(\d+)$'),
        'decixnyc': re.compile('^63034:0:(\d+)$|^0:(\d+)$'),
        'amsix': re.compile('^0:(\d+)$|^rt:0:(\d+)$|6777:0:(\d+)$'),
        'bcix': re.compile('^0:(\d+)$|^16374:0:(\d+)$'),
        'netnodstocb': re.compile('^0:(\d+)$|^rt:0:(\d+)$|^52005:0:(\d+)$'),
    },
    'allow' : {
        'ixbr' : re.compile('^65001:0:(\d+)$|^65001:(\d+)$|^ro:65001:(\d+)$|^rt:65001:(\d+)$'),
        'linx': re.compile('^8714:(\d+)$|^rt:8714:(\d+)$|^8714:1:(\d+)$'),
        'decix': re.compile('^65534:(\d+)$|^6695:(\d+)$|^6695:1:(\d+)$'),
        'decixmad': re.compile('^65534:(\d+)$|^48793:(\d+)$|^48793:1:(\d+)$'),
        'decixnyc': re.compile('^65534:(\d+)$|^63034:(\d+)$|^63034:1:(\d+)$'),
        'amsix': re.compile('^6777:(\d+)$|^rt:6777:(\d+)$|^6777:1:(\d+)$'),
        'bcix': re.compile('^16374:(\d+)$|^16374:1:(\d+)$'),
        'netnodstocb': re.compile('^52005:(\d+)$|^rt:rs_as:(\d+)$|^52005:1:(\d+)$'),
    },
    'prepend' : {
        'ixbr' : re.compile('^64601:(\d+)$|^64601:0:(\d+)$|^64602:(\d+)$|^64602:0:(\d+)$|^64603:(\d+)$|^64603:0:(\d+)$|^ro:64601:(\d+)$|^ro:64602:(\d+)$|^ro:64603:(\d+)$|^rt:64601:(\d+)$|^rt:64602:(\d+)$|^rt:64603:(\d+)$'),
        'linx': re.compile('^8714:65501$|^8714:65502$|^8714:65503$|^rt:8714:65501$|^rt:8714:65502$|^rt:8714:65503$|^8714:65501:1$|^8714:65502:2$|^8714:65503:3$|^65501:(\d+)$|^65502:(\d+)$|^65503:(\d+)$|^rt:65501:(\d+)$|^rt:65502:(\d+)$|^rt:65503:(\d+)$|^8714:65501:(\d+)$|^8714:65502:(\d+)$|^8714:65503:(\d+)$'),
        'decix': re.compile('^65001:(\d+)$|^65001:0$|^65002:(\d+)$|^65002:0$|^65003:(\d+)$|^65003:0$|^6695:101:(\d+)$|^6695:101:0$|^6695:102:(\d+)$|^6695:102:0$|^6695:103:(\d+)$|^6695:103:0$'),
        'decixmad': re.compile('^65001:(\d+)$|^65001:0$|^65002:(\d+)$|^65002:0$|^65003:(\d+)$|^65003:0$|^48793:101:(\d+)$|^48793:101:0$|^48793:102:(\d+)$|^48793:102:0$|^48793:103:(\d+)$|^48793:103:0$'),
        'decixnyc': re.compile('^65001:(\d+)$|^65001:0$|^65002:(\d+)$|^65002:0$|^65003:(\d+)$|^65003:0$|^48793:101:(\d+)$|^48793:101:0$|^48793:102:(\d+)$|^48793:102:0$|^48793:103:(\d+)$|^48793:103:0$'),
        'amsix': re.compile('^6777:65501$|^6777:65502$|^6777:65503$|^6777:101:(\d+)$|^6777:102:(\d+)$|^6777:103:(\d+)$'),
        'bcix': re.compile('^16374:101:(\d+)$|^16374:102:(\d+)$|^16374:103:(\d+)$'),
        'netnodstocb': re.compile('^65501:52005$|^65502:52005$|^65503:52005$|^65511:(\d+)$|^65512:(\d+)$|^65513:(\d+)$|^rt:65501:52005$|^rt:65502:52005$|^rt:65503:52005$|^rt:65511:(\d+)$|^rt:65512:(\d+)$|^rt:65513:(\d+)$|^52005:101:0$|^52005:102:0$|^52005:103:0$|^52005:101:(\d+)$|^52005:102:(\d+)$|^52005:103:(\d+)$'),
    },
    'blackhole' : {
        'ixbr' : re.compile('^65535:616:666$|^65535:666$|^ro:65535:666$|^rt:65535:666$'),
        'linx': re.compile('^65535:666$'),
        'decix': re.compile('^65535:666$'),
        'decixmad': re.compile('^65535:666$'),
        'decixnyc': re.compile('^65535:666$'),
        'amsix': re.compile('^65535:666$'),
        'bcix': re.compile('^65535:666$'),
        'netnodstocb': re.compile('^65535:666$'),
    }
}

ixpNameMapping = {
        'ixbr': 'IX.br-SP',
        'amsix': 'AMS-IX',
        'decix': 'DE-CIX',
        'decixmad': 'DE-CIX Mad',
        'decixnyc': 'DE-CIX NYC',
        'linx': 'LINX',
        'netnodstocb': 'Netnod Stock',
        'bcix': 'BCIX',
}


snapshotDates = {
    'v4':{
        'snap1': {
            'ixbr': '2021-07-19',
            'amsix': '2021-07-19',
            'decix': '2021-07-19',
            'decixmad': '2021-07-19',
            'decixnyc': '2021-07-19',
            'linx': '2021-07-19',
            'netnodstocb': '2021-07-19',
            'bcix': '2021-07-19',
        },
        'snap2': {
            'ixbr': '2021-07-25',
            'amsix': '2021-07-27',
            'decix': '2021-07-27',
            'decixmad': '2021-07-28',
            'decixnyc': '2021-07-28',
            'linx': '2021-07-26',
            'netnodstocb': '2021-07-26',
            'bcix': '2021-07-26',
        },
        'snap3': {
            'ixbr': '2021-08-02',
            'amsix': '2021-08-02',
            'decix': '2021-08-02',
            'decixmad': '2021-08-03',
            'decixnyc': '2021-08-03',
            'linx': '2021-08-02',
            'netnodstocb': '2021-08-04',
            'bcix': '2021-08-02',
        },
        'snap4': {
            'ixbr': '2021-08-08',
            'amsix': '2021-08-09',
            'decix': '2021-08-09',
            'decixmad': '2021-08-09',
            'decixnyc': '2021-08-09',
            'linx': '2021-08-09',
            'netnodstocb': '2021-08-09',
            'bcix': '2021-08-09',
        },
        'snap5': {
            'ixbr': '2021-08-16',
            'amsix': '2021-08-16',
            'decix': '2021-08-16',
            'decixmad': '2021-08-16',
            'decixnyc': '2021-08-16',
            'linx': '2021-08-16',
            'netnodstocb': '2021-08-16',
            'bcix': '2021-08-16',
        },
        'snap6': {
            'ixbr': '2021-08-23',
            'amsix': '2021-08-23',
            'decix': '2021-08-23',
            'decixmad': '2021-08-23',
            'decixnyc': '2021-08-23',
            'linx': '2021-08-23',
            'netnodstocb': '2021-08-23',
            'bcix': '2021-08-23',
        },
        'snap7': {
            'ixbr': '2021-08-31',
            'amsix': '2021-08-30',
            'decix': '2021-08-30',
            'decixmad': '2021-08-30',
            'decixnyc': '2021-08-30',
            'linx': '2021-08-30',
            'netnodstocb': '2021-08-30',
            'bcix': '2021-08-30',
        },
        'snap8': {
            'ixbr': '2021-09-07',
            'amsix': '2021-09-06',
            'decix': '2021-09-06',
            'decixmad': '2021-09-06',
            'decixnyc': '2021-09-06',
            'linx': '2021-09-06',
            'netnodstocb': '2021-09-06',
            'bcix': '2021-09-06',
        },
        'snap9': {
            'ixbr': '2021-09-13',
            'amsix': '2021-09-13',
            'decix': '2021-09-13',
            'decixmad': '2021-09-13',
            'decixnyc': '2021-09-13',
            'linx': '2021-09-13',
            'netnodstocb': '2021-09-13',
            'bcix': '2021-09-13',
        },
        'snap10': {
            'ixbr': '2021-09-20',
            'amsix': '2021-09-20',
            'decix': '2021-09-20',
            'decixmad': '2021-09-20',
            'decixnyc': '2021-09-20',
            'linx': '2021-09-20',
            'netnodstocb': '2021-09-20',
            'bcix': '2021-09-20',
        },
        'snap11': {
            'ixbr': '2021-09-28',
            'amsix': '2021-09-27',
            'decix': '2021-09-27',
            'decixmad': '2021-09-27',
            'decixnyc': '2021-09-27',
            'linx': '2021-09-27',
            'netnodstocb': '2021-09-27',
            'bcix': '2021-09-27',
        },
        'snap12': {
            'ixbr': '2021-10-04',
            'amsix': '2021-10-04',
            'decix': '2021-10-04',
            'decixmad': '2021-10-03',
            'decixnyc': '2021-10-03',
            'linx': '2021-10-03',
            'netnodstocb': '2021-10-02',
            'bcix': '2021-10-04',
        }
    },
    'v6':{
        'snap1': {
            'ixbr': '2021-07-19',
            'amsix': '2021-07-19',
            'decix': '2021-07-19',
            'decixmad': '2021-07-19',
            'decixnyc': '2021-07-19',
            'linx': '2021-07-19',
            'netnodstocb': '2021-07-19',
            'bcix': '2021-07-19',
        },
        'snap2': {
            'ixbr': '2021-07-26',
            'amsix': '2021-07-27',
            'decix': '2021-07-27',
            'decixmad': '2021-07-28',
            'decixnyc': '2021-07-28',
            'linx': '2021-07-26',
            'netnodstocb': '2021-07-26',
            'bcix': '2021-07-26',
        },
        'snap3': {
            'ixbr': '2021-08-03',
            'amsix': '2021-08-03',
            'decix': '2021-08-02',
            'decixmad': '2021-08-03',
            'decixnyc': '2021-08-03',
            'linx': '2021-08-02',
            'netnodstocb': '2021-08-04',
            'bcix': '2021-08-02',
        },
        'snap4': {
            'ixbr': '2021-08-10',
            'amsix': '2021-08-09',
            'decix': '2021-08-09',
            'decixmad': '2021-08-09',
            'decixnyc': '2021-08-09',
            'linx': '2021-08-09',
            'netnodstocb': '2021-08-09',
            'bcix': '2021-08-09',
        },
        'snap5': {
            'ixbr': '2021-08-16',
            'amsix': '2021-08-16',
            'decix': '2021-08-16',
            'decixmad': '2021-08-16',
            'decixnyc': '2021-08-16',
            'linx': '2021-08-16',
            'netnodstocb': '2021-08-16',
            'bcix': '2021-08-16',
        },
        'snap6': {
            'ixbr': '2021-08-22',
            'amsix': '2021-08-23',
            'decix': '2021-08-23',
            'decixmad': '2021-08-23',
            'decixnyc': '2021-08-23',
            'linx': '2021-08-23',
            'netnodstocb': '2021-08-24',
            'bcix': '2021-08-23',
        },
        'snap7': {
            'ixbr': '2021-08-31',
            'amsix': '2021-08-30',
            'decix': '2021-08-30',
            'decixmad': '2021-08-30',
            'decixnyc': '2021-08-30',
            'linx': '2021-08-30',
            'netnodstocb': '2021-08-30',
            'bcix': '2021-08-30',
        },
        'snap8': {
            'ixbr': '2021-09-05',
            'amsix': '2021-09-06',
            'decix': '2021-09-06',
            'decixmad': '2021-09-06',
            'decixnyc': '2021-09-06',
            'linx': '2021-09-06',
            'netnodstocb': '2021-09-06',
            'bcix': '2021-09-06',
        },
        'snap9': {
            'ixbr': '2021-09-13',
            'amsix': '2021-09-13',
            'decix': '2021-09-13',
            'decixmad': '2021-09-13',
            'decixnyc': '2021-09-13',
            'linx': '2021-09-13',
            'netnodstocb': '2021-09-13',
            'bcix': '2021-09-13',
        },
        'snap10': {
            'ixbr': '2021-09-20',
            'amsix': '2021-09-20',
            'decix': '2021-09-20',
            'decixmad': '2021-09-20',
            'decixnyc': '2021-09-20',
            'linx': '2021-09-20',
            'netnodstocb': '2021-09-20',
            'bcix': '2021-09-20',
        },
        'snap11': {
            'ixbr': '2021-09-27',
            'amsix': '2021-09-27',
            'decix': '2021-09-27',
            'decixmad': '2021-09-27',
            'decixnyc': '2021-09-27',
            'linx': '2021-09-27',
            'netnodstocb': '2021-09-27',
            'bcix': '2021-09-27',
        },
        'snap12': {
            'ixbr': '2021-10-04',
            'amsix': '2021-10-04',
            'decix': '2021-10-04',
            'decixmad': '2021-10-03',
            'decixnyc': '2021-10-03',
            'linx': '2021-10-03',
            'netnodstocb': '2021-10-02',
            'bcix': '2021-10-04',
        }
    }
}