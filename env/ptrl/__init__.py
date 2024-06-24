from gymnasium.envs.registration import register



# Register the 'RLP (reiforcement learning petrinet)' environment
register(
    id="ptrl-agv-v0",
    entry_point="ptrl.envs.agv.gym_env:AgvEnv",
)



