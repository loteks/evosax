import jax
import jax.numpy as jnp
from ..strategy import Strategy
from ..utils import GradientOptimizer


class Persistent_ES(Strategy):
    def __init__(self, num_dims: int, popsize: int, opt_name: str = "adam"):
        """Persistent ES (Vicol et al., 2021).
        The code & example are heavily adopted from the supplementary material:
        http://proceedings.mlr.press/v139/vicol21a/vicol21a-supp.pdf
        """
        super().__init__(num_dims, popsize)
        assert not self.popsize & 1, "Population size must be even"
        assert opt_name in ["sgd", "adam", "rmsprop", "clipup"]
        self.optimizer = GradientOptimizer[opt_name](self.num_dims)

    @property
    def params_strategy(self) -> dict:
        """Return default parameters of evolutionary strategy."""
        es_params = {
            "sigma_init": 0.1,  # Perturbation Std
            "sigma_decay": 0.999,
            "sigma_limit": 0.1,
            "T": 100,  # Total inner problem length
            "K": 10,  # Truncation length for partial unrolls
        }
        params = {**es_params, **self.optimizer.default_params}
        return params

    def initialize_strategy(self, rng, params) -> dict:
        """`initialize` the differential evolution strategy."""
        initialization = jax.random.uniform(
            rng,
            (self.num_dims,),
            minval=params["init_min"],
            maxval=params["init_max"],
        )
        es_state = {
            "mean": initialization,
            "pert_accum": jnp.zeros((self.popsize, self.num_dims)),
            "sigma": params["sigma_init"],
            "inner_step_counter": 0,
        }
        state = {**es_state, **self.optimizer.initialize(params)}
        return state

    def ask_strategy(self, rng, state, params):
        """`ask` for new proposed candidates to evaluate next."""
        # Generate antithetic perturbations
        pos_perts = (
            jax.random.normal(rng, (self.popsize // 2, self.num_dims))
            * state["sigma"]
        )
        neg_perts = -pos_perts
        perts = jnp.concatenate([pos_perts, neg_perts], axis=0)
        # Add the perturbations from this unroll to the perturbation accumulators
        state["pert_accum"] += perts
        y = state["mean"] + perts
        return jnp.squeeze(y), state

    def tell_strategy(self, x, fitness, state, params):
        """`tell` update to ES state."""
        theta_grad = jnp.mean(
            state["pert_accum"]
            * fitness.reshape(-1, 1)
            / (state["sigma"] ** 2),
            axis=0,
        )
        # Grad update using optimizer instance - decay lrate if desired
        state = self.optimizer.step(theta_grad, state, params)
        state = self.optimizer.update(state, params)
        state["inner_step_counter"] += params["K"]

        state["sigma"] *= params["sigma_decay"]
        state["sigma"] = jnp.maximum(state["sigma"], params["sigma_limit"])
        # Reset accumulated antithetic noise memory if done with inner problem
        reset = state["inner_step_counter"] >= params["T"]
        state["inner_step_counter"] = jax.lax.select(
            reset, 0, state["inner_step_counter"]
        )
        state["pert_accum"] = jax.lax.select(
            reset, jnp.zeros((self.popsize, self.num_dims)), state["pert_accum"]
        )
        return state
