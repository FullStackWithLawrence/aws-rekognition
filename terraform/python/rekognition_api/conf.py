# -*- coding: utf-8 -*-
# pylint: disable=no-member
"""Configuration for Lambda functions"""

import logging

# python stuff
import os  # library for interacting with the operating system
import platform  # library to view information about the server host this Lambda runs on
from typing import ClassVar, List

# 3rd party stuff
import boto3  # AWS SDK for Python https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
from pydantic import BaseModel, Field, ValidationError, validator

# our stuff
from .exceptions import RekognitionConfigurationError, RekognitionValueError


# Default values
# -----------------------------------------------------------------------------
class SettingsDefaults:
    """Default values for Settings"""

    AWS_REGION = "us-east-1"
    DEBUG_MODE = False
    TABLE_ID = "facialrecognition"
    COLLECTION_ID = TABLE_ID + "-collection"
    FACE_DETECT_MAX_FACES_COUNT = 10
    FACE_DETECT_THRESHOLD = 10
    FACE_DETECT_ATTRIBUTES = "DEFAULT"
    FACE_DETECT_QUALITY_FILTER = "AUTO"


ec2 = boto3.Session().client("ec2")
regions = ec2.describe_regions()
AWS_REGIONS = [region["RegionName"] for region in regions["Regions"]]


class Settings(BaseModel):
    """Settings for Lambda functions"""

    debug_mode: bool = Field(SettingsDefaults.DEBUG_MODE, env="DEBUG_MODE")
    aws_regions: List[str] = Field(AWS_REGIONS, description="The list of AWS regions")
    aws_region: str = Field(SettingsDefaults.AWS_REGION, env="AWS_REGION")
    table_id: str = Field(SettingsDefaults.TABLE_ID, env="TABLE_ID")
    collection_id: str = Field(SettingsDefaults.COLLECTION_ID, env="COLLECTION_ID")

    face_detect_max_faces_count: int = Field(
        SettingsDefaults.FACE_DETECT_MAX_FACES_COUNT, gt=0, env="FACE_DETECT_MAX_FACES_COUNT"
    )
    face_detect_attributes: str = Field(SettingsDefaults.FACE_DETECT_ATTRIBUTES, env="FACE_DETECT_ATTRIBUTES")
    face_detect_quality_filter: str = Field(
        SettingsDefaults.FACE_DETECT_QUALITY_FILTER, env="FACE_DETECT_QUALITY_FILTER"
    )
    face_detect_threshold: int = Field(SettingsDefaults.FACE_DETECT_THRESHOLD, gt=0, env="FACE_DETECT_THRESHOLD")

    # unvalidated settings
    s3_client: ClassVar = boto3.resource("s3")
    dynamodb_client: ClassVar = boto3.resource("dynamodb")
    dynamodb_table: ClassVar = dynamodb_client.Table(table_id)
    rekognition_client: ClassVar = boto3.client("rekognition")

    # use the boto3 library to initialize clients for the AWS services which we'll interact
    cloudwatch_dump: ClassVar = {
        "environment": {
            "os": os.name,
            "system": platform.system(),
            "release": platform.release(),
            "boto3": boto3.__version__,
            "COLLECTION_ID": collection_id,
            "TABLE_ID": table_id,
            "MAX_FACES": face_detect_max_faces_count,
            "FACE_DETECT_ATTRIBUTES": face_detect_attributes,
            "QUALITY_FILTER": face_detect_quality_filter,
            "DEBUG_MODE": debug_mode,
        }
    }

    class Config:
        """Pydantic configuration"""

        frozen = True

    @validator("aws_region")
    # pylint: disable=no-self-argument,unused-argument
    def validate_aws_region(cls, v, values, **kwargs):
        """Validate aws_region"""
        if "aws_regions" in values and v not in values["aws_regions"]:
            raise RekognitionValueError(f"aws_region {v} not in aws_regions")
        return v


settings = None
try:
    settings = Settings()
except ValidationError as e:
    raise RekognitionConfigurationError("Invalid configuration: " + str(e)) from e

logger = logging.getLogger(__name__)
logger.debug("DEBUG_MODE: %s", settings.debug_mode)
logger.debug("AWS_REGION: %s", settings.aws_region)
logger.debug("TABLE_ID: %s", settings.table_id)
logger.debug("COLLECTION_ID: %s", settings.collection_id)
logger.debug("FACE_DETECT_MAX_FACES_COUNT: %s", settings.face_detect_max_faces_count)
logger.debug("FACE_DETECT_ATTRIBUTES: %s", settings.face_detect_attributes)
logger.debug("FACE_DETECT_QUALITY_FILTER: %s", settings.face_detect_quality_filter)
logger.debug("FACE_DETECT_THRESHOLD: %s", settings.face_detect_threshold)
