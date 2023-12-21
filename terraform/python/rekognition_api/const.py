# -*- coding: utf-8 -*-
# pylint: disable=E1101
"""A module containing constants for the OpenAI API."""
import os
from pathlib import Path

import hcl2
import requests


MODULE_NAME = "rekognition_api"
HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = str(Path(HERE).parent)
PYTHON_ROOT = str(Path(PROJECT_ROOT).parent)
TERRAFORM_ROOT = str(Path(PROJECT_ROOT).parent)
REPO_ROOT = str(Path(TERRAFORM_ROOT).parent)

TERRAFORM_TFVARS = os.path.join(TERRAFORM_ROOT, "terraform.tfvars")
TFVARS = {}
IS_USING_TFVARS = False


def read_file_from_github(repo_owner, repo_name, file_path):
    """For prod. Read a file from a GitHub repository."""
    base_url = "https://raw.githubusercontent.com"
    url = f"{base_url}/{repo_owner}/{repo_name}/main/{file_path}"
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        return response.text
    return None


try:
    with open(TERRAFORM_TFVARS, "r", encoding="utf-8") as f:
        TFVARS = hcl2.load(f)
    IS_USING_TFVARS = True
except FileNotFoundError:
    tfvars = read_file_from_github(
        repo_owner="FullStackWithLawrence", repo_name="aws-rekognition", file_path="terraform/terraform.tfvars"
    )
    TFVARS = hcl2.loads(tfvars)
    IS_USING_TFVARS = True
