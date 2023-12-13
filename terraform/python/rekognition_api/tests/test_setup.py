# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position
"""Test Search Lambda function."""

# python stuff
import json
import os
import sys


HERE = os.path.abspath(os.path.dirname(__file__))
PYTHON_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(PYTHON_ROOT)  # noqa: E402


def noop():
    """Test to ensure that test suite setup works and that lambda_handler is importable."""


def get_test_file(filename: str):
    """Load a mock lambda_index event."""
    event = None
    try:
        path1 = os.path.join(PYTHON_ROOT, "data", filename)
        with open(path1, "r", encoding="utf-8") as file:
            event = json.load(file)
    except FileNotFoundError:
        path2 = os.path.join(HERE, "data", filename)
        with open(path2, "r", encoding="utf-8") as file:
            event = json.load(file)

    return event
