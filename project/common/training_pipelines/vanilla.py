import wandb
from common.config import Config
from common.log import log_loss
from common.persistance import save_model_or_skip
from common.training import build_early_stopper, build_optimizer, evaluate, update
from common.constants import *

def run(model, train_loader, test_loader, loss_fn, config: Config):
    # TODO: fix log_loss with commit
    optim = build_optimizer(model, config)
    stop = build_early_stopper(config)

    # log initial performance
    loss_init = evaluate(model, test_loader, loss_fn, config.device)
    wandb.log(log_loss(loss_init, VAL_LOSS))

    # train and evaluate
    for _ in range(0, config.training_epochs):
        
        # update
        loss_train = update(model, train_loader, optim, loss_fn, config.device, config.l1_lambda).mean()
        wandb.log(log_loss(loss_train, TRAIN_LOSS), commit=False)

        # evaluate
        loss_eval = evaluate(model, test_loader, loss_fn, config.device)
        wandb.log(log_loss(loss_eval, VAL_LOSS))

        if stop(loss_eval.mean().item()): break

    # store model
    save_model_or_skip(model, config, config.training_epochs)

    return model