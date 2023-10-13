import wandb
from common import pruning
from common.torch_utils import measure_global_sparsity
from common.tracking import Config, get_model_path, save_model
from common.training import evaluate, train_and_evaluate

SUMMARY = 'summary'
LOSS = 'loss'
EVAL = 'eval'
TRAIN = 'train'
BEST = 'best'
LAST = 'last'
PRUNE_ITER = 'prune_iter'
SPARSITY = 'sparsity'

BEST_EVAL = 'val_loss'  # "-".join((SUMMARY, LOSS, EVAL+BEST))
BEST_TRAIN = "-".join((SUMMARY, LOSS, TRAIN+BEST))

def run(model, train_loader, test_loader, optim, loss_fn, config: Config):
    device = config.device
    model_path = get_model_path(config)


    # TODO: With SWEEPS this doesnt work as optimization metric
    # wandb.define_metric(PRUNE_ITER)
    # wandb.define_metric(BEST_EVAL, summary="min", step_metric=PRUNE_ITER)
    # wandb.define_metric(BEST_TRAIN, summary="min", step_metric=PRUNE_ITER)
    # wandb.define_metric(SPARSITY, summary="min", step_metric=PRUNE_ITER)

    # preparing for pruning and [OPTIONALLY] save model state
    params_to_prune = pruning.convert_to_pruning_model(model.modules, prune_weights=True, prune_biases=True)
    if config.reinit: reinit_model_state_dict = pruning.get_model_state_dict(model, drop_masks=True)
    if config.persist: save_model(model, iteration=0, base=model_path)

    # log initial performance
    eval_loss_init = evaluate(model, test_loader, loss_fn, device).mean().item()

    wandb.log({
        BEST_EVAL : eval_loss_init,
        PRUNE_ITER : 0,
        SPARSITY : 0,
    })
    
    # loop over pruning levels
    for lvl in range(1, config.pruning_levels+1):
        
        N0, N, sparsity = measure_global_sparsity(model, use_mask=True)        
        train_losses, eval_losses = train_and_evaluate(model, train_loader, test_loader, optim, loss_fn, device, epochs=config.training_epochs)

        wandb.log({
            BEST_EVAL : min(eval_losses),
            BEST_TRAIN: min(train_losses),
            PRUNE_ITER : lvl,
            SPARSITY : sparsity,
            })
        
        if config.persist: save_model(model, iteration=lvl, base=model_path)

        # prune by global magnitude
        pruning.global_magnitude_pruning(params_to_prune, config.pruning_rate)

        # [OPTIONAL] reinit
        if config.reinit: model.load_state_dict(reinit_model_state_dict, strict=False)
    
    # final finetuning
    N0, N, sparsity = measure_global_sparsity(model, use_mask=True)        
    train_losses, eval_losses = train_and_evaluate(model, train_loader, test_loader, optim, loss_fn, device, epochs=config.training_epochs)
    wandb.log({
        BEST_EVAL : min(eval_losses),
        BEST_TRAIN: min(train_losses),
        PRUNE_ITER : lvl +1,
        SPARSITY : sparsity,
        })

    if config.persist: save_model(model, iteration=lvl+1, base=model_path)

    return model