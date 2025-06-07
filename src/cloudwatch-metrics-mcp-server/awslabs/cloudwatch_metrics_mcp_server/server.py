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

"""awslabs cloudwatch-metrics MCP Server implementation."""

import boto3
import datetime
import os
from awslabs.cloudwatch_metrics_mcp_server import MCP_SERVER_VERSION
from awslabs.cloudwatch_metrics_mcp_server.common import remove_null_values
from awslabs.cloudwatch_metrics_mcp_server.models import (
    Dimension,
    Metric,
    MetricData,
    MetricDataQuery,
    MetricDataResult,
    MetricList,
    MetricStatistics,
)
from botocore.config import Config
from loguru import logger
from mcp.server.fastmcp import Context, FastMCP
from pydantic import Field
from typing import Dict, List, Optional, Union


mcp = FastMCP(
    'awslabs.cloudwatch-metrics-mcp-server',
    instructions='Use this MCP server to run read-only commands and analyze CloudWatch Metrics. Supports retrieving metric data using the GetMetricData API. With CloudWatch Metrics, you can monitor your AWS resources and applications in real-time, set alarms, and visualize metrics to help you respond to operational issues.',
    dependencies=[
        'pydantic',
        'loguru',
    ],
)

# Initialize client
aws_region: str = os.environ.get('AWS_REGION', 'us-east-1')
config = Config(user_agent_extra=f'awslabs/mcp/cloudwatch-metrics-mcp-server/{MCP_SERVER_VERSION}')

try:
    if aws_profile := os.environ.get('AWS_PROFILE'):
        cloudwatch_client = boto3.Session(profile_name=aws_profile, region_name=aws_region).client(
            'cloudwatch', config=config
        )
    else:
        cloudwatch_client = boto3.Session(region_name=aws_region).client('cloudwatch', config=config)
except Exception as e:
    logger.error(f'Error creating cloudwatch client: {str(e)}')
    raise


@mcp.tool(name='list_metrics')
async def list_metrics_tool(
    ctx: Context,
    namespace: Optional[str] = Field(
        None,
        description='The namespace to filter metrics by',
    ),
    metric_name: Optional[str] = Field(
        None,
        description='The name of the metric to filter by',
    ),
    dimensions: Optional[List[Dict[str, str]]] = Field(
        None,
        description='The dimensions to filter by. Each dimension is a dictionary with "Name" and "Value" keys.',
    ),
    max_items: Optional[int] = Field(
        None,
        description='The maximum number of metrics to return',
    ),
) -> MetricList:
    """Lists CloudWatch metrics based on the specified filters.
    
    This tool retrieves information about available CloudWatch metrics in your AWS account.
    You can filter the metrics by namespace, metric name, and dimensions.
    
    Usage: Use this tool to discover available metrics that you can query data for.
    
    Returns:
    --------
    A MetricList object containing:
        - metrics: List of Metric objects with details such as namespace, metricName, and dimensions
        - nextToken: Token for pagination if there are more results
    """
    
    try:
        paginator = cloudwatch_client.get_paginator('list_metrics')
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
    
    except Exception as e:
        logger.error(f'Error in list_metrics_tool: {str(e)}')
        await ctx.error(f'Error listing metrics: {str(e)}')
        raise


@mcp.tool(name='get_metric_data')
async def get_metric_data_tool(
    ctx: Context,
    metric_data_queries: List[Dict] = Field(
        ...,
        description='List of metric data queries. Each query should have an "Id" and either a "MetricStat" or "Expression".',
    ),
    start_time: str = Field(
        ...,
        description='ISO 8601 formatted start time for the metric data query (e.g., "2025-04-19T20:00:00+00:00").',
    ),
    end_time: str = Field(
        ...,
        description='ISO 8601 formatted end time for the metric data query (e.g., "2025-04-19T21:00:00+00:00").',
    ),
    scan_by: Optional[str] = Field(
        None,
        description='The order to scan the metrics in. Valid values are "TimestampAscending" or "TimestampDescending".',
    ),
    max_datapoints: Optional[int] = Field(
        None,
        description='The maximum number of data points to return in the response.',
    ),
) -> MetricData:
    """Retrieves CloudWatch metric data using the GetMetricData API.
    
    This tool allows you to query multiple metrics and perform math expressions on them.
    You can specify the time range, scan order, and maximum number of data points to return.
    
    Usage: Use this tool to retrieve metric data for analysis and visualization.
    
    Returns:
    --------
    A MetricData object containing:
        - metricDataResults: List of MetricDataResult objects with the query results
        - nextToken: Token for pagination if there are more results
        - messages: Any messages related to the query
    """
    
    try:
        kwargs = {
            'MetricDataQueries': metric_data_queries,
            'StartTime': datetime.datetime.fromisoformat(start_time),
            'EndTime': datetime.datetime.fromisoformat(end_time),
            'ScanBy': scan_by,
            'MaxDatapoints': max_datapoints,
        }
        
        response = cloudwatch_client.get_metric_data(**remove_null_values(kwargs))
        
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
    
    except Exception as e:
        logger.error(f'Error in get_metric_data_tool: {str(e)}')
        await ctx.error(f'Error retrieving metric data: {str(e)}')
        raise


@mcp.tool(name='get_metric_statistics')
async def get_metric_statistics_tool(
    ctx: Context,
    namespace: str = Field(
        ...,
        description='The namespace of the metric',
    ),
    metric_name: str = Field(
        ...,
        description='The name of the metric',
    ),
    dimensions: Optional[List[Dict[str, str]]] = Field(
        None,
        description='The dimensions of the metric. Each dimension is a dictionary with "Name" and "Value" keys.',
    ),
    start_time: str = Field(
        ...,
        description='ISO 8601 formatted start time for the metric statistics query (e.g., "2025-04-19T20:00:00+00:00").',
    ),
    end_time: str = Field(
        ...,
        description='ISO 8601 formatted end time for the metric statistics query (e.g., "2025-04-19T21:00:00+00:00").',
    ),
    period: int = Field(
        ...,
        description='The granularity, in seconds, of the returned data points.',
    ),
    statistics: List[str] = Field(
        ...,
        description='The statistics to retrieve. Valid values are SampleCount, Average, Sum, Minimum, and Maximum.',
    ),
    unit: Optional[str] = Field(
        None,
        description='The unit for the metric. Valid values include Seconds, Microseconds, Milliseconds, Bytes, Kilobytes, Megabytes, Gigabytes, Terabytes, Bits, Kilobits, Megabits, Gigabits, Terabits, Percent, Count, Bytes/Second, Kilobytes/Second, Megabytes/Second, Gigabytes/Second, Terabytes/Second, Bits/Second, Kilobits/Second, Megabits/Second, Gigabits/Second, Terabits/Second, Count/Second, None.',
    ),
) -> List[MetricStatistics]:
    """Retrieves statistics for a specified CloudWatch metric.
    
    This tool allows you to get statistical data for a specific metric over a specified time range.
    You can specify the period, statistics types, and unit for the metric.
    
    Usage: Use this tool to analyze the statistical behavior of a metric over time.
    
    Returns:
    --------
    A list of MetricStatistics objects, each containing:
        - timestamp: The timestamp for the data point
        - sampleCount: The number of samples used for the data point
        - average: The average value for the data point
        - sum: The sum of values for the data point
        - minimum: The minimum value for the data point
        - maximum: The maximum value for the data point
    """
    
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
        
        response = cloudwatch_client.get_metric_statistics(**remove_null_values(kwargs))
        
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
    
    except Exception as e:
        logger.error(f'Error in get_metric_statistics_tool: {str(e)}')
        await ctx.error(f'Error retrieving metric statistics: {str(e)}')
        raise


def main():
    """Run the MCP server."""
    mcp.run()
    
    logger.info('CloudWatch Metrics MCP server started')


if __name__ == '__main__':
    main()