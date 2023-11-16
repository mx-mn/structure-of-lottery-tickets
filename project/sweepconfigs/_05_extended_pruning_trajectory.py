"""72 Runs"""
from common.constants import *
m=2
sweep_config = {
    'method': 'grid', 
    'name': 'different network sizes',
    'parameters':{
        "extension_levels" : {
            "values": [6,7,8,9,10]
        },
        "model_seed":  {
            "values": [7, 9, 11]
        },
        # "pruning_method":  { "values": [RANDOM, MAGNITUDE]},
        "prune_biases" : { 
            'values' : [ True, False ]
        }
    }
}