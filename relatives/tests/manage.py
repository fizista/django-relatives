#!/usr/bin/env python

PROJEC_MODULE = 'przewodnik'


def main():
    import os
    import sys
    os.environ["DJANGO_SETTINGS_MODULE"] = "relatives.tests.settings"
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    import sys
    from os.path import join, realpath, dirname
    __dir__ = realpath(dirname(__file__))
    sys.path.insert(0, realpath(join(__dir__, '..')))
    sys.path.insert(0, realpath(join(__dir__, '..', '..')))
    # Normalize the path so as to eliminate errors due to the relative
    # references to modules.
    sys.path.remove(__dir__)  # FIX errors
    main()
