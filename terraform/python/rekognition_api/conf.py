# -*- coding: utf-8 -*-
# pylint: disable=no-member
"""
Configuration for Lambda functions.

This module is used to configure the Lambda functions. It uses the pydantic_settings
library to validate the configuration values. The configuration values are read from
environment variables, or alternatively these can be set when instantiating Settings().
"""

import importlib.util
import logging

# python stuff
import os  # library for interacting with the operating system
import platform  # library to view information about the server host this Lambda runs on
import re
from typing import Any, Dict, List, Optional

# 3rd party stuff
import boto3  # AWS SDK for Python https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
from dotenv import load_dotenv
from pydantic import Field, ValidationError, ValidationInfo, field_validator
from pydantic_settings import BaseSettings
from rekognition_api.const import HERE, IS_USING_TFVARS, TFVARS

# our stuff
from rekognition_api.exceptions import (
    RekognitionConfigurationError,
    RekognitionValueError,
)


DOT_ENV_LOADED = load_dotenv()


def load_version() -> Dict[str, str]:
    """Stringify the __version__ module."""
    version_file_path = os.path.join(HERE, "__version__.py")
    spec = importlib.util.spec_from_file_location("__version__", version_file_path)
    version_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(version_module)
    return version_module.__dict__


VERSION = load_version()


def get_semantic_version() -> str:
    """
    Return the semantic version number.

    Example valid values of __version__.py are:
    0.1.17
    0.1.17-next.1
    0.1.17-next.2
    0.1.17-next.123456
    0.1.17-next-major.1
    0.1.17-next-major.2
    0.1.17-next-major.123456

    Note:
    - pypi does not allow semantic version numbers to contain a dash.
    - pypi does not allow semantic version numbers to contain a 'v' prefix.
    - pypi does not allow semantic version numbers to contain a 'next' suffix.
    """
    version = VERSION["__version__"]
    version = re.sub(r"-next\.\d+", "", version)
    return re.sub(r"-next-major\.\d+", "", version)


class SettingsDefaults:
    """Default values for Settings"""

    AWS_PROFILE = TFVARS.get("aws_profile", None)
    DUMP_DEFAULTS = TFVARS.get("dump_defaults", False)
    AWS_REGION = TFVARS.get("aws_region", "us-east-1")
    DEBUG_MODE: bool = bool(TFVARS.get("debug_mode", False))
    SHARED_RESOURCE_IDENTIFIER = TFVARS.get("shared_resource_identifier", "rekognition_api")

    AWS_DYNAMODB_TABLE_ID = "rekognition"

    AWS_REKOGNITION_COLLECTION_ID = AWS_DYNAMODB_TABLE_ID + "-collection"
    AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT: int = int(TFVARS.get("aws_rekognition_max_faces_count", 10))
    AWS_REKOGNITION_FACE_DETECT_THRESHOLD: int = int(TFVARS.get("aws_rekognition_face_detect_threshold", 10))
    AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES = TFVARS.get("aws_rekognition_face_detect_attributes", "DEFAULT")
    AWS_REKOGNITION_FACE_DETECT_QUALITY_FILTER = TFVARS.get("aws_rekognition_face_detect_quality_filter", "AUTO")

    @classmethod
    def to_dict(cls):
        """Convert SettingsDefaults to dict"""
        return {
            key: value
            for key, value in SettingsDefaults.__dict__.items()
            if not key.startswith("__") and not callable(key) and key != "to_dict"
        }


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


# pylint: disable=too-many-public-methods
class Settings(BaseSettings):
    """Settings for Lambda functions"""

    _aws_session: boto3.Session = None
    _dump: dict = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._initialized = True

    debug_mode: Optional[bool] = Field(
        SettingsDefaults.DEBUG_MODE,
        env="DEBUG_MODE",
        pre=True,
        getter=lambda v: empty_str_to_bool_default(v, SettingsDefaults.DEBUG_MODE),
    )
    dump_defaults: Optional[bool] = Field(
        SettingsDefaults.DUMP_DEFAULTS,
        env="DUMP_DEFAULTS",
        pre=True,
        getter=lambda v: empty_str_to_bool_default(v, SettingsDefaults.DUMP_DEFAULTS),
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
    aws_dynamodb_table_id: Optional[str] = Field(
        SettingsDefaults.AWS_DYNAMODB_TABLE_ID,
        env="AWS_DYNAMODB_TABLE_ID",
    )
    aws_rekognition_collection_id: Optional[str] = Field(
        SettingsDefaults.AWS_REKOGNITION_COLLECTION_ID,
        env="AWS_REKOGNITION_COLLECTION_ID",
    )

    aws_rekognition_face_detect_attributes: Optional[str] = Field(
        SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES,
        env="AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES",
    )
    aws_rekognition_face_detect_quality_filter: Optional[str] = Field(
        SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_QUALITY_FILTER,
        env="AWS_REKOGNITION_FACE_DETECT_QUALITY_FILTER",
    )
    aws_rekognition_face_detect_max_faces_count: Optional[int] = Field(
        SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT,
        gt=0,
        env="AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT",
        pre=True,
        getter=lambda v: empty_str_to_int_default(v, SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT),
    )
    aws_rekognition_face_detect_threshold: Optional[int] = Field(
        SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_THRESHOLD,
        gt=0,
        env="AWS_REKOGNITION_FACE_DETECT_THRESHOLD",
        pre=True,
        getter=lambda v: empty_str_to_int_default(v, SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_THRESHOLD),
    )
    shared_resource_identifier: Optional[str] = Field(
        SettingsDefaults.SHARED_RESOURCE_IDENTIFIER, env="SHARED_RESOURCE_IDENTIFIER"
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
        return self.dynamodb_client.Table(self.aws_dynamodb_table_id)

    @property
    def is_using_dotenv_file(self) -> bool:
        """Is the dotenv file being used?"""
        return DOT_ENV_LOADED

    @property
    def environment_variables(self) -> List[str]:
        """Environment variables"""
        return list(os.environ.keys())

    @property
    def is_using_tfvars_file(self) -> bool:
        """Is the tfvars file being used?"""
        return IS_USING_TFVARS

    @property
    def tfvars_variables(self) -> List[str]:
        """Terraform variables"""
        return list(TFVARS.keys())

    @property
    def is_using_aws_rekognition(self) -> bool:
        """Future: Is the AWS Rekognition service being used?"""
        return True

    @property
    def is_using_aws_dynamodb(self) -> bool:
        """Future: Is the AWS DynamoDB service being used?"""
        return True

    @property
    def version(self) -> str:
        """OpenAI API version"""
        return get_semantic_version()

    @property
    def dump(self) -> dict:
        """Dump all settings."""

        def recursive_sort_dict(d):
            return {k: recursive_sort_dict(v) if isinstance(v, dict) else v for k, v in sorted(d.items())}

        if self._dump and self._initialized:
            return self._dump

        self._dump = {
            "secrets": {},
            "environment": {
                "is_using_tfvars_file": self.is_using_tfvars_file,
                "is_using_dotenv_file": self.is_using_dotenv_file,
                "is_using_aws_rekognition": self.is_using_aws_rekognition,
                "is_using_aws_dynamodb": self.is_using_aws_dynamodb,
                "os": os.name,
                "system": platform.system(),
                "release": platform.release(),
                "boto3": boto3.__version__,
                "shared_resource_identifier": self.shared_resource_identifier,
                "debug_mode": self.debug_mode,
                "dump_defaults": self.dump_defaults,
                "version": self.version,
            },
            "aws": {
                "profile": self.aws_profile,
                "region": self.aws_region,
            },
            "rekognition": {
                "aws_rekognition_collection_id": self.aws_rekognition_collection_id,
                "aws_dynamodb_table_id": self.aws_dynamodb_table_id,
                "aws_rekognition_face_detect_max_faces_count": self.aws_rekognition_face_detect_max_faces_count,
                "aws_rekognition_face_detect_attributes": self.aws_rekognition_face_detect_attributes,
                "aws_rekognition_face_detect_quality_filter": self.aws_rekognition_face_detect_quality_filter,
                "aws_rekognition_face_detect_threshold": self.aws_rekognition_face_detect_threshold,
            },
            "dynamodb": {
                "table": self.aws_dynamodb_table_id,
            },
        }
        if self.dump_defaults:
            settings_defaults = SettingsDefaults.to_dict()
            self._dump["settings_defaults"] = settings_defaults

        if self.is_using_dotenv_file:
            self._dump["environment"]["dotenv"] = self.environment_variables

        if self.is_using_tfvars_file:
            self._dump["environment"]["tfvars"] = self.tfvars_variables

        self._dump = recursive_sort_dict(self._dump)
        return self._dump

    class Config:
        """Pydantic configuration"""

        frozen = True

    @field_validator("shared_resource_identifier")
    def validate_shared_resource_identifier(cls, v) -> str:
        """Validate shared_resource_identifier"""
        if v in [None, ""]:
            return SettingsDefaults.SHARED_RESOURCE_IDENTIFIER
        return v

    @field_validator("aws_profile")
    # pylint: disable=no-self-argument,unused-argument
    def validate_aws_profile(cls, v, values, **kwargs) -> str:
        """Validate aws_profile"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_PROFILE
        return v

    @field_validator("aws_region")
    # pylint: disable=no-self-argument,unused-argument
    def validate_aws_region(cls, v, values: ValidationInfo, **kwargs) -> str:
        """Validate aws_region"""
        valid_regions = values.data.get("aws_regions", [])
        if v in [None, ""]:
            return SettingsDefaults.AWS_REGION
        if v not in valid_regions:
            raise RekognitionValueError(f"aws_region {v} not in aws_regions")
        return v

    @field_validator("aws_dynamodb_table_id")
    def validate_table_id(cls, v) -> str:
        """Validate aws_dynamodb_table_id"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_DYNAMODB_TABLE_ID
        return v

    @field_validator("aws_rekognition_collection_id")
    def validate_collection_id(cls, v) -> str:
        """Validate aws_rekognition_collection_id"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_REKOGNITION_COLLECTION_ID
        return v

    @field_validator("aws_rekognition_face_detect_attributes")
    def validate_face_detect_attributes(cls, v) -> str:
        """Validate aws_rekognition_face_detect_attributes"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES
        return v

    @field_validator("debug_mode")
    def parse_debug_mode(cls, v) -> bool:
        """Parse debug_mode"""
        if isinstance(v, bool):
            return v
        if v in [None, ""]:
            return SettingsDefaults.DEBUG_MODE
        return v.lower() in ["true", "1", "t", "y", "yes"]

    @field_validator("dump_defaults")
    def parse_dump_defaults(cls, v) -> bool:
        """Parse dump_defaults"""
        if isinstance(v, bool):
            return v
        if v in [None, ""]:
            return SettingsDefaults.DUMP_DEFAULTS
        return v.lower() in ["true", "1", "t", "y", "yes"]

    @field_validator("aws_rekognition_face_detect_max_faces_count")
    def check_aws_rekognition_face_detect_max_faces_count(cls, v) -> int:
        """Check aws_rekognition_face_detect_max_faces_count"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT
        return int(v)

    @field_validator("aws_rekognition_face_detect_threshold")
    def check_face_detect_threshold(cls, v) -> int:
        """Check aws_rekognition_face_detect_threshold"""
        if isinstance(v, int):
            return v
        if v in [None, ""]:
            return SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_THRESHOLD
        return int(v)


settings = None
try:
    settings = Settings()
except ValidationError as e:
    raise RekognitionConfigurationError("Invalid configuration: " + str(e)) from e
