import os
import platform

from infrastructure.observability.logger import Logger


def is_dev_mode() -> bool:
    """True when running on macOS (development machine)."""
    return platform.system() == 'Darwin'


def get_env(key: str, default=None):
    """
    Read env var safely.
    - Returns the value if set.
    - Returns `default` (which may be None) if missing.
    - Logs a warning if missing AND not in dev mode (production should have all vars set).
    """
    raw = os.environ.get(key)

    if raw is None and not is_dev_mode():
        Logger.get_logger().warning(f"env var ausente: {key}")

    return raw if raw is not None else default
