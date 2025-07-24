# --- User-Selectable Profiles ---
c.KubeSpawner.profile_list = [
    {
        "display_name": "Small Server (2G RAM, 1 CPU)",
        "default": True,
        "kubespawner_override": {
            "mem_limit": "2G",
            "mem_guarantee": "1G",
            "cpu_limit": 1,
            "cpu_guarantee": 0.5,
        },
    },
    {
        "display_name": "Medium Server (8G RAM, 2 CPU)",
        "kubespawner_override": {
            "mem_limit": "8G",
            "mem_guarantee": "4G",
            "cpu_limit": 2,
            "cpu_guarantee": 1,
        },
    },
    {
        "display_name": "Large Server (32G RAM, 4 CPU)",
        "kubespawner_override": {
            "mem_limit": "32G",
            "mem_guarantee": "16G",
            "cpu_limit": 4,
            "cpu_guarantee": 2,
        },
    },
]
