#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # Development mode
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "modupen.settings.dev")

    # Production mode
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "modupen.settings.prod")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
