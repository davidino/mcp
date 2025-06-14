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

"""CloudWatch Insight Rules tool implementation."""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from loguru import logger
from mcp.server.fastmcp import Context

from awslabs.cloudwatch_mcp_server.services.insight_rule_service import InsightRuleService
from awslabs.cloudwatch_mcp_server.services.client_factory import ClientFactory


class InsightRulesOperation(str, Enum):
    """Enum for CloudWatch Insight Rules operations."""
    DELETE_INSIGHT_RULES = "delete_insight_rules"
    DESCRIBE_INSIGHT_RULES = "describe_insight_rules"
    DISABLE_INSIGHT_RULES = "disable_insight_rules"
    ENABLE_INSIGHT_RULES = "enable_insight_rules"
    GET_INSIGHT_RULE_REPORT = "get_insight_rule_report"
    LIST_MANAGED_INSIGHT_RULES = "list_managed_insight_rules"
    PUT_INSIGHT_RULE = "put_insight_rule"
    PUT_MANAGED_INSIGHT_RULES = "put_managed_insight_rules"


class InsightRulesTool:
    """Tool for working with CloudWatch Insight Rules."""
    
    def __init__(self, region_name: str = "us-east-1"):
        """Initialize the CloudWatch Insight Rules tool.
        
        Args:
            region_name: AWS region name.
        """
        self.region_name = region_name
        cloudwatch_client = ClientFactory.get_cloudwatch_client(region_name=region_name)
        self.insight_rule_service = InsightRuleService(cloudwatch_client)
    
    async def cloudwatch_insight_rules(
        self,
        ctx: Context,
        operation: InsightRulesOperation,
        # Parameters for delete_insight_rules, disable_insight_rules, enable_insight_rules
        rule_names: Optional[List[str]] = None,
        # Parameters for get_insight_rule_report
        rule_name: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        period: Optional[int] = None,
        max_contributor_count: Optional[int] = None,
        metrics: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        # Parameters for list_managed_insight_rules
        resource_arn: Optional[str] = None,
        # Parameters for put_insight_rule
        rule_definition: Optional[Union[str, Dict[str, Any]]] = None,
        rule_state: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        # Parameters for put_managed_insight_rules
        managed_rules: Optional[List[Dict]] = None,
        # Pagination parameters
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Perform CloudWatch Insight Rules operations.
        
        Args:
            ctx: The MCP context.
            operation: The operation to perform.
            
            # Parameters for delete_insight_rules, disable_insight_rules, enable_insight_rules
            rule_names: The names of the rules to delete, disable, or enable.
            
            # Parameters for get_insight_rule_report
            rule_name: The name of the rule to get a report for.
            start_time: The start time for the report (ISO 8601 format).
            end_time: The end time for the report (ISO 8601 format).
            period: The period in seconds for the report.
            max_contributor_count: The maximum number of contributors to include.
            metrics: The metrics to include in the report.
            order_by: How to order the contributors in the report.
            
            # Parameters for list_managed_insight_rules
            resource_arn: The ARN of the resource to list managed rules for.
            
            # Parameters for put_insight_rule
            rule_definition: The definition of the rule (JSON string or dict).
            rule_state: The state of the rule (ENABLED or DISABLED).
            tags: Tags to associate with the rule.
            
            # Parameters for put_managed_insight_rules
            managed_rules: The managed rules to create.
            
            # Pagination parameters
            max_results: The maximum number of results to return.
            next_token: The token for the next set of results.
            
        Returns:
            The result of the operation, which varies based on the operation type.
        """
        try:
            if operation == InsightRulesOperation.DELETE_INSIGHT_RULES:
                if not rule_names:
                    raise ValueError("rule_names is required for delete_insight_rules operation")
                
                return await self._delete_insight_rules(
                    ctx,
                    rule_names=rule_names,
                )
            if operation == InsightRulesOperation.DESCRIBE_INSIGHT_RULES:
                return await self._describe_insight_rules(
                    ctx,
                    max_results=max_results,
                    next_token=next_token,
                )
            if operation == InsightRulesOperation.DISABLE_INSIGHT_RULES:
                if not rule_names:
                    raise ValueError("rule_names is required for disable_insight_rules operation")
                
                return await self._disable_insight_rules(
                    ctx,
                    rule_names=rule_names,
                )
            if operation == InsightRulesOperation.ENABLE_INSIGHT_RULES:
                if not rule_names:
                    raise ValueError("rule_names is required for enable_insight_rules operation")
                
                return await self._enable_insight_rules(
                    ctx,
                    rule_names=rule_names,
                )
            if operation == InsightRulesOperation.GET_INSIGHT_RULE_REPORT:
                if not rule_name or not start_time or not end_time or not period:
                    raise ValueError("rule_name, start_time, end_time, and period are required for get_insight_rule_report operation")
                
                return await self._get_insight_rule_report(
                    ctx,
                    rule_name=rule_name,
                    start_time=start_time,
                    end_time=end_time,
                    period=period,
                    max_contributor_count=max_contributor_count,
                    metrics=metrics,
                    order_by=order_by,
                )
            if operation == InsightRulesOperation.LIST_MANAGED_INSIGHT_RULES:
                if not resource_arn:
                    raise ValueError("resource_arn is required for list_managed_insight_rules operation")
                
                return await self._list_managed_insight_rules(
                    ctx,
                    resource_arn=resource_arn,
                    max_results=max_results,
                    next_token=next_token,
                )
            if operation == InsightRulesOperation.PUT_INSIGHT_RULE:
                if not rule_name or not rule_definition:
                    raise ValueError("rule_name and rule_definition are required for put_insight_rule operation")
                
                return await self._put_insight_rule(
                    ctx,
                    rule_name=rule_name,
                    rule_definition=rule_definition,
                    rule_state=rule_state,
                    tags=tags,
                )
            if operation == InsightRulesOperation.PUT_MANAGED_INSIGHT_RULES:
                if not managed_rules:
                    raise ValueError("managed_rules is required for put_managed_insight_rules operation")
                
                return await self._put_managed_insight_rules(
                    ctx,
                    managed_rules=managed_rules,
                )
            else:
                raise ValueError(f"Unsupported operation: {operation}")
        except Exception as e:
            logger.error(f"Error in cloudwatch_insight_rules tool: {str(e)}")
            await ctx.error(f"CloudWatch Insight Rules operation failed: {str(e)}")
            raise
    
    async def _delete_insight_rules(
        self,
        ctx: Context,
        rule_names: List[str],
    ) -> Dict[str, Any]:
        """Deletes the specified Contributor Insights rules."""
        try:
            return await self.insight_rule_service.delete_insight_rules(
                rule_names=rule_names,
            )
        except Exception as e:
            logger.error(f"Error in delete_insight_rules: {str(e)}")
            await ctx.error(f"Failed to delete insight rules: {str(e)}")
            raise
    
    async def _describe_insight_rules(
        self,
        ctx: Context,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Returns a list of all Contributor Insights rules in your account."""
        try:
            return await self.insight_rule_service.describe_insight_rules(
                max_results=max_results,
                next_token=next_token,
            )
        except Exception as e:
            logger.error(f"Error in describe_insight_rules: {str(e)}")
            await ctx.error(f"Failed to describe insight rules: {str(e)}")
            raise
    
    async def _disable_insight_rules(
        self,
        ctx: Context,
        rule_names: List[str],
    ) -> Dict[str, Any]:
        """Disables the specified Contributor Insights rules."""
        try:
            return await self.insight_rule_service.disable_insight_rules(
                rule_names=rule_names,
            )
        except Exception as e:
            logger.error(f"Error in disable_insight_rules: {str(e)}")
            await ctx.error(f"Failed to disable insight rules: {str(e)}")
            raise
    
    async def _enable_insight_rules(
        self,
        ctx: Context,
        rule_names: List[str],
    ) -> Dict[str, Any]:
        """Enables the specified Contributor Insights rules."""
        try:
            return await self.insight_rule_service.enable_insight_rules(
                rule_names=rule_names,
            )
        except Exception as e:
            logger.error(f"Error in enable_insight_rules: {str(e)}")
            await ctx.error(f"Failed to enable insight rules: {str(e)}")
            raise
    
    async def _get_insight_rule_report(
        self,
        ctx: Context,
        rule_name: str,
        start_time: str,
        end_time: str,
        period: int,
        max_contributor_count: Optional[int] = None,
        metrics: Optional[List[str]] = None,
        order_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Returns data about the contributors for the specified rule."""
        try:
            return await self.insight_rule_service.get_insight_rule_report(
                rule_name=rule_name,
                start_time=start_time,
                end_time=end_time,
                period=period,
                max_contributor_count=max_contributor_count,
                metrics=metrics,
                order_by=order_by,
            )
        except Exception as e:
            logger.error(f"Error in get_insight_rule_report: {str(e)}")
            await ctx.error(f"Failed to get insight rule report: {str(e)}")
            raise
    
    async def _list_managed_insight_rules(
        self,
        ctx: Context,
        resource_arn: str,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Returns a list of managed Contributor Insights rules for a specific AWS resource."""
        try:
            return await self.insight_rule_service.list_managed_insight_rules(
                resource_arn=resource_arn,
                max_results=max_results,
                next_token=next_token,
            )
        except Exception as e:
            logger.error(f"Error in list_managed_insight_rules: {str(e)}")
            await ctx.error(f"Failed to list managed insight rules: {str(e)}")
            raise
    
    async def _put_insight_rule(
        self,
        ctx: Context,
        rule_name: str,
        rule_definition: Union[str, Dict[str, Any]],
        rule_state: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Creates a Contributor Insights rule."""
        try:
            # Convert dictionary to JSON string if needed
            if isinstance(rule_definition, dict):
                import json
                rule_definition = json.dumps(rule_definition)
                
            return await self.insight_rule_service.put_insight_rule(
                rule_name=rule_name,
                rule_definition=rule_definition,
                rule_state=rule_state,
                tags=tags,
            )
        except Exception as e:
            logger.error(f"Error in put_insight_rule: {str(e)}")
            await ctx.error(f"Failed to put insight rule: {str(e)}")
            raise
    
    async def _put_managed_insight_rules(
        self,
        ctx: Context,
        managed_rules: List[Dict],
    ) -> Dict[str, Any]:
        """Creates managed Contributor Insights rules for a specified AWS resource."""
        try:
            return await self.insight_rule_service.put_managed_insight_rules(
                managed_rules=managed_rules,
            )
        except Exception as e:
            logger.error(f"Error in put_managed_insight_rules: {str(e)}")
            await ctx.error(f"Failed to put managed insight rules: {str(e)}")
            raise
    
    def register(self, mcp_server):
        """Register the CloudWatch Insight Rules tool with the MCP server.
        
        Args:
            mcp_server: The MCP server to register the tool with.
        """
        mcp_server.tool(
            name='cloudwatch_insight_rules',
            description="""
            Comprehensive tool for working with CloudWatch Contributor Insights Rules. Supports:
            
            - Creating and managing Contributor Insights rules
            - Retrieving rule reports and data
            - Enabling and disabling rules
            - Managing managed rules for AWS resources
            
            Use this tool to gain insights into the top contributors to your CloudWatch metrics and logs.
            """
        )(self.cloudwatch_insight_rules)