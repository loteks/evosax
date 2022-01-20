import jax
import jax.numpy as jnp
from ..strategy import Strategy
from ..utils import adam_step


class Open_NES(Strategy):
    def __init__(self, num_dims: int, popsize: int):
        super().__init__(num_dims, popsize)
        assert not self.popsize & 1, "Population size must be even"

    @property
    def params_strategy(self):
        """Return default parameters of evolutionary strategy."""
        params = {
            "lrate_init": 0.01,  # Adam learning rate outer step
            "lrate_decay": 0.999,
            "lrate_limit": 0.01,
            "beta_1": 0.99,  # beta_1 outer step
            "beta_2": 0.999,  # beta_2 outer step
            "eps": 1e-8,  # eps constant outer step,
            "sigma_init": 0.1,
            "sigma_decay": 0.999,
            "sigma_limit": 0.1,
        }
        return params

    def initialize_strategy(self, rng, params):
        """`initialize` the evolutionary strategy."""
        initialization = jax.random.uniform(
            rng,
            (self.num_dims,),
            minval=params["init_min"],
            maxval=params["init_max"],
        )
        state = {
            "mean": initialization,
            "sigma": params["sigma_init"],
            "lrate": params["lrate_init"],
            "m": jnp.zeros(self.num_dims),
            "v": jnp.zeros(self.num_dims),
        }
        return state

    def ask_strategy(self, rng, state, params):
        """`ask` for new parameter candidates to evaluate next."""
        # Antithetic sampling of noise
        z_plus = jax.random.normal(
            rng,
            (jnp.array(self.popsize / 2, int), self.num_dims),
        )
        z = jnp.concatenate([z_plus, -1.0 * z_plus])
        x = state["mean"] + state["sigma"] * z
        return x, state

    def tell_strategy(self, x, fitness, state, params):
        """`tell` performance data for strategy state update."""
        # Reconstruct noise from last mean/std estimates
        noise = (x - state["mean"]) / state["sigma"]
        theta_grad = (
            1.0 / (self.popsize * state["sigma"]) * jnp.dot(noise.T, fitness)
        )

        # Natural grad update using optax API!
        state = adam_step(state, params, theta_grad)

        # Update lrate and standard deviation based on min and decay
        state["lrate"] *= params["lrate_decay"]
        state["lrate"] = jnp.maximum(state["lrate"], params["lrate_limit"])

        state["sigma"] *= params["sigma_decay"]
        state["sigma"] = jnp.maximum(state["sigma"], params["sigma_limit"])
        return state
