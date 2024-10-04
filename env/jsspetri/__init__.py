from gymnasium.envs.registration import register



# Register the 'jsspetri-mono' environment
register(
    id="jsspetri-v0",
    entry_point="jsspetri.envs.mono.gym_env:MonoEnv",
)

# Register the 'jsspetri-multi' environment
register(
    id="jsspetri-multi-v0",
    entry_point="jsspetri.envs.multi.gym_env:MultiEnv",
)

# Register the 'jsspetri-multi' environment
register(
    id="jsspetri-heuristic-v0",
    entry_point="jsspetri.envs.heuristic.gym_env:HeuristicEnv",
)


# Register the 'jsspetri-multi' environment
register(
    id="jsspetri-fms-v0",
    entry_point="jsspetri.envs.fms.gym_env:FmsEnv",
)

