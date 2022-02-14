# `evosax`: JAX-Based Evolution Strategies 🦎
[![Pyversions](https://img.shields.io/pypi/pyversions/evosax.svg?style=flat-square)](https://pypi.python.org/pypi/evosax) [![PyPI version](https://badge.fury.io/py/evosax.svg)](https://badge.fury.io/py/evosax)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/RobertTLange/evosax/branch/main/graph/badge.svg?token=5FUSX35KWO)](https://codecov.io/gh/RobertTLange/evosax)
<a href="https://github.com/RobertTLange/evosax/blob/main/docs/logo.png?raw=true"><img src="https://github.com/RobertTLange/evosax/blob/main/docs/logo.png?raw=true" width="170" align="right" /></a>

Tired of having to handle asynchronous processes for neuroevolution? Do you want to leverage massive vectorization and high-throughput accelerators for evolution strategies (ES)? `evosax` allows you to leverage JAX, XLA compilation and autovectorization to scale ES to your favorite accelerators. The API leverages the classical `ask`, `evaluate`, `tell` cycle of ES. Both `ask` and `tell` calls can leverage `jit`, `vmap`/`pmap` and `lax.scan`. It includes a vast set of both classic (e.g. CMA-ES, Differential Evolution, etc.) and modern neuroevolution (e.g. OpenAI-ES, Augmented RS, etc.) strategies. Get started here 👉 [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobertTLange/evosax/blob/main/examples/getting_started.ipynb)

## Basic `evosax` API Usage 🍲

```python
import jax
from evosax import CMA_ES
from evosax.problems import ClassicFitness

# Instantiate the search strategy
rng = jax.random.PRNGKey(0)
evaluator = ClassicFitness("rosenbrock", num_dims=2)
strategy = CMA_ES(popsize=20, num_dims=2, elite_ratio=0.5)
params = strategy.default_params
state = strategy.initialize(rng, params)

# Run ask-eval-tell loop - NOTE: By default minimization
for t in range(num_generations):
    rng, rng_gen, rng_eval = jax.random.split(rng, 3)
    x, state = strategy.ask(rng_gen, state, params)
    fitness = evaluator.rollout(rng_eval, x)
    state = strategy.tell(x, fitness, state, params)

# Get best overall population member & its fitness
state["best_member"], state["best_fitness"]
```

## Implemented Evolution Strategies 🦎

| Strategy | Reference | Import | Example |
| --- | --- | ---  | --- |
| OpenAI-ES | [Salimans et al. (2017)](https://arxiv.org/pdf/1703.03864.pdf) | [`Open_ES`](https://github.com/RobertTLange/evosax/tree/main/evosax/strategies/open_es.py) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobertTLange/evosax/blob/main/examples/03_cnn_mnist.ipynb)
| PEPG | [Sehnke et al. (2010)](https://citeseerx.ist.psu.edu/viewdoc/download;jsessionid=A64D1AE8313A364B814998E9E245B40A?doi=10.1.1.180.7104&rep=rep1&type=pdf) | [`PEPG_ES`](https://github.com/RobertTLange/evosax/tree/main/evosax/strategies/pepg_es.py)  | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobertTLange/evosax/blob/main/examples/03_cnn_mnist.ipynb)
| ARS | [Mania et al. (2018)](https://arxiv.org/pdf/1803.07055.pdf) | [`Augmented_RS`](https://github.com/RobertTLange/evosax/tree/main/evosax/strategies/ars.py)  | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobertTLange/evosax/blob/main/examples/03_cnn_mnist.ipynb)
| CMA-ES | [Hansen (2016)](https://arxiv.org/abs/1604.00772) | [`CMA_ES`](https://github.com/RobertTLange/evosax/tree/main/evosax/strategies/cma_es.py) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobertTLange/evosax/blob/main/examples/01_classic_low_d.ipynb)
| Simple Gaussian | [Rechenberg (1975)](https://onlinelibrary.wiley.com/doi/abs/10.1002/fedr.19750860506) | [`Simple_ES`](https://github.com/RobertTLange/evosax/tree/main/evosax/strategies/simple_es.py) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobertTLange/evosax/blob/main/examples/01_classic_low_d.ipynb)
| Simple Genetic | [Such et al. (2017)](https://arxiv.org/abs/1712.06567) | [`Simple_GA`](https://github.com/RobertTLange/evosax/tree/main/evosax/strategies/simple_ga.py) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobertTLange/evosax/blob/main/examples/01_classic_low_d.ipynb)
| x-NES | [Wierstra et al. (2014)](https://www.jmlr.org/papers/volume15/wierstra14a/wierstra14a.pdf) | [`xNES`](https://github.com/RobertTLange/evosax/tree/main/evosax/strategies/xnes.py)  | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobertTLange/evosax/blob/main/examples/01_classic_low_d.ipynb)
| Particle Swarm Optimization | [Kennedy & Eberhart (1995)](https://ieeexplore.ieee.org/document/488968) | [`PSO_ES`](https://github.com/RobertTLange/evosax/tree/main/evosax/strategies/pso_es.py)  | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobertTLange/evosax/blob/main/examples/01_classic_low_d.ipynb)
| Differential ES | [Storn & Price (1997)](https://www.metabolic-economics.de/pages/seminar_theoretische_biologie_2007/literatur/schaber/Storn1997JGlobOpt11.pdf) | [`Differential_ES`](https://github.com/RobertTLange/evosax/tree/main/evosax/strategies/differential_es.py)  | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobertTLange/evosax/blob/main/examples/01_classic_low_d.ipynb)
| Persistent ES | [Vicol et al. (2021)](http://proceedings.mlr.press/v139/vicol21a.html) | [`Persistent_ES`](https://github.com/RobertTLange/evosax/tree/main/evosax/strategies/persistent_es.py)  | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobertTLange/evosax/blob/main/examples/04_mlp_pes.ipynb)
| Population-Based Training | [Jaderberg et al. (2017)](https://arxiv.org/abs/1711.09846) | [`PBT_ES`](https://github.com/RobertTLange/evosax/tree/main/evosax/strategies/pbt_es.py)  | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobertTLange/evosax/blob/main/examples/05_quadratic_pbt.ipynb)

## Installation ⏳

The latest `evosax` release can directly be installed from PyPI:

```
pip install evosax
```

If you want to get the most recent commit, please install directly from the repository:

```
pip install pip install git+https://github.com/RobertTLange/evosax.git@main
```

In order to use JAX on your accelerators, you can find more details in the [JAX documentation](https://github.com/google/jax#installation).

## Examples 📖
* 📓 [Classic ES Tasks](https://github.com/RobertTLange/evosax/blob/main/examples/01_classic_low_d.ipynb): Simple API introduction on Rosenbrock function.
* 📓 [Pendulum-Control](https://github.com/RobertTLange/evosax/blob/main/examples/02_mlp_control.ipynb): Neuroevolution on the `Pendulum-v1` gym task.
* 📓 [MNIST-Classifier](https://github.com/RobertTLange/evosax/blob/main/examples/03_cnn_mnist.ipynb): OpenES/PEPG/ARS on MNIST-MLP.
* 📓 [LRateTune-PES](https://github.com/RobertTLange/evosax/blob/main/examples/04_mlp_pes.ipynb): Persistent ES on meta-learning problem.
* 📓 [Quadratic-PBT](https://github.com/RobertTLange/evosax/blob/main/examples/05_quadratic_pbt.ipynb): Population-Based Training on quadratic problem.

## Key Selling Points 💵

- **Strategy Diversity**: `evosax` implements a diverse set of both classic and modern neuroevolution strategies. All of them follow the same simple `ask`/`eval` API and come with tailored tools such as [ClipUp](https://arxiv.org/abs/2008.02387) optimization, parameter reshaping into PyTrees and fitness shaping (see below).

- **Vectorization/Parallelization of `ask`/`tell` Calls**: Both `ask` and `tell` calls can leverage `jit`, `vmap`/`pmap`. This enables vectorized/parallel rollouts of different evolution strategies.

```Python
from evosax import Augmented_RS
# E.g. vectorize over different lrate decays
strategy = Augmented_RS(popsize=100, num_dims=20)
es_params = {
    "lrate_decay": jnp.array([0.999, 0.99, 0.9]),
    ...
}
map_dict = {
    "lrate_decay": 0,
    ...
}
batch_init = jax.vmap(strategy.init, in_axes=(None, map_dict))
batch_ask = jax.vmap(strategy.ask, in_axes=(None, 0, map_dict)) #
batch_tell = jax.vmap(strategy.tell, in_axes=(0, 0, 0, map_dict))
```

- **Scan Through Evolution Rollouts**: You can also `lax.scan` through entire `init`, `ask`, `eval`, `tell` loops for fast compilation:

```Python
@partial(jax.jit, static_argnums=(4,))
def run_es_loop(rng num_steps):
    """Run evolution ask-eval-tell loop."""
    es_params = strategy.default_params

    def es_step(state_input, tmp):
        """Helper function to lax.scan through."""
        rng, state = state_input
        rng, rng_iter = jax.random.split(rng)
        x, state = strategy.ask(rng_iter, state, es_params)
        fitness = evaluate(x)
        state = strategy.tell(y, fitness, state, es_params)
        return [rng, state, hidden, -fitness], fitness[jnp.argmin(fitness)]

    _, scan_out = jax.lax.scan(es_step,
                               [rng, state],
                               [jnp.zeros(num_steps)])
    return jnp.min(scan_out)
```

- **Population Parameter Reshaping**: We provide a `ParamaterReshaper` wrapper to reshape flat parameter vectors into PyTrees. These are compatible with popular JAX neural network libraries such as Flax and Haiku.

```Python
from evosax import ParameterReshaper
from flax import linen as nn

class MLP(nn.Module):
    """Simple ReLU MLP."""

    num_hidden_units: int
    ...

    @nn.compact
    def __call__(self, obs):
        ...
        return ...

network = MLP(64)
policy_params = network.init(rng, jnp.zeros(4,), rng)
param_reshaper = ParameterReshaper(policy_params["params"])

# Get total number of parameters to evolve
param_reshaper.total_params

# Dictinory to vectorize rollouts over
param_reshaper.vmap_dict

# Get population candidates & reshape into pytrees
x = strategy.ask(...)
x_shaped = param_reshaper.reshape(x)
```


- **Flexible Fitness Shaping**:

```Python
from evosax import FitnessShaper

# Instantiate jittable helper class for fitness shaping
fit_shaper = FitnessShaper(centered_rank=True,
                           z_score=True,
                           weight_decay=0.01,
                           maximize=True)
fit_shaped = fit_shaper.apply(x, fitness) 
```


## References & Other Great JAX-ES Tools 📝
* 💻 [Evojax](https://github.com/google/evojax): JAX-ES library by Google Brain with great rollout wrappers.
* 💻 [QDax](https://github.com/adaptive-intelligent-robotics/QDax): Quality-Diversity algorithms in JAX.
* 💻 [Rob's Blog](https://roberttlange.github.io/posts/2020/12/neuroevolution-in-jax/): Tutorial on CMA-ES & leveraging JAX's primitives.

## Development 👷

You can run the test suite via `python -m pytest -vv tests/`. If you find a bug or are missing your favourite feature, feel free to create an issue and/or start [contributing](CONTRIBUTING.md) 🤗.

