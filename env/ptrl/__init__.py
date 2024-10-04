from gymnasium.envs.registration import register


register(
    id="ptrl-fms-v0",
    entry_point="ptrl.envs.fms.gym_env:FmsEnv",
    )
