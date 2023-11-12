Idea

Goal

Why is it interesting ? 

Experiments inspired by BIMT

Does IMP find independent tasks? 
If the lottery ticket is good, it should not cointain unnecessary components. Therefore shouldnt have connections to random inputs

Idea :
Concatenate the Dataset together
2 Input 2 output.
Then experiment with IMP and see if the Model ends up as 2 sperate models
So far, this happens quite consistently. It is really expensive to measure how close we are to 2 disconnected models, so either it is disconnected or not.

This can be done with arbitrary many tasks.
Only classification though

Experiments on Regresssion with iterative Magnitude Pruning were not successful. Probably due to the inherent numerical Delicacy with Regression. Regression is Analog, Classification is digital.

So: Concatenaded Moons or Two * N Moons Dataset.
Training Lottery ticket works.
\__/ This is what the val_los graph should look like. Used early stopping to save time.

So far it doesnt seem to work
By the time the Network splits, it does not seem to be a lottery ticket anymore. It merely is a weak classifier. Lets try without noise? 


TODO: Try without noise. Find way to say (I want this model down to 40 params.) and the pruning rate is implicitly calculated, depending on the number of pruning iterations (which are the metric of money).

Fit an exponential curve to 2 points : number of prunable params before pruning and the desired number after pruning. This fitted exponential is discretized with n steps, where n is the number of pruning levels that are selected. 
This effectively creates a setup where it is easily possible to tune the hyperparameters. 
Network size and pruning iterations are the parameters that change the training time significantly.


TODO:
There are interesting Metrics I would like to track, ideally during training of a Soon-to-be-Lottery ticket.
* number of prunable / non-prunable parameters remaining and number of weights and number of biases.
* number of zombie neurons (Life)



New experimental results 'hezzefi6' show that the zombies survive longer when they have a large positive bias.

TODO: 
track the weights over time, where they end up. Delete weights that are 0. dont log them.


YAY! Milestone
I found a setup, where the NN splits before the network quality degrades substantially.
This is cool
The question also is
How likely is it, that the network splits exactly how I want it to be?
And, at what point should/could the network split first, and when will it split for sure.

There seems to be a relationship between not splitting and bad performance.


### params

multiplying the number of neurons in the hidden layer by n, increases the number of weights by a factor of n**2
The largest possible split subnetworks. lets say neural network has the number of parameters $P$ that covers $k$ equal task.
Then, the minimum number of weights to remove, such that the largest possible complete subnetworks arise is 
$$\frac{P(k-1)}{k}$$
and the minimum number of parameters where this split occurs is obviously 
$$\frac{P}{k}$$


## Observations
* Zomie Neurons appear more often at higher sparsities
* Zombie Neurons can appear to survive longer if their associated bias is larger. Zombies with negative, 
* Comatose Neurons appear to only survive for few iterations
* Comatose Neurons behave very similarly across different seed-runs  
    * why? As soon as they become comatose, they do not receive any updates. When the average parameter rises, they lower relatively to the others.
* Negative Biases disappear (pruned, turn positive) --> RELU -> negative bias increases likelihood of 0-Activation and therefore no update which increases likelihood of pruning.

the pruning horizon. It increases steadily. 


## Experiments to run

What is actually interesting to test? What are the Hypothesis?

Hypothesis :
New experiment, broader hidden size.
What do I expect ? 

Comatose Neurons seem to follow a pattern like existence. First a peak, as the randomly dying neurons click out. Then they start to disappear fast. Then, the features that are deleted on purpose 
![Alt text](image-1.png)

This graph looks very cool  and is actually interesting.
It looks like the peak is relative between beginning and end.
So say, the peaks is **always** around iteration 12 of 20. lets say 11-13


Notes on experiments
the runs were fast up until 2 layer 600 or say 700.
Then tey quickly started to get very looong.

Now lets do experiments up until 300k parameters. Later it gets really really slow



# Plotting Network splitting

Goal. I want to see how network size (number of parameters) influences splitting pf the network.
To really compare, the networks would need to be pruned at the same parameters. 

When I keep the pruning iterations constant, but increase P, then the pruning rate is larger and the steps are at different numbers.

Then, it is hard to compare, since the steps where the network would exist are at different place, with different distances to each other.
How can we avoid that? 

Increasing P leads to an increased

Could compare: 
* one more pruning iteration and increase the number of parameters by *pr*, so that after 1 pruning iteration, the network has the same number of parameters.
* also simply increase the number of pruning iterations, without increasing P.

Then, if increasing parameters yields better results, more parameters mean better splitting.

Experiment setup:

I have a model with a defined Shape $S_0$ and associated number of prunable parameters $P_0$.
I decide for a pruning target $P_T$, the number of prunable parameters left after $T$ iterations of pruning.
The pruning rate $p$ is implicit form $P_0$, $P_T$ and $T$.  

The model can be extended. To extend the model according the the pruning trajectory $[P_0, P_1,...P_{T-1},P_T]$, the inverse pruning rate, or growing rate $g$ is calculated as follows
$$(1-p)*(1+g) = 1 \quad g = \frac{1}{1-p} - 1$$

To to get the shape of the extended model $S_{-1}$, first the number of parameters are calculated $P_{-1} = P_0 * (1+g)$.
The parameters are rounded to an integer, and the solve for the simple equation for the hidden dimension, which is the only variable in $S$ that we can change.

This can be generalized to 
$$
P_{-k} = P_0 * (1+g)^k
$$

The trajectory is simply extended, such that pruning $P_{-1}$ for one iteration yields $P_0$, which makes the networks comparable based on the number of prunable parameters they have.

### TODOs

What are the minimum defining characteristics for extending a network? 
Number of extensions, pruning rate, initial shape


- 