from gymnasium.envs.registration import register



# Register the 'RLP (reiforcement learning petrinet)' environment
register(
    id="ptrl-agv-v0",
    entry_point="ptrl.envs.agv.gym_env:AgvEnv",
)

register(
    id="ptrl-tools-v0",
    entry_point="ptrl.envs.tools.gym_env:ToolsEnv",
)


