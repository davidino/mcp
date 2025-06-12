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

"""CloudWatch Metric API routes."""

from typing import Dict, List, Optional, Any, Union
from mcp.server.fastmcp import Context
from pydantic import Field

from awslabs.cloudwatch_mcp_server.services.metric_service import MetricService
from awslabs.cloudwatch_mcp_server.services.client_factory import ClientFactory
from awslabs.cloudwatch_mcp_server.models import MetricList, MetricData, MetricStatistics


# Initialize services
cloudwatch_client = ClientFactory.get_cloudwatch_client()
metric_service = MetricService(cloudwatch_client)


async def list_metrics_route(
    ctx: Context,
    mcp,
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
    """
    return await metric_service.list_metrics(
        namespace=namespace,
        metric_name=metric_name,
        dimensions=dimensions,
        max_items=max_items,
    )


async def get_metric_data_route(
    ctx: Context,
    mcp,
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
    """
    return await metric_service.get_metric_data(
        metric_data_queries=metric_data_queries,
        start_time=start_time,
        end_time=end_time,
        scan_by=scan_by,
        max_datapoints=max_datapoints,
    )


async def get_metric_statistics_route(
    ctx: Context,
    mcp,
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
        description='The unit for the metric.',
    ),
) -> List[MetricStatistics]:
    """Retrieves statistics for a specified CloudWatch metric.
    
    This tool allows you to get statistical data for a specific metric over a specified time range.
    You can specify the period, statistics types, and unit for the metric.
    
    Usage: Use this tool to analyze the statistical behavior of a metric over time.
    """
    return await metric_service.get_metric_statistics(
        namespace=namespace,
        metric_name=metric_name,
        dimensions=dimensions,
        start_time=start_time,
        end_time=end_time,
        period=period,
        statistics=statistics,
        unit=unit,
    )


async def put_metric_data_route(
    ctx: Context,
    mcp,
    namespace: str = Field(
        ...,
        description='The namespace for the metric data.',
    ),
    metric_data: List[Dict] = Field(
        ...,
        description='The metric data points to publish. Each data point must include MetricName and Value.',
    ),
):
    """Publishes metric data points to Amazon CloudWatch.
    
    This tool allows you to publish custom metric data to CloudWatch.
    Each metric data point must include a metric name and value.
    
    Usage: Use this tool to publish custom metrics to CloudWatch for monitoring.
    """
    return await metric_service.put_metric_data(
        namespace=namespace,
        metric_data=metric_data,
    )


async def get_metric_widget_image_route(
    ctx: Context,
    mcp,
    metric_widget: Union[str, Dict[str, Any]] = Field(
        ...,
        description='The metric widget definition as a JSON string or dictionary.',
    ),
    output_format: Optional[str] = Field(
        None,
        description='The format of the resulting image. Valid values are png and jpg.',
    ),
) -> Dict[str, Any]:
    """Gets a snapshot graph of one or more CloudWatch metrics as a bitmap image.
    
    This tool allows you to get a snapshot graph of CloudWatch metrics as an image.
    The metric widget can be defined using either a JSON string or a dictionary.
    
    Example widget definition:
    {
      "width": 600,
      "height": 400,
      "metrics": [
        [ "AWS/EC2", "CPUUtilization", "InstanceId", "i-012345" ]
      ],
      "period": 300,
      "stat": "Average",
      "title": "EC2 Instance CPU"
    }
    
    Usage: Use this tool to generate metric visualizations for reports or dashboards.
    """
    try:
        return await metric_service.get_metric_widget_image(
            metric_widget=metric_widget,
            output_format=output_format,
        )
    except ValueError as e:
        await ctx.error(str(e))
        raise


def register_routes(mcp_server):
    """Register all metric routes with the MCP server."""
    mcp_server.tool(name='list_metrics')(list_metrics_route)
    mcp_server.tool(name='get_metric_data')(get_metric_data_route)
    mcp_server.tool(name='get_metric_statistics')(get_metric_statistics_route)
    mcp_server.tool(name='put_metric_data')(put_metric_data_route)
    mcp_server.tool(name='get_metric_widget_image')(get_metric_widget_image_route)