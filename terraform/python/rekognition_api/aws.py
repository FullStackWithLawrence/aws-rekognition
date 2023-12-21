# -*- coding: utf-8 -*-
"""A utility class for introspecting AWS infrastructure."""

# python stuff
import json
import socket

# our stuff
from rekognition_api.conf import settings


class AWSInfrastructureConfig:
    """AWS Infrastructure Config"""

    @property
    def dump(self):
        """Return a dict of the AWS infrastructure config."""
        return {
            "aws_apigateway": {
                "api_id": self.get_api(settings.aws_apigateway_name)["id"],
            },
            "aws_dynamodb": {
                "table_name": self.get_dyanmodb_table_by_name(
                    settings.aws_dynamodb_table_id,
                )
            },
            "aws_s3": {
                "bucket_name": self.get_bucket_by_prefix(settings.aws_s3_bucket_name),
            },
            "aws_rekognition": {
                "collection_id": self.get_rekognition_collection_by_id(settings.aws_rekognition_collection_id),
            },
        }

    def get_api_stage(self) -> str:
        """Return the API stage."""
        api = self.get_api(settings.aws_apigateway_name)
        api_id = api["id"]
        response = settings.aws_apigateway_client.get_stages(restApiId=api_id)
        # Assuming you want the most recently deployed stage
        stages = response.get("item", [])
        if stages:
            retval = stages[-1]["stageName"]
            return retval
        return ""

    def get_url(self, path) -> str:
        """Return the url for the given path."""
        if settings.aws_apigateway_create_custom_domaim:
            return f"https://{settings.aws_apigateway_domain_name}{path}"
        return f"https://{settings.aws_apigateway_domain_name}/{self.get_api_stage()}{path}"

    def aws_connection_works(self):
        """Test that the AWS connection works."""
        try:
            # Try a benign operation
            settings.aws_s3_client.list_buckets()
            return True
        except Exception:  # pylint: disable=broad-exception-caught
            return False

    def domain_exists(self) -> bool:
        """Test that the domain exists."""
        try:
            socket.gethostbyname(settings.aws_apigateway_domain_name)
            return True
        except socket.gaierror:
            return False

    def get_bucket_by_prefix(self, bucket_prefix) -> str:
        """Return the bucket name given the bucket prefix."""
        for bucket in settings.aws_s3_client.list_buckets()["Buckets"]:
            if bucket["Name"].startswith(bucket_prefix):
                return f"arn:aws:s3:::{bucket['Name']}"
        return None

    def bucket_exists(self, bucket_prefix) -> bool:
        """Test that the S3 bucket exists."""
        bucket = self.get_bucket_by_prefix(bucket_prefix)
        return bucket is not None

    def get_dyanmodb_table_by_name(self, table_name) -> str:
        """Return the DynamoDB table given the table name."""
        response = settings.aws_dynamodb_client.list_tables()
        for table in response["TableNames"]:
            if table == table_name:
                table_description = settings.aws_dynamodb_client.describe_table(TableName=table_name)
                return table_description["Table"]["TableArn"]
        return None

    def dynamodb_table_exists(self, table_name) -> bool:
        """Test that the DynamoDB table exists."""
        table = self.get_dyanmodb_table_by_name(table_name)
        return table is not None

    def api_exists(self, api_name: str) -> bool:
        """Test that the API Gateway exists."""
        response = settings.aws_apigateway_client.get_rest_apis()

        for item in response["items"]:
            if item["name"] == api_name:
                return True
        return False

    def get_api(self, api_name: str) -> json:
        """Test that the API Gateway exists."""
        response = settings.aws_apigateway_client.get_rest_apis()

        for item in response["items"]:
            if item["name"] == api_name:
                return item
        return False

    def api_resource_and_method_exists(self, path, method) -> bool:
        """Test that the API Gateway resource and method exists."""
        api = self.get_api(settings.aws_apigateway_name)
        api_id = api["id"]
        resources = settings.aws_apigateway_client.get_resources(restApiId=api_id)
        for resource in resources["items"]:
            if resource["path"] == path:
                try:
                    settings.aws_apigateway_client.get_method(
                        restApiId=api_id, resourceId=resource["id"], httpMethod=method
                    )
                    return True
                except settings.aws_apigateway_client.exceptions.NotFoundException:
                    return False

        return False

    def get_api_keys(self) -> str:
        """Test that the API Gateway exists."""
        response = settings.aws_apigateway_client.get_api_keys(includeValues=True)
        for item in response["items"]:
            if item["name"] == settings.shared_resource_identifier:
                return item["value"]
        return False

    def get_rekognition_collection_by_id(self, collection_id) -> str:
        """Return the Rekognition collection."""
        rekognition_client = settings.aws_session.client("rekognition")
        response = rekognition_client.list_collections()
        for collection in response["CollectionIds"]:
            if collection == collection_id:
                return collection
        return None

    def rekognition_collection_exists(self) -> bool:
        """Test that the Rekognition collection exists."""
        collection = self.get_rekognition_collection_by_id(settings.aws_rekognition_collection_id)
        return collection is not None


aws_infrastructure_config = AWSInfrastructureConfig()
