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

"""AWS client factory for CloudWatch MCP server."""

import boto3
import os
from botocore.config import Config
from loguru import logger

from awslabs.cloudwatch_mcp_server import MCP_SERVER_VERSION


class ClientFactory:
    """Factory for creating AWS clients."""
    
    @staticmethod
    def get_cloudwatch_client(region_name=None, profile_name=None):
        """
        Get a CloudWatch client.
        
        Args:
            region_name: AWS region name
            profile_name: AWS profile name
            
        Returns:
            A boto3 CloudWatch client
        """
        try:
            # Use environment variables if parameters not provided
            region = region_name or os.environ.get('AWS_REGION', 'us-east-1')
            profile = profile_name or os.environ.get('AWS_PROFILE')
            
            config = Config(user_agent_extra=f'awslabs/mcp/cloudwatch-metrics-mcp-server/{MCP_SERVER_VERSION}')
            
            if profile:
                return boto3.Session(profile_name=profile, region_name=region).client('cloudwatch', config=config)
            else:
                return boto3.Session(region_name=region).client('cloudwatch', config=config)
                
        except Exception as e:
            logger.error(f'Error creating CloudWatch client: {str(e)}')
            raise