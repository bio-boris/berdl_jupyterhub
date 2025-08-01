import json
import os
import logging
from pathlib import Path
import json5
from fasteners import InterProcessLock


log = logging.getLogger(__name__)


def setup_bashrc(username: str) -> None:
    """

    Args:
        username:

    Returns:

    """


def setup_jupyterai_extension(username: str) -> None:
    """
    Creates a default Jupyter AI config file for the user if one does not
    already exist. This prevents overwriting user customizations.
    """
    try:
        ai_config_path = Path(f"/home/{username}/.jupyter/jupyter_ai_config.json")

        if not ai_config_path.exists():
            ai_config_path.parent.mkdir(parents=True, exist_ok=True)

            default_config = {
                "AiExtension": {
                    "allowed_providers": [
                        "openai",
                        "openai-chat",
                        "anthropic",
                        "anthropic-chat",
                        "cborg",
                        "ollama",
                    ]
                }
            }

            with open(ai_config_path, "w") as f:
                json.dump(default_config, f, indent=4)

    except Exception as e:
        # Instead of printing, log the error. This is much better practice.
        log.error(
            f"Error setting up Jupyter AI extension for {username}: {e}", exc_info=True
        )


def setup_favorites_extension(
    username: str, user_dir: Path, favorites_paths: list[Path]
) -> None:
    """
    Safely adds default directories to the JupyterLab favorites extension.
    Uses a kernel-level lock to prevent race conditions and handle crashes.
    """
    try:
        settings_path = (
            user_dir
            / ".jupyter"
            / "lab"
            / "user-settings"
            / "@jlab-enhanced"
            / "favorites"
            / "favorites.jupyterlab-settings"
        )
        settings_path.parent.mkdir(parents=True, exist_ok=True)

        lock_path = settings_path.with_suffix(".jupyterlab-settings.lock")
        lock = InterProcessLock(str(lock_path))

        with lock:
            if settings_path.exists():
                with open(settings_path, "r") as f:
                    config = json5.load(f)
            else:
                config = {"favorites": []}

            existing_fav_set = {
                (fav["root"], fav["path"]) for fav in config.get("favorites", [])
            }

            for fav_path in favorites_paths:
                if not fav_path.is_dir():
                    log.warning(
                        f"Favorite path {fav_path} is not a directory. Skipping."
                    )
                    continue

                root_str = "/"
                path_str = str(fav_path.relative_to(root_str))

                if (root_str, path_str) not in existing_fav_set:
                    config["favorites"].append(
                        {
                            "root": root_str,
                            "path": path_str,
                            "contentType": "directory",
                            "iconLabel": "ui-components:folder",
                            "name": "$HOME" if fav_path == user_dir else fav_path.name,
                        }
                    )

            with open(settings_path, "w") as f:
                json5.dump(config, f, indent=2)

    except Exception as e:
        log.error(f"Error setting up favorites for {username}: {e}", exc_info=True)


def setup_user_environment(username: str) -> None:
    """
    Main function to orchestrate the setup of all user-specific extensions
    and configurations.
    """
    user_home_dir = Path(f"/home/{username}")
    if not user_home_dir.exists():
        log.error(
            f"User home directory {user_home_dir} does not exist. Aborting setup."
        )
        return

    default_favorites = [
        user_home_dir,
        Path("/global_share"),
    ]

    setup_favorites_extension(username, user_home_dir, default_favorites)
    setup_jupyterai_extension(username)
