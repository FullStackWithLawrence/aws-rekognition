# AWS Rekognition REST API

[![FullStackWithLawrence](https://a11ybadges.com/badge?text=FullStackWithLawrence&badgeColor=orange&logo=youtube&logoColor=282828)](https://www.youtube.com/@FullStackWithLawrence)<br>
[![Python](https://a11ybadges.com/badge?logo=python)](https://www.python.org/)
[![Amazon AWS](https://a11ybadges.com/badge?logo=amazonaws)](https://aws.amazon.com/)
[![Terraform](https://a11ybadges.com/badge?logo=terraform)](https://www.terraform.io/)<br>
[![12-Factor](https://img.shields.io/badge/12--Factor-Compliant-green.svg)](./doc/Twelve_Factor_Methodology.md)
[![Unit Tests](https://github.com/FullStackWithLawrence/aws-rekognition/actions/workflows/tests.yml/badge.svg)](https://github.com/FullStackWithLawrence/aws-rekognition/actions)
![GHA pushMain Status](https://img.shields.io/github/actions/workflow/status/FullStackWithLawrence/aws-rekognition/pushMain.yml?branch=main)
![Auto Assign](https://github.com/FullStackwithLawrence/aws-rekognition/actions/workflows/auto-assign.yml/badge.svg)[![Source
code](https://img.shields.io/static/v1?logo=github&label=Git&style=flat-square&color=orange&message=Source%20code)](https://github.com/FullStackWithLawrence/aws-rekognition)
[![Release Notes](https://img.shields.io/github/release/FullStackWithLawrence/aws-rekognition)](https://github.com/FullStackWithLawrence/aws-rekognition/releases)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![hack.d Lawrence McDaniel](https://img.shields.io/badge/hack.d-Lawrence%20McDaniel-orange.svg)](https://lawrencemcdaniel.com)

A facial recognition microservice built with AWS API Gateway, S3 and Python Lambda.

## Usage

1. Upload images that contain faces, and this microservice will index and database the facial recognition data in a fast, lightweight, searchable format.
2. Search for facial matches by uploading images to domain.com. Results are returns in JSON format.

## Quickstart Setup

1. Configure Terraform for your AWS account. Set these three values in [terraform.tfvars](./terraform/terraform.tfvars):

```terraform
account_id           = "012345678912"   # your 12-digit AWS account number
aws_region           = "us-east-1"      # an AWS data center
aws_profile          = "default"        # for aws cli credentials
```

2. base64 encode your image files

As a convenience, this repo includes a set of test data that has already been base64-encoded for you, located here: [test-data](./test-data/). It also includes this [base64encode.sh](./base64encode.sh) script that you can use to encode your own images, as per these examples.

```shell
./base64encode ImageWithFaces1.jpg
./base64encode ImageWithMoreFaces2.jpg
```

3. Index faces by uploading images to the `index` endpoint.

4. Search for indexed faces by uploading images to the `search` endpoint. Results are returned in JSON format. See [sample output](./doc/rekognition_search_output.json).

## API Key features

- Highly secure. Your OpenAI API key is stored in a local .env file, and is kept safe during development, build and deployment to production.
- Implements excellent [CloudWatch](https://aws.amazon.com/cloudwatch/) logs for Lambda as well as API Gateway
- Fully automated and [parameterized](./api/terraform/terraform.tfvars) Terraform build
- well documented code plus supplemental [documentation resources](./doc/) as well as detailed documentation on each [URL endpoint](./doc/examples/README.md).
- Low-cost [AWS serverless](https://aws.amazon.com/serverless/) implementation using [AWS API Gateway](https://aws.amazon.com/api-gateway/) and [AWS Lambda](https://aws.amazon.com/lambda/); free or nearly free in most cases
- Robust, performant and infinitely scalable
- Fast build time; usually less than 60 seconds to fully implement
- Deploy https to a custom domain
- Preconfigured [Postman](https://www.postman.com/) files for testing
- includes AWS API Gateway usage policy and api key
- Full CORS configuration

## Requirements

- [AWS account](https://aws.amazon.com/)
- [AWS Command Line Interface](https://aws.amazon.com/cli/)
- [Terraform](https://www.terraform.io/).
  _If you're new to Terraform then see [Getting Started With AWS and Terraform](./doc/terraform-getting-started.md)_
- [Python 3.11](https://www.python.org/downloads/): for creating virtual environment used for building AWS Lambda Layer, and locally by pre-commit linters and code formatters.
- [NodeJS](https://nodejs.org/en/download): used with NPM for local ReactJS developer environment, and for configuring/testing Semantic Release.

## Documentation

Please see this [detailed technical summary](./doc/REKOGNITION.md) of the architecture strategy for this solution. If you are new to Terraform and/or AWS then please read this [Getting Started Guide](./doc/TERRAFORM.md).

## Examples of Code Management Best Practices

This repo is referenced by multiple YouTube videos, including various tutorials about good coding practices and good code management. Of note:

### Automations

- [Automated Pull Requests](https://github.com/FullStackWithLawrence/aws-rekognition/pulls?q=is%3Apr+is%3Aclosed): Github Actions are triggered on pull requests to run any of several different kinds of technology-specific unit tests depending on the contents of the commits included in the PR.
- [python-dotenv](https://pypi.org/project/python-dotenv/) for storing sensitive data for local development
- [.gitignore](./.gitignore) ensures that no sensitive nor useless data accidentally gets pushed to GitHub.
- [tox.ini](./tox.ini) file for configuring behaviors of Python testing tools
- [GitHub Actions](https://github.com/features/actions) automates unit testing, semantic release rule checking, and dependabot actions.
- [GitHub Secrets](https://github.com/FullStackWithLawrence/aws-rekognition/settings/secrets/actions) to provide sensitive data to Github Actions workflows
- [GitHub Issues](https://github.com/features/issues)
- [Makefile](./Makefile) automates procedures like init, build, test, release and linting for Python, ReactJS and Terraform.
- [pre-commit](https://pre-commit.com/) automatically enforces a multitude of code quality, coding style and security policies.
- [Dependabot](https://github.com/dependabot) automatically updates the version pins of code library dependencies for Python, ReactJS and Terraform.
- [Unit Tests](https://docs.pytest.org/) are automated and can be invoked
  - manually from the command line
  - manually from GitHub Actions
  - automatically by Dependabot.
- [Mergify](https://mergify.com/) automates processing of bot-created pull requests
- [Semantic Release](https://github.com/semantic-release/semantic-release) automates version releases as well as maintains the change log for the repo.
- [Change Log](http://keepachangelog.com/)

### Linters and Formatters

Linters and formatters are tools used in programming to analyze and improve the quality of code. This project leverages several, including:

#### Code Formatting

- [Prettier](https://prettier.io/): an opinionated code formatter that supports many file formats and languages. This project leverages Prettier to standardize formatting of md, css, json, yml, js, jsx and Typescript files.
- [Black](https://github.com/psf/black): an opinionated code formatter for Python which is compatible with [PEP 8](https://peps.python.org/pep-0008/) and the [Python Style Guide](https://www.python.org/doc/essays/styleguide/).
- [isort](https://pycqa.github.io/isort/): a Python utility that sorts imports alphabetically, and automatically, separated into sections and by type.

#### Code Analysis

- [ESLint](https://eslint.org/): an open source project that helps you find and fix problems with your JavaScript and JSX code.
- [Flake8](https://flake8.pycqa.org/en/latest/): provides Python syntax checking, naming style enforcement, code style enforcement, and [cyclomatic complexity](https://en.wikipedia.org/wiki/Cyclomatic_complexity) analysis.
- [pylint](https://pypi.org/project/pylint/): a static code analyser for Python. It analyses your code without actually running it. It checks for errors, enforces a coding standard, looks for code smells, and can make suggestions about how the code could be refactored.
- [bandit](https://github.com/PyCQA/bandit): a tool designed to find common security issues in Python code.

#### Pre-commit hooks

- [pre-commit Hooks](https://pre-commit.com/hooks.html): scripts that run automatically before each commit is made to a repository, checking your code for embedded passwords, errors, issues, and any of a multitude of configurable policies that you can optionally enforce. They're part of the git hooks system, which allows you to trigger actions at certain points in git's execution. This project uses many Hooks. See [pre-commit-config.yaml](https://github.com/FullStackWithLawrence/aws-rekognition/blob/main/.pre-commit-config.yaml#L45).
- [codespell](https://github.com/codespell-project/codespell): fixes common misspellings in text files. It's designed primarily for checking misspelled words in source code, but it can be used with other files as well.

## Support

To get community support, go to the official [Issues Page](https://github.com/FullStackWithLawrence/aws-rekognition/issues) for this project.

## Contributing

We welcome contributions! There are a variety of ways for you to get involved, regardless of your background. In addition to Pull requests, this project would benefit from contributors focused on documentation and how-to video content creation, testing, community engagement, and stewards to help us to ensure that we comply with evolving standards for the ethical use of AI.

For developers, please see:

- the [Developer Setup Guide](./CONTRIBUTING.md)
- and these [commit comment guidelines](./doc/SEMANTIC_VERSIONING.md) 😬😬😬 for managing CI rules for automated semantic versioning.

You can also contact [Lawrence McDaniel](https://lawrencemcdaniel.com/contact) directly.
