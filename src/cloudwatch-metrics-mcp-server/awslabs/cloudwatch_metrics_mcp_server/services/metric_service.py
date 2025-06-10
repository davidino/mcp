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

"""CloudWatch Metric service implementation."""

import datetime
from typing import Dict, List, Optional, Any, Union
from botocore.exceptions import ClientError
from loguru import logger

from awslabs.cloudwatch_metrics_mcp_server.common import remove_null_values
from awslabs.cloudwatch_metrics_mcp_server.models import (
    Dimension,
    Metric,
    MetricData,
    MetricDataResult,
    MetricList,
    MetricStatistics,
)


class MetricService:
    """Service for CloudWatch Metric operations."""
    
    def __init__(self, cloudwatch_client):
        """Initialize the metric service with a CloudWatch client."""
        self.cloudwatch_client = cloudwatch_client
    
    async def list_metrics(
        self,
        namespace: Optional[str] = None,
        metric_name: Optional[str] = None,
        dimensions: Optional[List[Dict[str, str]]] = None,
        max_items: Optional[int] = None,
    ) -> MetricList:
        """Lists CloudWatch metrics based on the specified filters."""
        try:
            paginator = self.cloudwatch_client.get_paginator('list_metrics')
            kwargs = {
                'Namespace': namespace,
                'MetricName': metric_name,
                'Dimensions': dimensions,
            }
            
            if max_items:
                kwargs['PaginationConfig'] = {'MaxItems': max_items}
            
            metrics = []
            for page in paginator.paginate(**remove_null_values(kwargs)):
                metrics.extend(page.get('Metrics', []))
                
            logger.info(f'Found {len(metrics)} metrics')
            
            # Convert to our model format
            modeled_metrics = []
            for metric in metrics:
                dimensions = []
                for dim in metric.get('Dimensions', []):
                    dimensions.append(Dimension(name=dim['Name'], value=dim['Value']))
                
                modeled_metrics.append(
                    Metric(
                        namespace=metric['Namespace'],
                        metricName=metric['MetricName'],
                        dimensions=dimensions
                    )
                )
            
            return MetricList(metrics=modeled_metrics)
        except ClientError as e:
            logger.error(f"ClientError in list_metrics: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in list_metrics: {e}")
            raise
    
    async def get_metric_data(
        self,
        metric_data_queries: List[Dict],
        start_time: str,
        end_time: str,
        scan_by: Optional[str] = None,
        max_datapoints: Optional[int] = None,
    ) -> MetricData:
        """Retrieves CloudWatch metric data using the GetMetricData API."""
        try:
            kwargs = {
                'MetricDataQueries': metric_data_queries,
                'StartTime': datetime.datetime.fromisoformat(start_time),
                'EndTime': datetime.datetime.fromisoformat(end_time),
                'ScanBy': scan_by,
                'MaxDatapoints': max_datapoints,
            }
            
            response = self.cloudwatch_client.get_metric_data(**remove_null_values(kwargs))
            
            # Convert to our model format
            results = []
            for result in response.get('MetricDataResults', []):
                results.append(
                    MetricDataResult(
                        id=result['Id'],
                        label=result.get('Label'),
                        statusCode=result['StatusCode'],
                        timestamps=result.get('Timestamps', []),
                        values=result.get('Values', []),
                        messages=result.get('Messages'),
                    )
                )
            
            return MetricData(
                metricDataResults=results,
                nextToken=response.get('NextToken'),
                messages=response.get('Messages'),
            )
        except ClientError as e:
            logger.error(f"ClientError in get_metric_data: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in get_metric_data: {e}")
            raise
    
    async def get_metric_statistics(
        self,
        namespace: str,
        metric_name: str,
        start_time: str,
        end_time: str,
        period: int,
        statistics: List[str],
        dimensions: Optional[List[Dict[str, str]]] = None,
        unit: Optional[str] = None,
    ) -> List[MetricStatistics]:
        """Retrieves statistics for a specified CloudWatch metric."""
        try:
            kwargs = {
                'Namespace': namespace,
                'MetricName': metric_name,
                'Dimensions': dimensions,
                'StartTime': datetime.datetime.fromisoformat(start_time),
                'EndTime': datetime.datetime.fromisoformat(end_time),
                'Period': period,
                'Statistics': statistics,
                'Unit': unit,
            }
            
            response = self.cloudwatch_client.get_metric_statistics(**remove_null_values(kwargs))
            
            # Convert to our model format
            results = []
            for datapoint in response.get('Datapoints', []):
                results.append(
                    MetricStatistics(
                        timestamp=datapoint['Timestamp'],
                        sampleCount=datapoint.get('SampleCount'),
                        average=datapoint.get('Average'),
                        sum=datapoint.get('Sum'),
                        minimum=datapoint.get('Minimum'),
                        maximum=datapoint.get('Maximum'),
                    )
                )
            
            return results
        except ClientError as e:
            logger.error(f"ClientError in get_metric_statistics: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in get_metric_statistics: {e}")
            raise
    
    async def put_metric_data(
        self,
        namespace: str,
        metric_data: List[Dict],
    ) -> Dict[str, str]:
        """Publishes metric data points to Amazon CloudWatch."""
        try:
            self.cloudwatch_client.put_metric_data(
                Namespace=namespace,
                MetricData=metric_data
            )
            
            logger.info(f'Successfully published {len(metric_data)} metric data points to {namespace}')
            return {"status": f"Successfully published {len(metric_data)} metric data points to {namespace}"}
        except ClientError as e:
            logger.error(f"ClientError in put_metric_data: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in put_metric_data: {e}")
            raise