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

"""CloudWatch Alarm API routes."""

from typing import Dict, List, Optional, Any
from mcp.server.fastmcp import Context
from pydantic import Field

from awslabs.cloudwatch_mcp_server.services.alarm_service import AlarmService
from awslabs.cloudwatch_mcp_server.services.client_factory import ClientFactory


# Initialize services
cloudwatch_client = ClientFactory.get_cloudwatch_client()
alarm_service = AlarmService(cloudwatch_client)


async def describe_alarm_history_route(
    ctx: Context,
    mcp,
    alarm_name: Optional[str] = Field(
        None,
        description='The name of the alarm to retrieve history for.',
    ),
    alarm_types: Optional[List[str]] = Field(
        None,
        description='The type of alarm histories to retrieve. Possible values: CompositeAlarm, MetricAlarm.',
    ),
    history_item_type: Optional[str] = Field(
        None,
        description='The type of alarm history item to retrieve. Possible values: ConfigurationUpdate, StateUpdate, Action.',
    ),
    start_date: Optional[str] = Field(
        None,
        description='The start date for the alarm history in ISO 8601 format.',
    ),
    end_date: Optional[str] = Field(
        None,
        description='The end date for the alarm history in ISO 8601 format.',
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
    """Route for describe_alarm_history API."""
    return await alarm_service.describe_alarm_history(
        alarm_name=alarm_name,
        alarm_types=alarm_types,
        history_item_type=history_item_type,
        start_date=start_date,
        end_date=end_date,
        max_records=max_records,
        next_token=next_token,
    )


async def describe_alarms_route(
    ctx: Context,
    mcp,
    alarm_names: Optional[List[str]] = Field(
        None,
        description='The names of the alarms to retrieve information about.',
    ),
    alarm_name_prefix: Optional[str] = Field(
        None,
        description='The alarm name prefix. Only alarms with names that start with this prefix will be returned.',
    ),
    alarm_types: Optional[List[str]] = Field(
        None,
        description='The type of alarms to retrieve. Possible values: CompositeAlarm, MetricAlarm.',
    ),
    state_value: Optional[str] = Field(
        None,
        description='The state value to filter by. Possible values: OK, ALARM, INSUFFICIENT_DATA.',
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
    """Route for describe_alarms API."""
    return await alarm_service.describe_alarms(
        alarm_names=alarm_names,
        alarm_name_prefix=alarm_name_prefix,
        alarm_types=alarm_types,
        state_value=state_value,
        action_prefix=action_prefix,
        max_records=max_records,
        next_token=next_token,
    )


async def describe_alarms_for_metric_route(
    ctx: Context,
    mcp,
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
        description='The statistic for the metric. Possible values include: SampleCount, Average, Sum, Minimum, Maximum.',
    ),
    extended_statistic: Optional[str] = Field(
        None,
        description='The extended statistic for the metric. Specify a percentile statistic (p0.0-p100).',
    ),
):
    """Route for describe_alarms_for_metric API."""
    return await alarm_service.describe_alarms_for_metric(
        namespace=namespace,
        metric_name=metric_name,
        dimensions=dimensions,
        statistic=statistic,
        extended_statistic=extended_statistic,
    )


async def put_composite_alarm_route(
    ctx: Context,
    mcp,
    alarm_name: str = Field(
        ...,
        description='The name of the alarm.',
    ),
    alarm_rule: str = Field(
        ...,
        description='The rule expression that defines the composite alarm.',
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
    insufficient_data_actions: Optional[List[str]] = Field(
        None,
        description='The actions to execute when this alarm transitions to the INSUFFICIENT_DATA state.',
    ),
    ok_actions: Optional[List[str]] = Field(
        None,
        description='The actions to execute when this alarm transitions to the OK state.',
    ),
):
    """Route for put_composite_alarm API."""
    return await alarm_service.put_composite_alarm(
        alarm_name=alarm_name,
        alarm_rule=alarm_rule,
        actions_enabled=actions_enabled,
        alarm_actions=alarm_actions,
        alarm_description=alarm_description,
        insufficient_data_actions=insufficient_data_actions,
        ok_actions=ok_actions,
    )


async def put_metric_alarm_route(
    ctx: Context,
    mcp,
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
        description='The statistic for the metric. Possible values include: SampleCount, Average, Sum, Minimum, Maximum.',
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
        description='The dimensions of the metric. Each dimension is a dictionary with "Name" and "Value" keys.',
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
        description='The unit of the metric associated with the alarm.',
    ),
):
    """Route for put_metric_alarm API."""
    return await alarm_service.put_metric_alarm(
        alarm_name=alarm_name,
        comparison_operator=comparison_operator,
        evaluation_periods=evaluation_periods,
        metric_name=metric_name,
        namespace=namespace,
        period=period,
        statistic=statistic,
        threshold=threshold,
        actions_enabled=actions_enabled,
        alarm_actions=alarm_actions,
        alarm_description=alarm_description,
        dimensions=dimensions,
        insufficient_data_actions=insufficient_data_actions,
        ok_actions=ok_actions,
        unit=unit,
    )


async def delete_alarms_route(
    ctx: Context,
    mcp,
    alarm_names: List[str] = Field(
        ...,
        description='The names of the alarms to delete.',
    ),
):
    """Route for delete_alarms API."""
    return await alarm_service.delete_alarms(
        alarm_names=alarm_names,
    )


async def disable_alarm_actions_route(
    ctx: Context,
    mcp,
    alarm_names: List[str] = Field(
        ...,
        description='The names of the alarms to disable actions for.',
    ),
):
    """Route for disable_alarm_actions API."""
    return await alarm_service.disable_alarm_actions(
        alarm_names=alarm_names,
    )


async def enable_alarm_actions_route(
    ctx: Context,
    mcp,
    alarm_names: List[str] = Field(
        ...,
        description='The names of the alarms to enable actions for.',
    ),
):
    """Route for enable_alarm_actions API."""
    return await alarm_service.enable_alarm_actions(
        alarm_names=alarm_names,
    )


async def set_alarm_state_route(
    ctx: Context,
    mcp,
    alarm_name: str = Field(
        ...,
        description='The name of the alarm.',
    ),
    state_value: str = Field(
        ...,
        description='The value of the state. Possible values: OK, ALARM, INSUFFICIENT_DATA.',
    ),
    state_reason: str = Field(
        ...,
        description='The reason that this alarm is set to this state.',
    ),
    state_reason_data: Optional[str] = Field(
        None,
        description='The reason data (JSON string) that this alarm is set to this state.',
    ),
):
    """Route for set_alarm_state API."""
    return await alarm_service.set_alarm_state(
        alarm_name=alarm_name,
        state_value=state_value,
        state_reason=state_reason,
        state_reason_data=state_reason_data,
    )


def register_routes(mcp_server):
    """Register all alarm routes with the MCP server."""
    mcp_server.tool(name='describe_alarm_history')(describe_alarm_history_route)
    mcp_server.tool(name='describe_alarms')(describe_alarms_route)
    mcp_server.tool(name='desc_alarms_for_metric')(describe_alarms_for_metric_route)
    mcp_server.tool(name='put_composite_alarm')(put_composite_alarm_route)
    mcp_server.tool(name='put_metric_alarm')(put_metric_alarm_route)
    mcp_server.tool(name='delete_alarms')(delete_alarms_route)
    mcp_server.tool(name='disable_alarm_actions')(disable_alarm_actions_route)
    mcp_server.tool(name='enable_alarm_actions')(enable_alarm_actions_route)
    mcp_server.tool(name='set_alarm_state')(set_alarm_state_route)