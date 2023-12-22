# -*- coding: utf-8 -*-
"""Common functions for Lambda functions"""
import datetime
import json
import sys
import traceback

from rekognition_api.conf import settings


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d")

        return super().default(o)


def cloudwatch_handler(event, quiet: bool = False):
    """Create a CloudWatch log entry for the event and dump the event to stdout."""
    if settings.debug_mode and not quiet:
        print(json.dumps(settings.dump, cls=DateTimeEncoder))
        print(json.dumps({"event": event}, cls=DateTimeEncoder))


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
        print(json.dumps({"retval": retval}, cls=DateTimeEncoder))

    # see https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
    retval = {
        "isBase64Encoded": False,
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, cls=DateTimeEncoder),
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


def recursive_sort_dict(d):
    """Recursively sort a dictionary by key."""
    return {k: recursive_sort_dict(v) if isinstance(v, dict) else v for k, v in sorted(d.items())}
