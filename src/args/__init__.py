from collections import namedtuple
from json import load as json_load

def get_args():
    with open('config.json') as fp:
        result = json_load(fp)    
    Configs = namedtuple('configs', result.keys())    
    return Configs(*result.values())