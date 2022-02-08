import jax
import jax.numpy as jnp
from ..strategy import Strategy
from ..utils import GradientOptimizer


class PEPG_ES(Strategy):
    def __init__(
        self,
        num_dims: int,
        popsize: int,
        elite_ratio: float = 0.1,
        opt_name: str = "sgd",
    ):
        super().__init__(num_dims, popsize)
        self.elite_ratio = elite_ratio
        self.elite_popsize = int(self.popsize / 2 * self.elite_ratio)

        # Baseline = average of batch
        assert not self.popsize & 1, "Population size must be even"
        assert opt_name in ["sgd", "adam", "rmsprop", "clipup"]
        self.optimizer = GradientOptimizer[opt_name](self.num_dims)

    @property
    def params_strategy(self):
        es_params = {
            "sigma_init": 0.10,  # initial standard deviation
            "sigma_decay": 0.999,  # Anneal standard deviation
            "sigma_limit": 0.01,  # Stop annealing if less than this
            "sigma_lrate": 0.20,  # Learning rate for std
            "sigma_max_change": 0.2,  # Clip adaptive sigma to 20%
        }
        params = {**es_params, **self.optimizer.default_params}
        return params

    def initialize_strategy(self, rng, params):
        """
        `initialize` the differential evolution strategy.
        Initialize all population members by randomly sampling
        positions in search-space (defined in `params`).
        """
        initialization = jax.random.uniform(
            rng,
            (self.num_dims,),
            minval=params["init_min"],
            maxval=params["init_max"],
        )
        es_state = {
            "mean": initialization,
            "fitness": jnp.zeros(self.popsize) - 20e10,
            "lrate": params["lrate_init"],
            "sigma": jnp.ones(self.num_dims) * params["sigma_init"],
        }
        state = {**es_state, **self.optimizer.initialize(params)}
        return state

    def ask_strategy(self, rng, state, params):
        """`ask` for new parameter candidates to evaluate next."""
        # Antithetic sampling of noise
        z_plus = jax.random.normal(
            rng,
            (jnp.array(self.popsize / 2, int), self.num_dims),
        )
        z = jnp.concatenate([z_plus, -1.0 * z_plus])
        x = state["mean"] + z * state["sigma"].reshape(1, self.num_dims)
        return x, state

    def tell_strategy(self, x, fitness, state, params):
        # Reconstruct noise from last mean/std estimates
        noise = (x - state["mean"]) / state["sigma"]
        noise_1 = noise[: jnp.array(self.popsize / 2, int)]
        fit_1 = fitness[: jnp.array(self.popsize / 2, int)]
        fit_2 = fitness[jnp.array(self.popsize / 2, int) :]
        elite_idx = jnp.minimum(fit_1, fit_2).argsort()[: self.elite_popsize]

        fitness_elite = jnp.concatenate([fit_1[elite_idx], fit_2[elite_idx]])
        fit_diff = fit_1[elite_idx] - fit_2[elite_idx]
        fit_diff_noise = jnp.dot(noise_1[elite_idx].T, fit_diff)

        theta_grad = 1.0 / (self.elite_popsize) * fit_diff_noise
        # Grad update using optimizer instance - decay lrate if desired
        state = self.optimizer.step(theta_grad, state, params)
        state = self.optimizer.update(state, params)
        # Update sigma vector
        S = (
            noise_1 * noise_1
            - (state["sigma"] * state["sigma"]).reshape(1, self.num_dims)
        ) / state["sigma"].reshape(1, self.num_dims)
        rS = (fit_1 + fit_2) / 2.0 - jnp.mean(fitness_elite)
        delta_sigma = (jnp.dot(rS, S)) / self.elite_popsize
        change_sigma = params["sigma_lrate"] * delta_sigma
        change_sigma = jnp.minimum(
            change_sigma, params["sigma_max_change"] * state["sigma"]
        )
        change_sigma = jnp.maximum(
            change_sigma, -params["sigma_max_change"] * state["sigma"]
        )

        # adjust sigma according to the adaptive sigma calculation
        # for stability, don't let sigma move more than 20% of orig value
        state["sigma"] -= change_sigma
        state["sigma"] *= params["sigma_decay"]
        state["sigma"] = jnp.maximum(state["sigma"], params["sigma_limit"])
        return state
