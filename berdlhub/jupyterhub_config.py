"""Main JupyterHub configuration file.

This file orchestrates loading all configuration modules.
"""

import os
import sys

# Add config directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Get the config object
c = get_config()

# Validate environment variables first
from validators import validate_environment

validate_environment()

# Load all configuration modules in order
from berdlhub.config.hub import configure_hub
from berdlhub.config.auth import configure_auth
from berdlhub.config.spawner import configure_spawner
from berdlhub.config.profiles import configure_profiles
from berdlhub.config.storage import configure_hostpath_storage
from berdlhub.config.resources import configure_resources
from berdlhub.config.environment import configure_environment
from berdlhub.config.services import configure_services
from berdlhub.config.debug import configure_debug
from berdlhub.config.hooks import configure_hooks

# Apply configurations in dependency order
configure_hub(c)
configure_auth(c)
configure_spawner(c)
configure_environment(c)
configure_resources(c)
configure_hostpath_storage(c)
configure_profiles(c)
configure_services(c)
configure_hooks(c)


# Apply debug last (can override other settings)
configure_debug(c)

