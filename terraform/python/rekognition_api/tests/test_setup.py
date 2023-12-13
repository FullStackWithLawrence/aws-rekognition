# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position
"""Test Search Lambda function."""

# python stuff
import os
import sys


HERE = os.path.abspath(os.path.dirname(__file__))
PYTHON_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(PYTHON_ROOT)  # noqa: E402


def noop():
    """Test to ensure that test suite setup works and that lambda_handler is importable."""
