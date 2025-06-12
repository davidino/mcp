# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""CloudWatch Tag service implementation."""

from typing import Dict, List, Any
from botocore.exceptions import ClientError
from loguru import logger


class TagService:
    """Service for CloudWatch Tag operations."""
    
    def __init__(self, cloudwatch_client):
        """Initialize the tag service with a CloudWatch client."""
        self.cloudwatch_client = cloudwatch_client
    
    async def list_tags_for_resource(
        self,
        resource_arn: str,
    ) -> Dict[str, Any]:
        """Lists the tags for a CloudWatch resource."""
        try:
            response = self.cloudwatch_client.list_tags_for_resource(
                ResourceARN=resource_arn
            )
            return {
                "tags": response.get('Tags', [])
            }
        except ClientError as e:
            logger.error(f"ClientError in list_tags_for_resource: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in list_tags_for_resource: {e}")
            raise
    
    async def tag_resource(
        self,
        resource_arn: str,
        tags: List[Dict[str, str]],
    ) -> Dict[str, str]:
        """Adds or modifies tags for a CloudWatch resource."""
        try:
            self.cloudwatch_client.tag_resource(
                ResourceARN=resource_arn,
                Tags=tags
            )
            logger.info(f'Successfully tagged resource: {resource_arn}')
            return {"status": f"Successfully tagged resource: {resource_arn}"}
        except ClientError as e:
            logger.error(f"ClientError in tag_resource: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in tag_resource: {e}")
            raise
    
    async def untag_resource(
        self,
        resource_arn: str,
        tag_keys: List[str],
    ) -> Dict[str, str]:
        """Removes tags from a CloudWatch resource."""
        try:
            self.cloudwatch_client.untag_resource(
                ResourceARN=resource_arn,
                TagKeys=tag_keys
            )
            logger.info(f'Successfully untagged resource: {resource_arn}')
            return {"status": f"Successfully untagged resource: {resource_arn}"}
        except ClientError as e:
            logger.error(f"ClientError in untag_resource: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in untag_resource: {e}")
            raise