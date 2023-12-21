from common.models import SimpleMLP
from common.config import Config
from common.constants import *

m = 2

run_config = Config(
    description='''This is the winning formula. The netowrk splits before the performance degrades.''',
    pipeline=IMP,
    activation=RELU,
    loss_fn= BCE,
    
    dataset=OLD_MOONS,  # works reliably
    #dataset=MULTI_MOONS,  # works reliably

    num_concat_datasets=m,
    
    model_shape=[m*2, 40, 40, m],
    model_class = SimpleMLP.__name__,

    # noise = 0.1

    # training
    lr=0.001,
    optimizer=ADAM,
    training_epochs= 3000,

    # seeds
    model_seed=7, # good seeds : 2
    data_seed=0,  # split old but not new
    # data_seed=1, # splits old but not new
    # data_seed=0, # splits

    persist=False,

    # early stop
    early_stopping=True,
    early_stop_patience=10,
    early_stop_delta=0.0,

    # yielded good results
    loss_cutoff=0.01,  

    # pruning
    pruning_method=MAGNITUDE,
    prune_biases=True,
    prune_weights=True,
    pruning_target=50,
    pruning_levels=20,
    reinit=True,

    # newly added 
    init_strategy_weights = None,
    init_strategy_biases = None,
    n_samples=1000,
    #noise=0.0,
    noise=0.0,
    init_mean=None,
    init_std=None,
)
