# -*- coding: utf-8 -*-
# pylint: disable=E1101
"""A module containing constants for the OpenAI API."""
import os
from pathlib import Path

import hcl2


MODULE_NAME = "rekognition_api"
HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = str(Path(HERE).parent)
PYTHON_ROOT = str(Path(PROJECT_ROOT).parent)
TERRAFORM_ROOT = str(Path(PROJECT_ROOT).parent)
REPO_ROOT = str(Path(TERRAFORM_ROOT).parent)
TERRAFORM_TFVARS = os.path.join(TERRAFORM_ROOT, "terraform.tfvars")
TFVARS = {}
IS_USING_TFVARS = False

try:
    with open(TERRAFORM_TFVARS, "r", encoding="utf-8") as f:
        TFVARS = hcl2.load(f)
    IS_USING_TFVARS = True
except FileNotFoundError:
    pass
