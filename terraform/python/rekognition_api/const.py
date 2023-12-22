# -*- coding: utf-8 -*-
# pylint: disable=E1101
"""A module containing constants for the OpenAI API."""
import logging
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
if not os.path.exists(TERRAFORM_TFVARS):
    TERRAFORM_TFVARS = os.path.join(HERE, "terraform.tfvars")

TFVARS = {}
IS_USING_TFVARS = False

logger = logging.getLogger(__name__)

# def read_file_from_github(repo_owner, repo_name, file_path):
#     """For prod. Read a file from a GitHub repository."""
#     base_url = "https://raw.githubusercontent.com"
#     url = f"{base_url}/{repo_owner}/{repo_name}/main/{file_path}"
#     response = requests.get(url, timeout=5)
#     if response.status_code == 200:
#         return response.text
#     return None

with open(TERRAFORM_TFVARS, "r", encoding="utf-8") as f:
    TFVARS = hcl2.load(f)

try:
    with open(TERRAFORM_TFVARS, "r", encoding="utf-8") as f:
        TFVARS = hcl2.load(f)
    IS_USING_TFVARS = True
except FileNotFoundError:
    logger.warning("No terraform.tfvars file found. Using default values.")
