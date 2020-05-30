import json
import os
from functools import reduce

cfg = json.load(
    open(os.path.join(os.path.dirname(__file__), '__defaults.json')))


def get_cfg(*keys, default=None, cast=lambda x: x):
    '''
        get returns the nested field from a dict.
        it will try to perform the given cast on the field value.
        if the cast fails or the value dne, the default is returned
    '''
    v = reduce(lambda d, key: d.get(key, default) if isinstance(
        d, dict) else default, keys, globals()['cfg'])
    try:
        return cast(v)
    except:
        return default
