# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position
"""Test Search Lambda function."""

# python stuff
import json
import os
import sys


HERE = os.path.abspath(os.path.dirname(__file__))
PYTHON_ROOT = os.path.dirname(HERE)
sys.path.append(PYTHON_ROOT)  # noqa: E402


def noop():
    """Test to ensure that test suite setup works and that lambda_handler is importable."""


def get_test_file(filename: str):
    """Load a mock lambda_index event."""
    path = os.path.join(HERE, "mock_data", filename)
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)
