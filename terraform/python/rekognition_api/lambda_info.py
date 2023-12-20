# -*- coding: utf-8 -*-
# pylint: disable=R0911,R0912,W0718
"""Lambda entry point for rekognition_api/info"""

# python stuff
import logging  # library for interacting with application log data

# our stuff
from rekognition_api.common import http_response_factory
from rekognition_api.conf import settings


# pylint: disable=unused-argument
def lambda_handler(event, context):  # noqa: C901
    """Lambda entry point"""

    return http_response_factory(status_code=200, body=settings.dump)
