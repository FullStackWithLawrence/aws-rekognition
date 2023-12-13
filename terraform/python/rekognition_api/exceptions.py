# -*- coding: utf-8 -*-
"""Module exceptions.py"""

import boto3


rekognition_client = boto3.client("rekognition")

EXCEPTION_MAP = {
    rekognition_client.exceptions.ThrottlingException: (401, "InvalidParameterException"),
    rekognition_client.exceptions.ProvisionedThroughputExceededException: (401, "InvalidParameterException"),
    rekognition_client.exceptions.ServiceQuotaExceededException: (401, "InvalidParameterException"),
    rekognition_client.exceptions.AccessDeniedException: (403, "AccessDeniedException"),
    rekognition_client.exceptions.ResourceNotFoundException: (404, "ResourceNotFoundException"),
    rekognition_client.exceptions.InvalidS3ObjectException: (406, "InvalidS3ObjectException"),
    rekognition_client.exceptions.ImageTooLargeException: (406, "ImageTooLargeException"),
    rekognition_client.exceptions.InvalidImageFormatException: (406, "InvalidImageFormatException"),
    rekognition_client.exceptions.InternalServerError: (500, "InternalServerError"),
    Exception: (500, "InternalServerError"),
}


class RekognitionConfigurationError(Exception):
    """Exception raised for errors in the configuration."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class RekognitionValueError(Exception):
    """Exception raised for errors in the configuration."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class RekognitionIlligalInvocationError(Exception):
    """Exception raised when the service is called by an unknown service."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
