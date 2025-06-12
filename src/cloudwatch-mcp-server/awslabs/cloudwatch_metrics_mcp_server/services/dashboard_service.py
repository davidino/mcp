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

"""CloudWatch Dashboard service implementation."""

import json
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError
from loguru import logger

from awslabs.cloudwatch_metrics_mcp_server.common import remove_null_values


class DashboardService:
    """Service for CloudWatch Dashboard operations."""
    
    def __init__(self, cloudwatch_client):
        """Initialize the dashboard service with a CloudWatch client."""
        self.cloudwatch_client = cloudwatch_client
    
    async def delete_dashboards(
        self,
        dashboard_names: List[str],
    ) -> Dict[str, str]:
        """Deletes the specified CloudWatch dashboards."""
        try:
            self.cloudwatch_client.delete_dashboards(DashboardNames=dashboard_names)
            logger.info(f'Successfully deleted {len(dashboard_names)} dashboards')
            return {"status": f"Successfully deleted {len(dashboard_names)} dashboards"}
        except ClientError as e:
            logger.error(f"ClientError in delete_dashboards: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in delete_dashboards: {e}")
            raise
    
    async def get_dashboard(
        self,
        dashboard_name: str,
    ) -> Dict[str, Any]:
        """Retrieves the specified CloudWatch dashboard."""
        try:
            response = self.cloudwatch_client.get_dashboard(DashboardName=dashboard_name)
            return {
                "dashboardName": response.get('DashboardName'),
                "dashboardArn": response.get('DashboardArn'),
                "dashboardBody": response.get('DashboardBody'),
                "size": response.get('Size')
            }
        except ClientError as e:
            logger.error(f"ClientError in get_dashboard: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in get_dashboard: {e}")
            raise
    
    async def list_dashboards(
        self,
        dashboard_name_prefix: Optional[str] = None,
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Lists the CloudWatch dashboards in your account."""
        try:
            kwargs = {
                'DashboardNamePrefix': dashboard_name_prefix,
                'NextToken': next_token,
            }
            response = self.cloudwatch_client.list_dashboards(**remove_null_values(kwargs))
            return {
                "dashboardEntries": response.get('DashboardEntries', []),
                "nextToken": response.get('NextToken')
            }
        except ClientError as e:
            logger.error(f"ClientError in list_dashboards: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in list_dashboards: {e}")
            raise
    
    async def put_dashboard(
        self,
        dashboard_name: str,
        dashboard_body: Any,
    ) -> Dict[str, Any]:
        """Creates or updates a CloudWatch dashboard.
        
        Args:
            dashboard_name: The name of the dashboard.
            dashboard_body: The dashboard body as a string or dictionary.
            
        Returns:
            A dictionary containing dashboard validation messages.
            
        Raises:
            ValueError: If the dashboard body is not valid JSON.
        """
        try:
            # Convert dictionary to JSON string if needed
            if isinstance(dashboard_body, dict):
                dashboard_body = json.dumps(dashboard_body)
            
            # Validate that dashboard_body is valid JSON
            try:
                json.loads(dashboard_body)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in dashboard_body: {e}")
                raise ValueError(f"The dashboard_body must be a valid JSON string: {e}")
            
            response = self.cloudwatch_client.put_dashboard(
                DashboardName=dashboard_name,
                DashboardBody=dashboard_body
            )
            return {
                "dashboardValidationMessages": response.get('DashboardValidationMessages', [])
            }
        except ClientError as e:
            logger.error(f"ClientError in put_dashboard: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in put_dashboard: {e}")
            raise