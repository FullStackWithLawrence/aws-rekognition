# -*- coding: utf-8 -*-
# pylint: disable=no-member
"""
Configuration for Lambda functions.

This module is used to configure the Lambda functions. It uses the pydantic_settings
library to validate the configuration values. The configuration values are read from
environment variables, or alternatively these can be set when instantiating Settings().
"""

import logging

# python stuff
import os  # library for interacting with the operating system
import platform  # library to view information about the server host this Lambda runs on
from typing import ClassVar, List, Optional

# 3rd party stuff
import boto3  # AWS SDK for Python https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
from pydantic import Field, ValidationError, validator
from pydantic_settings import BaseSettings

# our stuff
from rekognition_api.exceptions import (
    RekognitionConfigurationError,
    RekognitionValueError,
)


# Default values
# -----------------------------------------------------------------------------
class SettingsDefaults:
    """Default values for Settings"""

    AWS_PROFILE = None
    AWS_REGION = "us-east-1"
    DEBUG_MODE = False
    TABLE_ID = "rekognition"
    COLLECTION_ID = TABLE_ID + "-collection"
    FACE_DETECT_MAX_FACES_COUNT = 10
    FACE_DETECT_THRESHOLD = 10
    FACE_DETECT_ATTRIBUTES = "DEFAULT"
    FACE_DETECT_QUALITY_FILTER = "AUTO"


ec2 = boto3.Session().client("ec2")
regions = ec2.describe_regions()
AWS_REGIONS = [region["RegionName"] for region in regions["Regions"]]


def empty_str_to_bool_default(v: str, default: bool) -> bool:
    """Convert empty string to default boolean value"""
    if v in [None, ""]:
        return default
    return v.lower() in ["true", "1", "t", "y", "yes"]


def empty_str_to_int_default(v: str, default: int) -> int:
    """Convert empty string to default integer value"""
    if v in [None, ""]:
        return default
    try:
        return int(v)
    except ValueError:
        return default


class Settings(BaseSettings):
    """Settings for Lambda functions"""

    _aws_session: boto3.Session = None

    debug_mode: Optional[bool] = Field(
        SettingsDefaults.DEBUG_MODE,
        env="DEBUG_MODE",
        pre=True,
        getter=lambda v: empty_str_to_bool_default(v, SettingsDefaults.DEBUG_MODE),
    )
    aws_profile: Optional[str] = Field(
        SettingsDefaults.AWS_PROFILE,
        env="AWS_PROFILE",
    )
    aws_regions: Optional[List[str]] = Field(AWS_REGIONS, description="The list of AWS regions")
    aws_region: Optional[str] = Field(
        SettingsDefaults.AWS_REGION,
        env="AWS_REGION",
    )
    table_id: Optional[str] = Field(
        SettingsDefaults.TABLE_ID,
        env="TABLE_ID",
    )
    collection_id: Optional[str] = Field(
        SettingsDefaults.COLLECTION_ID,
        env="COLLECTION_ID",
    )

    face_detect_attributes: Optional[str] = Field(
        SettingsDefaults.FACE_DETECT_ATTRIBUTES,
        env="FACE_DETECT_ATTRIBUTES",
    )
    face_detect_quality_filter: Optional[str] = Field(
        SettingsDefaults.FACE_DETECT_QUALITY_FILTER,
        env="FACE_DETECT_QUALITY_FILTER",
    )
    face_detect_max_faces_count: Optional[int] = Field(
        SettingsDefaults.FACE_DETECT_MAX_FACES_COUNT,
        gt=0,
        env="FACE_DETECT_MAX_FACES_COUNT",
        pre=True,
        getter=lambda v: empty_str_to_int_default(v, SettingsDefaults.FACE_DETECT_MAX_FACES_COUNT),
    )
    face_detect_threshold: Optional[int] = Field(
        SettingsDefaults.FACE_DETECT_THRESHOLD,
        gt=0,
        env="FACE_DETECT_THRESHOLD",
        pre=True,
        getter=lambda v: empty_str_to_int_default(v, SettingsDefaults.FACE_DETECT_THRESHOLD),
    )

    @property
    def aws_session(self):
        """AWS session"""
        if not self._aws_session:
            if self.aws_profile:
                self._aws_session = boto3.Session(profile_name=self.aws_profile, region_name=self.aws_region)
            else:
                self._aws_session = boto3.Session(region_name=self.aws_region)
        return self._aws_session

    @property
    def s3_client(self):
        """S3 client"""
        return self.aws_session.resource("s3")

    @property
    def dynamodb_client(self):
        """DynamoDB client"""
        return self.aws_session.resource("dynamodb")

    @property
    def rekognition_client(self):
        """Rekognition client"""
        return self.aws_session.client("rekognition")

    @property
    def dynamodb_table(self):
        """DynamoDB table"""
        return self.dynamodb_client.Table(self.table_id)

    # use the boto3 library to initialize clients for the AWS services which we'll interact
    @property
    def cloudwatch_dump(self):
        """Dump settings to CloudWatch"""
        return {
            "environment": {
                "os": os.name,
                "system": platform.system(),
                "release": platform.release(),
                "boto3": boto3.__version__,
                "COLLECTION_ID": self.collection_id,
                "TABLE_ID": self.table_id,
                "MAX_FACES": self.face_detect_max_faces_count,
                "FACE_DETECT_ATTRIBUTES": self.face_detect_attributes,
                "QUALITY_FILTER": self.face_detect_quality_filter,
                "DEBUG_MODE": self.debug_mode,
            }
        }

    class Config:
        """Pydantic configuration"""

        frozen = True

    @validator("aws_profile", pre=True)
    # pylint: disable=no-self-argument,unused-argument
    def validate_aws_profile(cls, v, values, **kwargs):
        """Validate aws_profile"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_PROFILE
        return v

    @validator("aws_region", pre=True)
    # pylint: disable=no-self-argument,unused-argument
    def validate_aws_region(cls, v, values, **kwargs):
        """Validate aws_region"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_REGION
        if "aws_regions" in values and v not in values["aws_regions"]:
            raise RekognitionValueError(f"aws_region {v} not in aws_regions")
        return v

    @validator("table_id", pre=True)
    def validate_table_id(cls, v):
        """Validate table_id"""
        if v in [None, ""]:
            return SettingsDefaults.TABLE_ID
        return v

    @validator("collection_id", pre=True)
    def validate_collection_id(cls, v):
        """Validate collection_id"""
        if v in [None, ""]:
            return SettingsDefaults.COLLECTION_ID
        return v

    @validator("face_detect_attributes", pre=True)
    def validate_face_detect_attributes(cls, v):
        """Validate face_detect_attributes"""
        if v in [None, ""]:
            return SettingsDefaults.FACE_DETECT_ATTRIBUTES
        return v

    @validator("debug_mode", pre=True)
    def parse_debug_mode(cls, v):
        """Parse debug_mode"""
        if isinstance(v, bool):
            return v
        if v in [None, ""]:
            return SettingsDefaults.DEBUG_MODE
        return v.lower() in ["true", "1", "t", "y", "yes"]

    @validator("face_detect_max_faces_count", pre=True)
    def check_face_detect_max_faces_count(cls, v):
        """Check face_detect_max_faces_count"""
        if v in [None, ""]:
            return SettingsDefaults.FACE_DETECT_MAX_FACES_COUNT
        return int(v)

    @validator("face_detect_threshold", pre=True)
    def check_face_detect_threshold(cls, v):
        """Check face_detect_threshold"""
        if isinstance(v, int):
            return v
        if v in [None, ""]:
            return SettingsDefaults.FACE_DETECT_THRESHOLD
        return int(v)


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
