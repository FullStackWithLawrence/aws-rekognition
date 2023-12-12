# -*- coding: utf-8 -*-
"""Module exceptions.py"""


from .conf import settings


EXCEPTION_MAP = {
    settings.rekognition_client.exceptions.ThrottlingException: (401, "InvalidParameterException"),
    settings.rekognition_client.exceptions.ProvisionedThroughputExceededException: (401, "InvalidParameterException"),
    settings.rekognition_client.exceptions.ServiceQuotaExceededException: (401, "InvalidParameterException"),
    settings.rekognition_client.exceptions.AccessDeniedException: (403, "AccessDeniedException"),
    settings.rekognition_client.exceptions.ResourceNotFoundException: (404, "ResourceNotFoundException"),
    settings.rekognition_client.exceptions.InvalidS3ObjectException: (406, "InvalidS3ObjectException"),
    settings.rekognition_client.exceptions.ImageTooLargeException: (406, "ImageTooLargeException"),
    settings.rekognition_client.exceptions.InvalidImageFormatException: (406, "InvalidImageFormatException"),
    settings.rekognition_client.exceptions.InternalServerError: (500, "InternalServerError"),
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
