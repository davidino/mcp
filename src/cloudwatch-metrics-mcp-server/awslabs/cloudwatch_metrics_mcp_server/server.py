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
    instructions='Use this MCP server to interact with CloudWatch Metrics and Dashboards. Supports retrieving metric data, managing dashboards, and working with CloudWatch alarms. With CloudWatch, you can monitor your AWS resources and applications in real-time, set alarms, create dashboards, and visualize metrics to help you respond to operational issues.',
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
        description='The unit for the metric.',
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


# Dashboard API implementations
@mcp.tool(name='delete_dashboards')
async def delete_dashboards_tool(
    ctx: Context,
    dashboard_names: List[str] = Field(
        ...,
        description='The names of the dashboards to delete.',
    ),
) -> Dict[str, str]:
    """Deletes the specified CloudWatch dashboards."""
    try:
        cloudwatch_client.delete_dashboards(DashboardNames=dashboard_names)
        logger.info(f'Successfully deleted {len(dashboard_names)} dashboards')
        return {"status": f"Successfully deleted {len(dashboard_names)} dashboards"}
    except Exception as e:
        logger.error(f'Error in delete_dashboards_tool: {str(e)}')
        await ctx.error(f'Error deleting dashboards: {str(e)}')
        raise

@mcp.tool(name='get_dashboard')
async def get_dashboard_tool(
    ctx: Context,
    dashboard_name: str = Field(
        ...,
        description='The name of the dashboard to retrieve.',
    ),
):
    """Retrieves the specified CloudWatch dashboard."""
    try:
        response = cloudwatch_client.get_dashboard(DashboardName=dashboard_name)
        return {
            "dashboardName": response.get('DashboardName'),
            "dashboardArn": response.get('DashboardArn'),
            "dashboardBody": response.get('DashboardBody'),
            "size": response.get('Size')
        }
    except Exception as e:
        logger.error(f'Error in get_dashboard_tool: {str(e)}')
        await ctx.error(f'Error retrieving dashboard: {str(e)}')
        raise

@mcp.tool(name='list_dashboards')
async def list_dashboards_tool(
    ctx: Context,
    dashboard_name_prefix: Optional[str] = Field(
        None,
        description='The prefix of the dashboard names to filter by.',
    ),
    next_token: Optional[str] = Field(
        None,
        description='The token for the next set of results.',
    ),
):
    """Lists the CloudWatch dashboards in your account."""
    try:
        kwargs = {
            'DashboardNamePrefix': dashboard_name_prefix,
            'NextToken': next_token,
        }
        response = cloudwatch_client.list_dashboards(**remove_null_values(kwargs))
        return {
            "dashboardEntries": response.get('DashboardEntries', []),
            "nextToken": response.get('NextToken')
        }
    except Exception as e:
        logger.error(f'Error in list_dashboards_tool: {str(e)}')
        await ctx.error(f'Error listing dashboards: {str(e)}')
        raise

@mcp.tool(name='put_dashboard')
async def put_dashboard_tool(
    ctx: Context,
    dashboard_name: str = Field(
        ...,
        description='The name of the dashboard.',
    ),
    dashboard_body: str = Field(
        ...,
        description='The detailed information about the dashboard in JSON format.',
    ),
):
    """Creates or updates a CloudWatch dashboard."""
    try:
        response = cloudwatch_client.put_dashboard(
            DashboardName=dashboard_name,
            DashboardBody=dashboard_body
        )
        return {
            "dashboardValidationMessages": response.get('DashboardValidationMessages', [])
        }
    except Exception as e:
        logger.error(f'Error in put_dashboard_tool: {str(e)}')
        await ctx.error(f'Error creating or updating dashboard: {str(e)}')
        raise


# Anomaly Detector API implementations
@mcp.tool(name='delete_anomaly_detector')
async def delete_anomaly_detector_tool(
    ctx: Context,
    namespace: str = Field(
        ...,
        description='The namespace of the metric.',
    ),
    metric_name: str = Field(
        ...,
        description='The name of the metric.',
    ),
    dimensions: Optional[List[Dict[str, str]]] = Field(
        None,
        description='The dimensions of the metric. Each dimension is a dictionary with "Name" and "Value" keys.',
    ),
    stat: Optional[str] = Field(
        None,
        description='The statistic of the metric.',
    ),
    single_metric_anomaly_detector: Optional[Dict] = Field(
        None,
        description='A single metric anomaly detector to delete.',
    ),
    metric_math_anomaly_detector: Optional[Dict] = Field(
        None,
        description='A metric math anomaly detector to delete.',
    ),
):
    """Deletes the specified anomaly detection model."""
    try:
        kwargs = {
            'Namespace': namespace,
            'MetricName': metric_name,
            'Dimensions': dimensions,
            'Stat': stat,
            'SingleMetricAnomalyDetector': single_metric_anomaly_detector,
            'MetricMathAnomalyDetector': metric_math_anomaly_detector,
        }
        cloudwatch_client.delete_anomaly_detector(**remove_null_values(kwargs))
        logger.info(f'Successfully deleted anomaly detector for {namespace}:{metric_name}')
        return {"status": f"Successfully deleted anomaly detector for {namespace}:{metric_name}"}
    except Exception as e:
        logger.error(f'Error in delete_anomaly_detector_tool: {str(e)}')
        await ctx.error(f'Error deleting anomaly detector: {str(e)}')
        raise


@mcp.tool(name='describe_anomaly_detectors')
async def describe_anomaly_detectors_tool(
    ctx: Context,
    namespace: Optional[str] = Field(
        None,
        description='The namespace of the metric.',
    ),
    metric_name: Optional[str] = Field(
        None,
        description='The name of the metric.',
    ),
    dimensions: Optional[List[Dict[str, str]]] = Field(
        None,
        description='The dimensions of the metric. Each dimension is a dictionary with "Name" and "Value" keys.',
    ),
    stat: Optional[str] = Field(
        None,
        description='The statistic of the metric.',
    ),
    next_token: Optional[str] = Field(
        None,
        description='The token for the next set of results.',
    ),
    max_results: Optional[int] = Field(
        None,
        description='The maximum number of results to return.',
    ),
):
    """Lists the anomaly detection models that you have created."""
    try:
        kwargs = {
            'Namespace': namespace,
            'MetricName': metric_name,
            'Dimensions': dimensions,
            'Stat': stat,
            'NextToken': next_token,
            'MaxResults': max_results,
        }
        response = cloudwatch_client.describe_anomaly_detectors(**remove_null_values(kwargs))
        return {
            "anomalyDetectors": response.get('AnomalyDetectors', []),
            "nextToken": response.get('NextToken')
        }
    except Exception as e:
        logger.error(f'Error in describe_anomaly_detectors_tool: {str(e)}')
        await ctx.error(f'Error describing anomaly detectors: {str(e)}')
        raise


@mcp.tool(name='put_anomaly_detector')
async def put_anomaly_detector_tool(
    ctx: Context,
    namespace: str = Field(
        ...,
        description='The namespace of the metric.',
    ),
    metric_name: str = Field(
        ...,
        description='The name of the metric.',
    ),
    dimensions: Optional[List[Dict[str, str]]] = Field(
        None,
        description='The dimensions of the metric. Each dimension is a dictionary with "Name" and "Value" keys.',
    ),
    stat: Optional[str] = Field(
        None,
        description='The statistic of the metric.',
    ),
    configuration: Optional[Dict] = Field(
        None,
        description='The configuration for the anomaly detection model.',
    ),
    single_metric_anomaly_detector: Optional[Dict] = Field(
        None,
        description='A single metric anomaly detector to create or update.',
    ),
    metric_math_anomaly_detector: Optional[Dict] = Field(
        None,
        description='A metric math anomaly detector to create or update.',
    ),
):
    """Creates or updates an anomaly detection model for a CloudWatch metric."""
    try:
        kwargs = {
            'Namespace': namespace,
            'MetricName': metric_name,
            'Dimensions': dimensions,
            'Stat': stat,
            'Configuration': configuration,
            'SingleMetricAnomalyDetector': single_metric_anomaly_detector,
            'MetricMathAnomalyDetector': metric_math_anomaly_detector,
        }
        cloudwatch_client.put_anomaly_detector(**remove_null_values(kwargs))
        logger.info(f'Successfully created or updated anomaly detector for {namespace}:{metric_name}')
        return {"status": f"Successfully created or updated anomaly detector for {namespace}:{metric_name}"}
    except Exception as e:
        logger.error(f'Error in put_anomaly_detector_tool: {str(e)}')
        await ctx.error(f'Error creating or updating anomaly detector: {str(e)}')
        raise


# Tag API implementations
@mcp.tool(name='list_tags_for_resource')
async def list_tags_for_resource_tool(
    ctx: Context,
    resource_arn: str = Field(
        ...,
        description='The ARN of the CloudWatch resource.',
    ),
):
    """Lists the tags for a CloudWatch resource."""
    try:
        response = cloudwatch_client.list_tags_for_resource(
            ResourceARN=resource_arn
        )
        return {
            "tags": response.get('Tags', [])
        }
    except Exception as e:
        logger.error(f'Error in list_tags_for_resource_tool: {str(e)}')
        await ctx.error(f'Error listing tags for resource: {str(e)}')
        raise


@mcp.tool(name='tag_resource')
async def tag_resource_tool(
    ctx: Context,
    resource_arn: str = Field(
        ...,
        description='The ARN of the CloudWatch resource.',
    ),
    tags: List[Dict[str, str]] = Field(
        ...,
        description='The list of tags to add to the resource. Each tag is a dictionary with "Key" and "Value" keys.',
    ),
):
    """Adds or modifies tags for a CloudWatch resource."""
    try:
        cloudwatch_client.tag_resource(
            ResourceARN=resource_arn,
            Tags=tags
        )
        logger.info(f'Successfully tagged resource: {resource_arn}')
        return {"status": f"Successfully tagged resource: {resource_arn}"}
    except Exception as e:
        logger.error(f'Error in tag_resource_tool: {str(e)}')
        await ctx.error(f'Error tagging resource: {str(e)}')
        raise


@mcp.tool(name='untag_resource')
async def untag_resource_tool(
    ctx: Context,
    resource_arn: str = Field(
        ...,
        description='The ARN of the CloudWatch resource.',
    ),
    tag_keys: List[str] = Field(
        ...,
        description='The list of tag keys to remove from the resource.',
    ),
):
    """Removes tags from a CloudWatch resource."""
    try:
        cloudwatch_client.untag_resource(
            ResourceARN=resource_arn,
            TagKeys=tag_keys
        )
        logger.info(f'Successfully untagged resource: {resource_arn}')
        return {"status": f"Successfully untagged resource: {resource_arn}"}
    except Exception as e:
        logger.error(f'Error in untag_resource_tool: {str(e)}')
        await ctx.error(f'Error untagging resource: {str(e)}')
        raise


# Alarm API implementations
@mcp.tool(name='describe_alarm_history')
async def describe_alarm_history_tool(
    ctx: Context,
    alarm_name: Optional[str] = Field(
        None,
        description='The name of the alarm to retrieve history for.',
    ),
    alarm_types: Optional[List[str]] = Field(
        None,
        description='The type of alarm histories to retrieve. Valid values are CompositeAlarm and MetricAlarm.',
    ),
    history_item_type: Optional[str] = Field(
        None,
        description='The type of alarm history item to retrieve. Valid values are ConfigurationUpdate, StateUpdate, and Action.',
    ),
    start_date: Optional[str] = Field(
        None,
        description='ISO 8601 formatted start date for the alarm history (e.g., "2025-04-19T20:00:00+00:00").',
    ),
    end_date: Optional[str] = Field(
        None,
        description='ISO 8601 formatted end date for the alarm history (e.g., "2025-04-19T21:00:00+00:00").',
    ),
    max_records: Optional[int] = Field(
        None,
        description='The maximum number of alarm history records to retrieve.',
    ),
    next_token: Optional[str] = Field(
        None,
        description='The token for the next set of results.',
    ),
):
    """Retrieves the history for the specified alarm."""
    try:
        kwargs = {
            'AlarmName': alarm_name,
            'AlarmTypes': alarm_types,
            'HistoryItemType': history_item_type,
            'StartDate': datetime.datetime.fromisoformat(start_date) if start_date else None,
            'EndDate': datetime.datetime.fromisoformat(end_date) if end_date else None,
            'MaxRecords': max_records,
            'NextToken': next_token,
        }
        
        response = cloudwatch_client.describe_alarm_history(**remove_null_values(kwargs))
        
        # Convert to a simpler format
        history_items = []
        for item in response.get('AlarmHistoryItems', []):
            history_items.append({
                'alarmName': item.get('AlarmName'),
                'timestamp': item.get('Timestamp').isoformat() if hasattr(item.get('Timestamp'), 'isoformat') else str(item.get('Timestamp')),
                'historyItemType': item.get('HistoryItemType'),
                'historySummary': item.get('HistorySummary'),
                'historyData': item.get('HistoryData'),
            })
        
        return {
            'alarmHistoryItems': history_items,
            'nextToken': response.get('NextToken')
        }
    
    except Exception as e:
        logger.error(f'Error in describe_alarm_history_tool: {str(e)}')
        await ctx.error(f'Error retrieving alarm history: {str(e)}')
        raise


@mcp.tool(name='describe_alarms')
async def describe_alarms_tool(
    ctx: Context,
    alarm_names: Optional[List[str]] = Field(
        None,
        description='The names of the alarms to retrieve information for.',
    ),
    alarm_name_prefix: Optional[str] = Field(
        None,
        description='The alarm name prefix to filter by.',
    ),
    alarm_types: Optional[List[str]] = Field(
        None,
        description='The type of alarms to retrieve. Valid values are CompositeAlarm and MetricAlarm.',
    ),
    state_value: Optional[str] = Field(
        None,
        description='The state value to filter by. Valid values are OK, ALARM, and INSUFFICIENT_DATA.',
    ),
    action_prefix: Optional[str] = Field(
        None,
        description='The action name prefix to filter by.',
    ),
    max_records: Optional[int] = Field(
        None,
        description='The maximum number of alarm records to retrieve.',
    ),
    next_token: Optional[str] = Field(
        None,
        description='The token for the next set of results.',
    ),
):
    """Retrieves information about the specified alarms."""
    try:
        kwargs = {
            'AlarmNames': alarm_names,
            'AlarmNamePrefix': alarm_name_prefix,
            'AlarmTypes': alarm_types,
            'StateValue': state_value,
            'ActionPrefix': action_prefix,
            'MaxRecords': max_records,
            'NextToken': next_token,
        }
        
        response = cloudwatch_client.describe_alarms(**remove_null_values(kwargs))
        
        # Convert to a simpler format
        metric_alarms = []
        for alarm in response.get('MetricAlarms', []):
            metric_alarms.append({
                'alarmName': alarm.get('AlarmName'),
                'alarmArn': alarm.get('AlarmArn'),
                'stateValue': alarm.get('StateValue'),
                'stateReason': alarm.get('StateReason'),
                'metricName': alarm.get('MetricName'),
                'namespace': alarm.get('Namespace'),
                'statistic': alarm.get('Statistic'),
                'dimensions': alarm.get('Dimensions'),
                'period': alarm.get('Period'),
                'threshold': alarm.get('Threshold'),
                'comparisonOperator': alarm.get('ComparisonOperator'),
            })
        
        composite_alarms = []
        for alarm in response.get('CompositeAlarms', []):
            composite_alarms.append({
                'alarmName': alarm.get('AlarmName'),
                'alarmArn': alarm.get('AlarmArn'),
                'stateValue': alarm.get('StateValue'),
                'stateReason': alarm.get('StateReason'),
                'alarmRule': alarm.get('AlarmRule'),
            })
        
        return {
            'metricAlarms': metric_alarms,
            'compositeAlarms': composite_alarms,
            'nextToken': response.get('NextToken')
        }
    
    except Exception as e:
        logger.error(f'Error in describe_alarms_tool: {str(e)}')
        await ctx.error(f'Error retrieving alarms: {str(e)}')
        raise


@mcp.tool(name='describe_alarms_for_metric')
async def describe_alarms_for_metric_tool(
    ctx: Context,
    namespace: str = Field(
        ...,
        description='The namespace of the metric.',
    ),
    metric_name: str = Field(
        ...,
        description='The name of the metric.',
    ),
    dimensions: Optional[List[Dict[str, str]]] = Field(
        None,
        description='The dimensions of the metric. Each dimension is a dictionary with "Name" and "Value" keys.',
    ),
    statistic: Optional[str] = Field(
        None,
        description='The statistic for the metric. Valid values include SampleCount, Average, Sum, Minimum, and Maximum.',
    ),
    extended_statistic: Optional[str] = Field(
        None,
        description='The extended statistic for the metric, such as p99 or p95.',
    ),
):
    """Retrieves all alarms for a specified metric."""
    try:
        kwargs = {
            'MetricName': metric_name,
            'Namespace': namespace,
            'Dimensions': dimensions,
            'Statistic': statistic,
            'ExtendedStatistic': extended_statistic,
        }
        
        response = cloudwatch_client.describe_alarms_for_metric(**remove_null_values(kwargs))
        
        # Convert to a simpler format
        metric_alarms = []
        for alarm in response.get('MetricAlarms', []):
            metric_alarms.append({
                'alarmName': alarm.get('AlarmName'),
                'alarmArn': alarm.get('AlarmArn'),
                'stateValue': alarm.get('StateValue'),
                'stateReason': alarm.get('StateReason'),
                'metricName': alarm.get('MetricName'),
                'namespace': alarm.get('Namespace'),
                'statistic': alarm.get('Statistic'),
                'dimensions': alarm.get('Dimensions'),
                'period': alarm.get('Period'),
                'threshold': alarm.get('Threshold'),
                'comparisonOperator': alarm.get('ComparisonOperator'),
            })
        
        return {
            'metricAlarms': metric_alarms
        }
    
    except Exception as e:
        logger.error(f'Error in describe_alarms_for_metric_tool: {str(e)}')
        await ctx.error(f'Error retrieving alarms for metric: {str(e)}')
        raise


@mcp.tool(name='put_composite_alarm')
async def put_composite_alarm_tool(
    ctx: Context,
    alarm_name: str = Field(
        ...,
        description='The name of the composite alarm.',
    ),
    alarm_rule: str = Field(
        ...,
        description='The rule expression that specifies when the composite alarm goes into ALARM state.',
    ),
    actions_enabled: Optional[bool] = Field(
        None,
        description='Indicates whether actions should be executed during any changes to the alarm state.',
    ),
    alarm_actions: Optional[List[str]] = Field(
        None,
        description='The actions to execute when this alarm transitions to the ALARM state.',
    ),
    alarm_description: Optional[str] = Field(
        None,
        description='The description for the composite alarm.',
    ),
    insufficient_data_actions: Optional[List[str]] = Field(
        None,
        description='The actions to execute when this alarm transitions to the INSUFFICIENT_DATA state.',
    ),
    ok_actions: Optional[List[str]] = Field(
        None,
        description='The actions to execute when this alarm transitions to the OK state.',
    ),
):
    """Creates or updates a composite alarm."""
    try:
        kwargs = {
            'AlarmName': alarm_name,
            'AlarmRule': alarm_rule,
            'ActionsEnabled': actions_enabled,
            'AlarmActions': alarm_actions,
            'AlarmDescription': alarm_description,
            'InsufficientDataActions': insufficient_data_actions,
            'OKActions': ok_actions,
        }
        
        cloudwatch_client.put_composite_alarm(**remove_null_values(kwargs))
        
        logger.info(f'Successfully created or updated composite alarm: {alarm_name}')
        return {"status": f"Successfully created or updated composite alarm: {alarm_name}"}
    
    except Exception as e:
        logger.error(f'Error in put_composite_alarm_tool: {str(e)}')
        await ctx.error(f'Error creating or updating composite alarm: {str(e)}')
        raise


@mcp.tool(name='put_metric_alarm')
async def put_metric_alarm_tool(
    ctx: Context,
    alarm_name: str = Field(
        ...,
        description='The name of the alarm.',
    ),
    comparison_operator: str = Field(
        ...,
        description='The arithmetic operation to use when comparing the specified statistic and threshold.',
    ),
    evaluation_periods: int = Field(
        ...,
        description='The number of periods over which data is compared to the specified threshold.',
    ),
    metric_name: Optional[str] = Field(
        None,
        description='The name of the metric associated with the alarm.',
    ),
    namespace: Optional[str] = Field(
        None,
        description='The namespace of the metric associated with the alarm.',
    ),
    period: Optional[int] = Field(
        None,
        description='The period, in seconds, over which the statistic is applied.',
    ),
    statistic: Optional[str] = Field(
        None,
        description='The statistic for the metric.',
    ),
    threshold: Optional[float] = Field(
        None,
        description='The value against which the specified statistic is compared.',
    ),
    actions_enabled: Optional[bool] = Field(
        None,
        description='Indicates whether actions should be executed during any changes to the alarm state.',
    ),
    alarm_actions: Optional[List[str]] = Field(
        None,
        description='The actions to execute when this alarm transitions to the ALARM state.',
    ),
    alarm_description: Optional[str] = Field(
        None,
        description='The description for the alarm.',
    ),
    dimensions: Optional[List[Dict[str, str]]] = Field(
        None,
        description='The dimensions for the metric.',
    ),
    insufficient_data_actions: Optional[List[str]] = Field(
        None,
        description='The actions to execute when this alarm transitions to the INSUFFICIENT_DATA state.',
    ),
    ok_actions: Optional[List[str]] = Field(
        None,
        description='The actions to execute when this alarm transitions to the OK state.',
    ),
    unit: Optional[str] = Field(
        None,
        description='The unit of the metric.',
    ),
):
    """Creates or updates a metric alarm."""
    try:
        kwargs = {
            'AlarmName': alarm_name,
            'ComparisonOperator': comparison_operator,
            'EvaluationPeriods': evaluation_periods,
            'MetricName': metric_name,
            'Namespace': namespace,
            'Period': period,
            'Statistic': statistic,
            'Threshold': threshold,
            'ActionsEnabled': actions_enabled,
            'AlarmActions': alarm_actions,
            'AlarmDescription': alarm_description,
            'Dimensions': dimensions,
            'InsufficientDataActions': insufficient_data_actions,
            'OKActions': ok_actions,
            'Unit': unit,
        }
        
        cloudwatch_client.put_metric_alarm(**remove_null_values(kwargs))
        
        logger.info(f'Successfully created or updated metric alarm: {alarm_name}')
        return {"status": f"Successfully created or updated metric alarm: {alarm_name}"}
    
    except Exception as e:
        logger.error(f'Error in put_metric_alarm_tool: {str(e)}')
        await ctx.error(f'Error creating or updating metric alarm: {str(e)}')
        raise


@mcp.tool(name='delete_alarms')
async def delete_alarms_tool(
    ctx: Context,
    alarm_names: List[str] = Field(
        ...,
        description='The names of the alarms to delete.',
    ),
):
    """Deletes the specified CloudWatch alarms."""
    try:
        cloudwatch_client.delete_alarms(
            AlarmNames=alarm_names
        )
        
        logger.info(f'Successfully deleted {len(alarm_names)} alarms')
        return {"status": f"Successfully deleted {len(alarm_names)} alarms"}
    
    except Exception as e:
        logger.error(f'Error in delete_alarms_tool: {str(e)}')
        await ctx.error(f'Error deleting alarms: {str(e)}')
        raise


@mcp.tool(name='disable_alarm_actions')
async def disable_alarm_actions_tool(
    ctx: Context,
    alarm_names: List[str] = Field(
        ...,
        description='The names of the alarms to disable actions for.',
    ),
):
    """Disables actions for the specified alarms."""
    try:
        cloudwatch_client.disable_alarm_actions(
            AlarmNames=alarm_names
        )
        
        logger.info(f'Successfully disabled actions for {len(alarm_names)} alarms')
        return {"status": f"Successfully disabled actions for {len(alarm_names)} alarms"}
    
    except Exception as e:
        logger.error(f'Error in disable_alarm_actions_tool: {str(e)}')
        await ctx.error(f'Error disabling alarm actions: {str(e)}')
        raise


@mcp.tool(name='enable_alarm_actions')
async def enable_alarm_actions_tool(
    ctx: Context,
    alarm_names: List[str] = Field(
        ...,
        description='The names of the alarms to enable actions for.',
    ),
):
    """Enables actions for the specified alarms."""
    try:
        cloudwatch_client.enable_alarm_actions(
            AlarmNames=alarm_names
        )
        
        logger.info(f'Successfully enabled actions for {len(alarm_names)} alarms')
        return {"status": f"Successfully enabled actions for {len(alarm_names)} alarms"}
    
    except Exception as e:
        logger.error(f'Error in enable_alarm_actions_tool: {str(e)}')
        await ctx.error(f'Error enabling alarm actions: {str(e)}')
        raise


@mcp.tool(name='set_alarm_state')
async def set_alarm_state_tool(
    ctx: Context,
    alarm_name: str = Field(
        ...,
        description='The name of the alarm.',
    ),
    state_value: str = Field(
        ...,
        description='The value of the state. Valid values are OK, ALARM, and INSUFFICIENT_DATA.',
    ),
    state_reason: str = Field(
        ...,
        description='The reason for the state change.',
    ),
    state_reason_data: Optional[str] = Field(
        None,
        description='The reason data for the state change, in JSON format.',
    ),
):
    """Temporarily sets the state of an alarm."""
    try:
        kwargs = {
            'AlarmName': alarm_name,
            'StateValue': state_value,
            'StateReason': state_reason,
            'StateReasonData': state_reason_data,
        }
        
        cloudwatch_client.set_alarm_state(**remove_null_values(kwargs))
        
        logger.info(f'Successfully set alarm state for {alarm_name} to {state_value}')
        return {"status": f"Successfully set alarm state for {alarm_name} to {state_value}"}
    
    except Exception as e:
        logger.error(f'Error in set_alarm_state_tool: {str(e)}')
        await ctx.error(f'Error setting alarm state: {str(e)}')
        raise


def main():
    """Run the MCP server."""
    mcp.run()
    
    logger.info('CloudWatch Metrics MCP server started')


if __name__ == '__main__':
    main()