# config/network.py - Practical example
def configure_network(c):
    """Configure network settings with security in mind."""

    # Add labels for network policy targeting
    c.KubeSpawner.extra_labels.update(
        {
            "notebook-user": "{username}",  # For per-user policies
            "network-policy": "restricted",
        }
    )

    # You might want different policies for different profiles
    for profile in c.KubeSpawner.profile_list:
        if "Large Server" in profile["display_name"]:
            # Data science profile might need more access
            profile["kubespawner_override"]["extra_labels"] = {
                "network-policy": "data-science"
            }
