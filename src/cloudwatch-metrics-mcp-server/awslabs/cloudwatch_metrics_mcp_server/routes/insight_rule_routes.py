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

"""CloudWatch Insight Rule API routes."""

from typing import Dict, List, Optional
from mcp.server.fastmcp import Context
from pydantic import Field

from awslabs.cloudwatch_metrics_mcp_server.services.insight_rule_service import InsightRuleService
from awslabs.cloudwatch_metrics_mcp_server.services.client_factory import ClientFactory


# Initialize services
cloudwatch_client = ClientFactory.get_cloudwatch_client()
insight_rule_service = InsightRuleService(cloudwatch_client)


async def delete_insight_rules_route(
    ctx: Context,
    mcp,
    rule_names: List[str] = Field(
        ...,
        description='The names of the rules to delete.',
    ),
):
    """Route for delete_insight_rules API."""
    return await insight_rule_service.delete_insight_rules(
        rule_names=rule_names,
    )


async def describe_insight_rules_route(
    ctx: Context,
    mcp,
    next_token: Optional[str] = Field(
        None,
        description='The token for the next set of results.',
    ),
    max_results: Optional[int] = Field(
        None,
        description='The maximum number of results to return.',
    ),
):
    """Route for describe_insight_rules API."""
    return await insight_rule_service.describe_insight_rules(
        next_token=next_token,
        max_results=max_results,
    )


async def disable_insight_rules_route(
    ctx: Context,
    mcp,
    rule_names: List[str] = Field(
        ...,
        description='The names of the rules to disable.',
    ),
):
    """Route for disable_insight_rules API."""
    return await insight_rule_service.disable_insight_rules(
        rule_names=rule_names,
    )


async def enable_insight_rules_route(
    ctx: Context,
    mcp,
    rule_names: List[str] = Field(
        ...,
        description='The names of the rules to enable.',
    ),
):
    """Route for enable_insight_rules API."""
    return await insight_rule_service.enable_insight_rules(
        rule_names=rule_names,
    )


async def get_insight_rule_report_route(
    ctx: Context,
    mcp,
    rule_name: str = Field(
        ...,
        description='The name of the rule.',
    ),
    start_time: str = Field(
        ...,
        description='ISO 8601 formatted start time for the report (e.g., "2025-04-19T20:00:00+00:00").',
    ),
    end_time: str = Field(
        ...,
        description='ISO 8601 formatted end time for the report (e.g., "2025-04-19T21:00:00+00:00").',
    ),
    period: int = Field(
        ...,
        description='The period, in seconds, to use for the statistics in the report.',
    ),
    max_contributor_count: Optional[int] = Field(
        None,
        description='The maximum number of contributors to include in the report.',
    ),
    metrics: Optional[List[str]] = Field(
        None,
        description='The metrics to include in the report.',
    ),
    order_by: Optional[str] = Field(
        None,
        description='Determines how the contributors are ordered in the report.',
    ),
):
    """Route for get_insight_rule_report API."""
    return await insight_rule_service.get_insight_rule_report(
        rule_name=rule_name,
        start_time=start_time,
        end_time=end_time,
        period=period,
        max_contributor_count=max_contributor_count,
        metrics=metrics,
        order_by=order_by,
    )


async def list_managed_insight_rules_route(
    ctx: Context,
    mcp,
    resource_arn: str = Field(
        ...,
        description='The ARN of the resource.',
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
    """Route for list_managed_insight_rules API."""
    return await insight_rule_service.list_managed_insight_rules(
        resource_arn=resource_arn,
        next_token=next_token,
        max_results=max_results,
    )


async def put_insight_rule_route(
    ctx: Context,
    mcp,
    rule_name: str = Field(
        ...,
        description='The name of the rule.',
    ),
    rule_definition: str = Field(
        ...,
        description='The definition of the rule, as a JSON string.',
    ),
    rule_state: Optional[str] = Field(
        None,
        description='The state of the rule. Valid values are ENABLED and DISABLED.',
    ),
    tags: Optional[Dict[str, str]] = Field(
        None,
        description='A map of key-value pairs to associate with the rule.',
    ),
):
    """Route for put_insight_rule API."""
    return await insight_rule_service.put_insight_rule(
        rule_name=rule_name,
        rule_definition=rule_definition,
        rule_state=rule_state,
        tags=tags,
    )


async def put_managed_insight_rules_route(
    ctx: Context,
    mcp,
    managed_rules: List[Dict] = Field(
        ...,
        description='The managed rules to create.',
    ),
):
    """Route for put_managed_insight_rules API."""
    return await insight_rule_service.put_managed_insight_rules(
        managed_rules=managed_rules,
    )


def register_routes(mcp_server):
    """Register all insight rule routes with the MCP server."""
    mcp_server.tool(name='delete_insight_rules')(delete_insight_rules_route)
    mcp_server.tool(name='desc_insight_rules')(describe_insight_rules_route)
    mcp_server.tool(name='disable_insight_rules')(disable_insight_rules_route)
    mcp_server.tool(name='enable_insight_rules')(enable_insight_rules_route)
    mcp_server.tool(name='get_insight_rule_report')(get_insight_rule_report_route)
    mcp_server.tool(name='list_managed_insight_rules')(list_managed_insight_rules_route)
    mcp_server.tool(name='put_insight_rule')(put_insight_rule_route)
    mcp_server.tool(name='put_managed_insight_rules')(put_managed_insight_rules_route)