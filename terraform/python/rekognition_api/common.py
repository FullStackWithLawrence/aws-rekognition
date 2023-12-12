# -*- coding: utf-8 -*-
"""Common functions for Lambda functions"""
import json
import sys
import traceback

from .conf import settings


def http_response_factory(status_code: int, body: json) -> json:
    """
    Generate a standardized JSON return dictionary for all possible response scenarios.

    status_code: an HTTP response code. see https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
    body: a JSON dict of Rekognition results for status 200, an error dict otherwise.

    see https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html
    """
    if status_code < 100 or status_code > 599:
        raise ValueError(f"Invalid HTTP response code received: {status_code}")

    if settings.debug_mode:
        retval = {
            "isBase64Encoded": False,
            "statusCode": status_code,
            "headers": {"Content-Type": "application/json"},
            "body": body,
        }
        # log our output to the CloudWatch log for this Lambda
        print(json.dumps({"retval": retval}))

    # see https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
    retval = {
        "isBase64Encoded": False,
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }

    return retval


def exception_response_factory(exception) -> json:
    """
    Generate a standardized error response dictionary that includes
    the Python exception type and stack trace.

    exception: a descendant of Python Exception class
    """
    exc_info = sys.exc_info()
    retval = {
        "error": str(exception),
        "description": "".join(traceback.format_exception(*exc_info)),
    }

    return retval
