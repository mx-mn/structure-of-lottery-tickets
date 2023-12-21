from tqdm import tqdm
from common.log import Logger, returns_true_every_nth_time
from common.config import Config
from common.nxutils import GraphManager
from common.persistance import save_model_or_skip
from common.pruning import build_pruning_func, build_reinit_func, count_prunable_params
from common.training import build_early_stopper, build_optimizer, update, evaluate
from common.constants import *

def run(model, train_loader, test_loader, loss_fn, config: Config):

    # preparing for pruning and [OPTIONALLY] save model state
    prune = build_pruning_func(model, config)
    reinit = build_reinit_func(model)
    gm = GraphManager(model, config.model_shape, config.task_description, config.extension_levels) if config.log_graph_statistics else None
    log = Logger(config.task_description, True)
    save_model_or_skip(model, config, f'{-config.extension_levels}_init')
    
    # log initial performance and descriptive statistics
    init_loss, init_accuracy = evaluate(model, test_loader, loss_fn, config.device)
    log.metrics({VAL_LOSS:init_loss, ACCURACY:init_accuracy, 'level': -config.extension_levels-1})
    # log.descriptive_statistics(model, at_init=True)
    log.commit()  # LOG BEFORE TRAINING

    # get the complete levels
    levels = list(range(-config.extension_levels, config.pruning_levels))

    pparams = config.param_trajectory[0]
    pborder = 0

    ####################
    ### Training 
    ####################
    for level, pruning_amount in tqdm(zip(levels, config.pruning_trajectory, strict=True), 'Pruning Levels', len(levels)):
        log_now = returns_true_every_nth_time(n=config.log_every_n_epochs, and_at_0=True)

        # train and evaluate the model and log the performance
        optim = build_optimizer(model, config)
        stopper = build_early_stopper(config)

        for epoch in tqdm(range(config.epochs), f'Training Level {level}', config.epochs):
            train_loss = update(model, train_loader, optim, loss_fn, config.device, config.l1_lambda)
            val_loss, val_acc = evaluate(model, test_loader, loss_fn, config.device)

            log.metrics(
                prefix='epoch/',
                only_if_true=log_now(),
                values={TRAIN_LOSS : train_loss.mean(), VAL_LOSS : val_loss, ACCURACY : val_acc.mean()},
            )
            # log.commit()
            # log.descriptive_statistics(model, prefix=f'epochwise-descriptive')

            if config.loss_cutoff is not None and val_loss.mean().item() < config.loss_cutoff: break
            if stopper(val_loss.mean().item()): break

        save_model_or_skip(model, config, level)

        # log weights, biases, metrics at early stopping iteration
        log.metrics({TRAIN_LOSS : train_loss, VAL_LOSS : val_loss, ACCURACY : val_acc})
        log.metrics({'pparams' : pparams, 'level' : level, 'stop' : epoch, 'pborder' : pborder})
        # log.descriptive_statistics(model)

        gm.update(model) if gm is not None else None
        log.feature_categorization(gm)
        log.splitting(gm)
        log.graphs(gm)
        
        # there is only one commit in each Pruning LEVEL! except in-epoch logging is active
        log.commit()  # LOG PRUNING LEVEL

        # prune the model and reinit
        pborder = prune(pruning_amount)
        pparams -= pruning_amount
        if config.reinit: reinit(model)
    
    log.metrics({'pparams' : pparams, 'level' : config.pruning_levels, 'pborder' : pborder})

    ####################
    ### final finetuning
    ####################
    stopper = build_early_stopper(config)
    optim = build_optimizer(model, config)
    log_now = returns_true_every_nth_time(config.log_every_n_epochs)

    for epoch in tqdm(range(config.epochs), f'Final Finetuning', config.epochs):

        train_loss = update(model, train_loader, optim, loss_fn, config.device, config.l1_lambda)
        val_loss, val_acc = evaluate(model, test_loader, loss_fn, config.device)
        mean_eval_loss: float = val_loss.mean().item()

        #log.descriptive_statistics(model, prefix=f'epoch/')
        log.metrics(
            prefix='epoch/',
            only_if_true=log_now(),
            values={TRAIN_LOSS : train_loss.mean(), VAL_LOSS : val_loss, ACCURACY : val_acc.mean()}
        )
        #log.commit()  # TODO: this breaks logging of the last metrics correctly.

        if stopper(mean_eval_loss): break

    log.metrics({TRAIN_LOSS : train_loss, VAL_LOSS : val_loss, ACCURACY : val_acc})
    # log.descriptive_statistics(model)

    gm.update(model) if gm is not None else None
    log.feature_categorization(gm)
    log.splitting(gm)
    log.graphs(gm)
    log.summary(gm)
    log.commit()

    save_model_or_skip(model, config, config.pruning_levels)
