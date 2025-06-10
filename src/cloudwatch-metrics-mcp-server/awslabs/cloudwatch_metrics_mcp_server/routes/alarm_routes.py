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

from awslabs.cloudwatch_metrics_mcp_server.services.alarm_service import AlarmService
from awslabs.cloudwatch_metrics_mcp_server.services.client_factory import ClientFactory


# Initialize services
cloudwatch_client = ClientFactory.get_cloudwatch_client()
alarm_service = AlarmService(cloudwatch_client)


async def describe_alarm_history_route(
    ctx: Context,
    mcp,
    alarm_name: Optional[str] = None,
    alarm_types: Optional[List[str]] = None,
    history_item_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    max_records: Optional[int] = None,
    next_token: Optional[str] = None,
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
    alarm_names: Optional[List[str]] = None,
    alarm_name_prefix: Optional[str] = None,
    alarm_types: Optional[List[str]] = None,
    state_value: Optional[str] = None,
    action_prefix: Optional[str] = None,
    max_records: Optional[int] = None,
    next_token: Optional[str] = None,
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
    namespace: str,
    metric_name: str,
    dimensions: Optional[List[Dict[str, str]]] = None,
    statistic: Optional[str] = None,
    extended_statistic: Optional[str] = None,
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
    alarm_name: str,
    alarm_rule: str,
    actions_enabled: Optional[bool] = None,
    alarm_actions: Optional[List[str]] = None,
    alarm_description: Optional[str] = None,
    insufficient_data_actions: Optional[List[str]] = None,
    ok_actions: Optional[List[str]] = None,
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
    alarm_name: str,
    comparison_operator: str,
    evaluation_periods: int,
    metric_name: Optional[str] = None,
    namespace: Optional[str] = None,
    period: Optional[int] = None,
    statistic: Optional[str] = None,
    threshold: Optional[float] = None,
    actions_enabled: Optional[bool] = None,
    alarm_actions: Optional[List[str]] = None,
    alarm_description: Optional[str] = None,
    dimensions: Optional[List[Dict[str, str]]] = None,
    insufficient_data_actions: Optional[List[str]] = None,
    ok_actions: Optional[List[str]] = None,
    unit: Optional[str] = None,
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
    alarm_names: List[str],
):
    """Route for delete_alarms API."""
    return await alarm_service.delete_alarms(
        alarm_names=alarm_names,
    )


async def disable_alarm_actions_route(
    ctx: Context,
    mcp,
    alarm_names: List[str],
):
    """Route for disable_alarm_actions API."""
    return await alarm_service.disable_alarm_actions(
        alarm_names=alarm_names,
    )


async def enable_alarm_actions_route(
    ctx: Context,
    mcp,
    alarm_names: List[str],
):
    """Route for enable_alarm_actions API."""
    return await alarm_service.enable_alarm_actions(
        alarm_names=alarm_names,
    )


async def set_alarm_state_route(
    ctx: Context,
    mcp,
    alarm_name: str,
    state_value: str,
    state_reason: str,
    state_reason_data: Optional[str] = None,
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