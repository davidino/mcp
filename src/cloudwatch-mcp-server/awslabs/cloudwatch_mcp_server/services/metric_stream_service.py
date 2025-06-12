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

"""CloudWatch Metric Stream service implementation."""

from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError
from loguru import logger

from awslabs.cloudwatch_mcp_server.common import remove_null_values


class MetricStreamService:
    """Service for CloudWatch Metric Stream operations."""
    
    def __init__(self, cloudwatch_client):
        """Initialize the metric stream service with a CloudWatch client."""
        self.cloudwatch_client = cloudwatch_client
    
    async def delete_metric_stream(
        self,
        name: str,
    ) -> Dict[str, str]:
        """Deletes the specified metric stream."""
        try:
            self.cloudwatch_client.delete_metric_stream(
                Name=name
            )
            
            logger.info(f'Successfully deleted metric stream: {name}')
            return {"status": f"Successfully deleted metric stream: {name}"}
        except ClientError as e:
            logger.error(f"ClientError in delete_metric_stream: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in delete_metric_stream: {e}")
            raise
    
    async def get_metric_stream(
        self,
        name: str,
    ) -> Dict[str, Any]:
        """Retrieves the specified metric stream."""
        try:
            response = self.cloudwatch_client.get_metric_stream(
                Name=name
            )
            
            return {
                "arn": response.get('Arn'),
                "name": response.get('Name'),
                "includeFilters": response.get('IncludeFilters'),
                "excludeFilters": response.get('ExcludeFilters'),
                "firehoseArn": response.get('FirehoseArn'),
                "roleArn": response.get('RoleArn'),
                "state": response.get('State'),
                "creationDate": response.get('CreationDate').isoformat() if hasattr(response.get('CreationDate'), 'isoformat') else str(response.get('CreationDate')),
                "lastUpdateDate": response.get('LastUpdateDate').isoformat() if hasattr(response.get('LastUpdateDate'), 'isoformat') else str(response.get('LastUpdateDate')),
                "outputFormat": response.get('OutputFormat'),
                "statisticsConfigurations": response.get('StatisticsConfigurations'),
                "includeLinkedAccountsMetrics": response.get('IncludeLinkedAccountsMetrics')
            }
        except ClientError as e:
            logger.error(f"ClientError in get_metric_stream: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in get_metric_stream: {e}")
            raise
    
    async def list_metric_streams(
        self,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Lists the metric streams in your account."""
        try:
            kwargs = {
                'NextToken': next_token,
                'MaxResults': max_results,
            }
            
            response = self.cloudwatch_client.list_metric_streams(**remove_null_values(kwargs))
            
            # Convert dates to strings
            entries = []
            for entry in response.get('Entries', []):
                if 'CreationDate' in entry and hasattr(entry['CreationDate'], 'isoformat'):
                    entry['CreationDate'] = entry['CreationDate'].isoformat()
                if 'LastUpdateDate' in entry and hasattr(entry['LastUpdateDate'], 'isoformat'):
                    entry['LastUpdateDate'] = entry['LastUpdateDate'].isoformat()
                entries.append(entry)
            
            return {
                "entries": entries,
                "nextToken": response.get('NextToken')
            }
        except ClientError as e:
            logger.error(f"ClientError in list_metric_streams: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in list_metric_streams: {e}")
            raise
    
    async def put_metric_stream(
        self,
        name: str,
        firehose_arn: str,
        role_arn: str,
        output_format: str,
        include_filters: Optional[List[Dict]] = None,
        exclude_filters: Optional[List[Dict]] = None,
        statistics_configurations: Optional[List[Dict]] = None,
        include_linked_accounts_metrics: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Creates or updates a metric stream."""
        try:
            kwargs = {
                'Name': name,
                'FirehoseArn': firehose_arn,
                'RoleArn': role_arn,
                'OutputFormat': output_format,
                'IncludeFilters': include_filters,
                'ExcludeFilters': exclude_filters,
                'StatisticsConfigurations': statistics_configurations,
                'IncludeLinkedAccountsMetrics': include_linked_accounts_metrics,
            }
            
            response = self.cloudwatch_client.put_metric_stream(**remove_null_values(kwargs))
            
            logger.info(f'Successfully created or updated metric stream: {name}')
            return {
                "status": f"Successfully created or updated metric stream: {name}",
                "arn": response.get('Arn')
            }
        except ClientError as e:
            logger.error(f"ClientError in put_metric_stream: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in put_metric_stream: {e}")
            raise
    
    async def start_metric_streams(
        self,
        names: List[str],
    ) -> Dict[str, str]:
        """Starts the specified metric streams."""
        try:
            self.cloudwatch_client.start_metric_streams(
                Names=names
            )
            
            logger.info(f'Successfully started {len(names)} metric streams')
            return {"status": f"Successfully started {len(names)} metric streams"}
        except ClientError as e:
            logger.error(f"ClientError in start_metric_streams: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in start_metric_streams: {e}")
            raise
    
    async def stop_metric_streams(
        self,
        names: List[str],
    ) -> Dict[str, str]:
        """Stops the specified metric streams."""
        try:
            self.cloudwatch_client.stop_metric_streams(
                Names=names
            )
            
            logger.info(f'Successfully stopped {len(names)} metric streams')
            return {"status": f"Successfully stopped {len(names)} metric streams"}
        except ClientError as e:
            logger.error(f"ClientError in stop_metric_streams: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in stop_metric_streams: {e}")
            raise