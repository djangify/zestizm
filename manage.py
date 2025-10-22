#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Add this section to load .env file
import environ

env = environ.Env()
# Get the base directory
BASE_DIR = Path(__file__).resolve().parent
# Read the .env file
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zestizm.settings.local")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
