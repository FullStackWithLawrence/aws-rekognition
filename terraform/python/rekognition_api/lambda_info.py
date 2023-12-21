# -*- coding: utf-8 -*-
# pylint: disable=R0911,R0912,W0718
"""Lambda entry point for rekognition_api/info"""

from rekognition_api.aws import aws_infrastructure_config as aws_config
from rekognition_api.common import http_response_factory
from rekognition_api.conf import settings


# pylint: disable=unused-argument
def lambda_handler(event, context):  # noqa: C901
    """Lambda entry point"""
    info = {
        "aws_infrastructure": aws_config.dump,
        "settings": settings.dump,
    }
    return http_response_factory(status_code=200, body=info)
