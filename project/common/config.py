import importlib.util
from dataclasses import dataclass, asdict
from common.constants import *

@dataclass
class Config:
    # MODEL and INITIALIZATION
    model_class : str  # use CLASS.__name__
    dataset : str  # use CONSTANTS
    loss_fn : str  # use CONSTANTS
    pipeline : str   # use CONSTANTS
    activation : str # use CONSTANTS
    optimizer : str  # use CONSTANTS

    lr : float
    epochs : int
    model_shape : list[int]
    model_seed : int
    data_seed : int

    # DEFAULTED CONFIGS
    init_strategy_biases : InitializationStrategy = None
    init_strategy_weights : InitializationStrategy = None
    init_mean : float = None
    init_std : float = None

    task_description : dict = None
    n_samples : int = 800
    noise : float = None
    device: str = 'cpu'
    persist : bool = True  # wether to save the model at the checkpoints

    # OPTIONAL CONFIGS
    log_every_n_epochs: int = None
    log_graph_statistics: bool = True

    num_concat_datasets: int = None
    run_name : str = None
    wandb_url : str = None
    run_id : str = None
    local_dir_name: str = None 

    l1_lambda : float = None  # lambda for l1 regularisation
    bimt_local : bool = None  # if locality regularisation should be activated
    bimt_swap : int = None  # swap every n-th iteration
    bimt_prune : float = None  # if bimt thresholding in the end is activated.
    momentum : float = None
    batch_size : int  = None  # if None, batch size is dataset size
    description : str = None  # just add information about the idea behind the configuration for documentation purposes.

    # Early stopping
    early_stop_delta : float = 0.0
    early_stop_patience : int = None
    loss_cutoff : float = None  # if loss is less than this, stop training early
    
    # Pruning
    pruning_method : str = None  # RANDOM or MAGNITUDE
    extension_levels: int = 0 # how many 
    pruning_levels : int = None  # number of times pruning is applied
    pruning_rate   : float = None  # if pruning target is specified, pruning rate is overwritten
    pruning_target : int = None  # if specified, pruning rate is ignored
    prune_weights : bool = None
    prune_biases : bool = None

    # Set by program
    params_before_pruning : int = None # params in the beginning param_trajectory[0]
    params_prunable : int = None  # is set when pruning
    params_total  : int = None  # is set when pruning
    pruning_trajectory : list[int] = None
    param_trajectory : list[int] = None
    reinit : bool  = None  # reinitialize the network after pruning (only IMP)

    base_model_shape: str = None # if extenion overrides model shape, this is original

    def as_dict(self):
        data = asdict(self)
        return {key: value for key, value in data.items() if value is not None}

def import_config(filename):
    """Import a file, used for config."""
    if filename is None: return None

    # Remove the '.py' extension from the filename
    module_name = filename.replace('.py', '')

    # Create a module spec from the filename
    spec = importlib.util.spec_from_file_location(module_name, filename)

    # Create a new module based on the spec
    module = importlib.util.module_from_spec(spec)

    # Execute the module in its own namespace
    spec.loader.exec_module(module)

    config = getattr(module, 'run_config', None)
    if config is not None: return config

    config = getattr(module, 'sweep_config', None)
    if config is not None: return config

    raise ValueError('No valid config found.')