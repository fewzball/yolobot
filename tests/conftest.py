# -*- coding: utf-8 -*-
"""
This module contains our testing hooks.
"""


def pytest_configure():
    """Sets the path so we don't have to set it in every single test file.
    This assumes that the tests are being run from the root directory."""
    import os
    import sys
    sys.path.append(os.getcwd())
