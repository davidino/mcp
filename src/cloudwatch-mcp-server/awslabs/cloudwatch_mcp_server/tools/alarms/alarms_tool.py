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

"""CloudWatch Alarms tool implementation."""

from enum import Enum
from typing import Dict, List, Optional, Any, Literal
from loguru import logger
from mcp.server.fastmcp import Context

from awslabs.cloudwatch_mcp_server.services.alarm_service import AlarmService
from awslabs.cloudwatch_mcp_server.services.client_factory import ClientFactory


class AlarmsOperation(str, Enum):
    """Enum for CloudWatch Alarms operations."""
    DESCRIBE_ALARM_HISTORY = "describe_alarm_history"
    DESCRIBE_ALARMS = "describe_alarms"
    DESCRIBE_ALARMS_FOR_METRIC = "describe_alarms_for_metric"
    PUT_COMPOSITE_ALARM = "put_composite_alarm"
    PUT_METRIC_ALARM = "put_metric_alarm"
    DELETE_ALARMS = "delete_alarms"
    DISABLE_ALARM_ACTIONS = "disable_alarm_actions"
    ENABLE_ALARM_ACTIONS = "enable_alarm_actions"
    SET_ALARM_STATE = "set_alarm_state"


class AlarmsTool:
    """Tool for working with CloudWatch Alarms."""
    
    def __init__(self, region_name: str = "us-east-1"):
        """Initialize the CloudWatch Alarms tool.
        
        Args:
            region_name: AWS region name.
        """
        self.region_name = region_name
        cloudwatch_client = ClientFactory.get_cloudwatch_client(region_name=region_name)
        self.alarms_service = AlarmService(cloudwatch_client)
    
    async def cloudwatch_alarms(
        self,
        ctx: Context,
        operation: AlarmsOperation,
        # Parameters for describe_alarm_history
        alarm_name: Optional[str] = None,
        alarm_types: Optional[List[str]] = None,
        history_item_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        # Parameters for describe_alarms
        alarm_names: Optional[List[str]] = None,
        alarm_name_prefix: Optional[str] = None,
        state_value: Optional[str] = None,
        action_prefix: Optional[str] = None,
        # Parameters for describe_alarms_for_metric
        namespace: Optional[str] = None,
        metric_name: Optional[str] = None,
        dimensions: Optional[List[Dict[str, str]]] = None,
        statistic: Optional[str] = None,
        extended_statistic: Optional[str] = None,
        # Parameters for put_composite_alarm
        alarm_rule: Optional[str] = None,
        # Parameters for put_metric_alarm
        comparison_operator: Optional[str] = None,
        evaluation_periods: Optional[int] = None,
        period: Optional[int] = None,
        threshold: Optional[float] = None,
        unit: Optional[str] = None,
        # Common parameters for put operations
        actions_enabled: Optional[bool] = None,
        alarm_actions: Optional[List[str]] = None,
        alarm_description: Optional[str] = None,
        insufficient_data_actions: Optional[List[str]] = None,
        ok_actions: Optional[List[str]] = None,
        # Parameters for set_alarm_state
        state_reason: Optional[str] = None,
        state_reason_data: Optional[str] = None,
        # Pagination parameters
        max_records: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Perform CloudWatch Alarms operations.
        
        Args:
            ctx: The MCP context.
            operation: The operation to perform.
            
            # Parameters for describe_alarm_history
            alarm_name: The name of the alarm to retrieve history for.
            alarm_types: The type of alarm to retrieve history for.
            history_item_type: The type of alarm history item to retrieve.
            start_date: The start date for the alarm history.
            end_date: The end date for the alarm history.
            
            # Parameters for describe_alarms
            alarm_names: The names of the alarms to retrieve.
            alarm_name_prefix: The prefix for the alarm names to retrieve.
            state_value: The state value to filter alarms by.
            action_prefix: The action prefix to filter alarms by.
            
            # Parameters for describe_alarms_for_metric
            namespace: The namespace of the metric.
            metric_name: The name of the metric.
            dimensions: The dimensions of the metric.
            statistic: The statistic of the metric.
            extended_statistic: The extended statistic of the metric.
            
            # Parameters for put_composite_alarm
            alarm_rule: The rule for the composite alarm.
            
            # Parameters for put_metric_alarm
            comparison_operator: The comparison operator for the metric alarm.
            evaluation_periods: The number of periods to evaluate the metric.
            period: The period in seconds over which the statistic is applied.
            threshold: The threshold value to compare with the metric.
            unit: The unit of the metric.
            
            # Common parameters for put operations
            actions_enabled: Whether actions are enabled for the alarm.
            alarm_actions: The actions to execute when the alarm transitions to ALARM state.
            alarm_description: The description of the alarm.
            insufficient_data_actions: The actions to execute when the alarm transitions to INSUFFICIENT_DATA state.
            ok_actions: The actions to execute when the alarm transitions to OK state.
            
            # Parameters for set_alarm_state
            state_reason: The reason for the alarm state change.
            state_reason_data: The reason data for the alarm state change.
            
            # Pagination parameters
            max_records: The maximum number of records to return.
            next_token: The token for the next set of records.
            
        Returns:
            The result of the operation, which varies based on the operation type.
        """
        try:
            if operation == AlarmsOperation.DESCRIBE_ALARM_HISTORY:
                return await self._describe_alarm_history(
                    ctx,
                    alarm_name=alarm_name,
                    alarm_types=alarm_types,
                    history_item_type=history_item_type,
                    start_date=start_date,
                    end_date=end_date,
                    max_records=max_records,
                    next_token=next_token,
                )
            elif operation == AlarmsOperation.DESCRIBE_ALARMS:
                return await self._describe_alarms(
                    ctx,
                    alarm_names=alarm_names,
                    alarm_name_prefix=alarm_name_prefix,
                    alarm_types=alarm_types,
                    state_value=state_value,
                    action_prefix=action_prefix,
                    max_records=max_records,
                    next_token=next_token,
                )
            elif operation == AlarmsOperation.DESCRIBE_ALARMS_FOR_METRIC:
                if not namespace or not metric_name:
                    raise ValueError("namespace and metric_name are required for describe_alarms_for_metric operation")
                
                return await self._describe_alarms_for_metric(
                    ctx,
                    namespace=namespace,
                    metric_name=metric_name,
                    dimensions=dimensions,
                    statistic=statistic,
                    extended_statistic=extended_statistic,
                )
            elif operation == AlarmsOperation.PUT_COMPOSITE_ALARM:
                if not alarm_name or not alarm_rule:
                    raise ValueError("alarm_name and alarm_rule are required for put_composite_alarm operation")
                
                return await self._put_composite_alarm(
                    ctx,
                    alarm_name=alarm_name,
                    alarm_rule=alarm_rule,
                    actions_enabled=actions_enabled,
                    alarm_actions=alarm_actions,
                    alarm_description=alarm_description,
                    insufficient_data_actions=insufficient_data_actions,
                    ok_actions=ok_actions,
                )
            elif operation == AlarmsOperation.PUT_METRIC_ALARM:
                if not alarm_name or not comparison_operator or not evaluation_periods:
                    raise ValueError("alarm_name, comparison_operator, and evaluation_periods are required for put_metric_alarm operation")
                
                return await self._put_metric_alarm(
                    ctx,
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
            elif operation == AlarmsOperation.DELETE_ALARMS:
                if not alarm_names:
                    raise ValueError("alarm_names is required for delete_alarms operation")
                
                return await self._delete_alarms(
                    ctx,
                    alarm_names=alarm_names,
                )
            elif operation == AlarmsOperation.DISABLE_ALARM_ACTIONS:
                if not alarm_names:
                    raise ValueError("alarm_names is required for disable_alarm_actions operation")
                
                return await self._disable_alarm_actions(
                    ctx,
                    alarm_names=alarm_names,
                )
            elif operation == AlarmsOperation.ENABLE_ALARM_ACTIONS:
                if not alarm_names:
                    raise ValueError("alarm_names is required for enable_alarm_actions operation")
                
                return await self._enable_alarm_actions(
                    ctx,
                    alarm_names=alarm_names,
                )
            elif operation == AlarmsOperation.SET_ALARM_STATE:
                if not alarm_name or not state_value or not state_reason:
                    raise ValueError("alarm_name, state_value, and state_reason are required for set_alarm_state operation")
                
                return await self._set_alarm_state(
                    ctx,
                    alarm_name=alarm_name,
                    state_value=state_value,
                    state_reason=state_reason,
                    state_reason_data=state_reason_data,
                )
            else:
                raise ValueError(f"Unsupported operation: {operation}")
        except Exception as e:
            logger.error(f"Error in cloudwatch_alarms tool: {str(e)}")
            await ctx.error(f"CloudWatch Alarms operation failed: {str(e)}")
            raise
    
    async def _describe_alarm_history(
        self,
        ctx: Context,
        alarm_name: Optional[str] = None,
        alarm_types: Optional[List[str]] = None,
        history_item_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_records: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieves the history for the specified alarm."""
        try:
            return await self.alarms_service.describe_alarm_history(
                alarm_name=alarm_name,
                alarm_types=alarm_types,
                history_item_type=history_item_type,
                start_date=start_date,
                end_date=end_date,
                max_records=max_records,
                next_token=next_token,
            )
        except Exception as e:
            logger.error(f"Error in describe_alarm_history: {str(e)}")
            await ctx.error(f"Failed to describe alarm history: {str(e)}")
            raise
    
    async def _describe_alarms(
        self,
        ctx: Context,
        alarm_names: Optional[List[str]] = None,
        alarm_name_prefix: Optional[str] = None,
        alarm_types: Optional[List[str]] = None,
        state_value: Optional[str] = None,
        action_prefix: Optional[str] = None,
        max_records: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieves information about the specified alarms."""
        try:
            return await self.alarms_service.describe_alarms(
                alarm_names=alarm_names,
                alarm_name_prefix=alarm_name_prefix,
                alarm_types=alarm_types,
                state_value=state_value,
                action_prefix=action_prefix,
                max_records=max_records,
                next_token=next_token,
            )
        except Exception as e:
            logger.error(f"Error in describe_alarms: {str(e)}")
            await ctx.error(f"Failed to describe alarms: {str(e)}")
            raise
    
    async def _describe_alarms_for_metric(
        self,
        ctx: Context,
        namespace: str,
        metric_name: str,
        dimensions: Optional[List[Dict[str, str]]] = None,
        statistic: Optional[str] = None,
        extended_statistic: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieves all alarms for a specified metric."""
        try:
            return await self.alarms_service.describe_alarms_for_metric(
                namespace=namespace,
                metric_name=metric_name,
                dimensions=dimensions,
                statistic=statistic,
                extended_statistic=extended_statistic,
            )
        except Exception as e:
            logger.error(f"Error in describe_alarms_for_metric: {str(e)}")
            await ctx.error(f"Failed to describe alarms for metric: {str(e)}")
            raise
    
    async def _put_composite_alarm(
        self,
        ctx: Context,
        alarm_name: str,
        alarm_rule: str,
        actions_enabled: Optional[bool] = None,
        alarm_actions: Optional[List[str]] = None,
        alarm_description: Optional[str] = None,
        insufficient_data_actions: Optional[List[str]] = None,
        ok_actions: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """Creates or updates a composite alarm."""
        try:
            return await self.alarms_service.put_composite_alarm(
                alarm_name=alarm_name,
                alarm_rule=alarm_rule,
                actions_enabled=actions_enabled,
                alarm_actions=alarm_actions,
                alarm_description=alarm_description,
                insufficient_data_actions=insufficient_data_actions,
                ok_actions=ok_actions,
            )
        except Exception as e:
            logger.error(f"Error in put_composite_alarm: {str(e)}")
            await ctx.error(f"Failed to put composite alarm: {str(e)}")
            raise
    
    async def _put_metric_alarm(
        self,
        ctx: Context,
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
    ) -> Dict[str, str]:
        """Creates or updates a metric alarm."""
        try:
            return await self.alarms_service.put_metric_alarm(
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
        except Exception as e:
            logger.error(f"Error in put_metric_alarm: {str(e)}")
            await ctx.error(f"Failed to put metric alarm: {str(e)}")
            raise
    
    async def _delete_alarms(
        self,
        ctx: Context,
        alarm_names: List[str],
    ) -> Dict[str, str]:
        """Deletes the specified CloudWatch alarms."""
        try:
            return await self.alarms_service.delete_alarms(
                alarm_names=alarm_names,
            )
        except Exception as e:
            logger.error(f"Error in delete_alarms: {str(e)}")
            await ctx.error(f"Failed to delete alarms: {str(e)}")
            raise
    
    async def _disable_alarm_actions(
        self,
        ctx: Context,
        alarm_names: List[str],
    ) -> Dict[str, str]:
        """Disables actions for the specified alarms."""
        try:
            return await self.alarms_service.disable_alarm_actions(
                alarm_names=alarm_names,
            )
        except Exception as e:
            logger.error(f"Error in disable_alarm_actions: {str(e)}")
            await ctx.error(f"Failed to disable alarm actions: {str(e)}")
            raise
    
    async def _enable_alarm_actions(
        self,
        ctx: Context,
        alarm_names: List[str],
    ) -> Dict[str, str]:
        """Enables actions for the specified alarms."""
        try:
            return await self.alarms_service.enable_alarm_actions(
                alarm_names=alarm_names,
            )
        except Exception as e:
            logger.error(f"Error in enable_alarm_actions: {str(e)}")
            await ctx.error(f"Failed to enable alarm actions: {str(e)}")
            raise
    
    async def _set_alarm_state(
        self,
        ctx: Context,
        alarm_name: str,
        state_value: str,
        state_reason: str,
        state_reason_data: Optional[str] = None,
    ) -> Dict[str, str]:
        """Temporarily sets the state of an alarm."""
        try:
            return await self.alarms_service.set_alarm_state(
                alarm_name=alarm_name,
                state_value=state_value,
                state_reason=state_reason,
                state_reason_data=state_reason_data,
            )
        except Exception as e:
            logger.error(f"Error in set_alarm_state: {str(e)}")
            await ctx.error(f"Failed to set alarm state: {str(e)}")
            raise
    
    def register(self, mcp_server):
        """Register the CloudWatch Alarms tool with the MCP server.
        
        Args:
            mcp_server: The MCP server to register the tool with.
        """
        mcp_server.tool(
            name='cloudwatch_alarms',
            description="""
            Comprehensive tool for working with CloudWatch Alarms. Supports:
            
            - Retrieving alarm history and information
            - Creating and updating metric and composite alarms
            - Deleting alarms
            - Enabling and disabling alarm actions
            - Setting alarm states
            
            Use this tool to monitor, manage, and respond to your AWS CloudWatch alarms.
            """
        )(self.cloudwatch_alarms)