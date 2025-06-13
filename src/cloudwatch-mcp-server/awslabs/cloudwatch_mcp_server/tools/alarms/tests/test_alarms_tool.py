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

"""Tests for the CloudWatch Alarms tool."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from awslabs.cloudwatch_mcp_server.tools.alarms.alarms_tool import AlarmsTool, AlarmsOperation


@pytest.fixture
def mock_context():
    """Create a mock context."""
    context = MagicMock()
    context.error = AsyncMock()
    return context


def test_register():
    """Test AlarmsTool registration."""
    tool = AlarmsTool()
    mock_server = MagicMock()
    mock_tool_decorator = MagicMock()
    mock_server.tool.return_value = mock_tool_decorator
    
    tool.register(mock_server)
    
    mock_server.tool.assert_called_once_with(
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
    )
    mock_tool_decorator.assert_called_once_with(tool.cloudwatch_alarms)


@pytest.fixture
def mock_alarm_service():
    """Create a mock alarm service."""
    service = MagicMock()
    service.describe_alarm_history = AsyncMock()
    service.describe_alarms = AsyncMock()
    service.describe_alarms_for_metric = AsyncMock()
    service.put_composite_alarm = AsyncMock()
    service.put_metric_alarm = AsyncMock()
    service.delete_alarms = AsyncMock()
    service.disable_alarm_actions = AsyncMock()
    service.enable_alarm_actions = AsyncMock()
    service.set_alarm_state = AsyncMock()
    return service


@pytest.fixture
def alarms_tool(mock_alarm_service):
    """Create an AlarmsTool with a mock alarm service."""
    with patch('awslabs.cloudwatch_mcp_server.tools.alarms.alarms_tool.ClientFactory') as mock_factory:
        mock_factory.get_cloudwatch_client.return_value = MagicMock()
        tool = AlarmsTool(region_name='us-east-1')
        tool.alarms_service = mock_alarm_service
        return tool


@pytest.mark.asyncio
async def test_describe_alarm_history(alarms_tool, mock_context, mock_alarm_service):
    """Test describe_alarm_history operation."""
    mock_alarm_service.describe_alarm_history.return_value = {"alarmHistoryItems": []}
    
    result = await alarms_tool.cloudwatch_alarms(
        mock_context,
        operation=AlarmsOperation.DESCRIBE_ALARM_HISTORY,
        alarm_name="test-alarm"
    )
    
    mock_alarm_service.describe_alarm_history.assert_called_once_with(
        alarm_name="test-alarm",
        alarm_types=None,
        history_item_type=None,
        start_date=None,
        end_date=None,
        max_records=None,
        next_token=None
    )
    assert result == {"alarmHistoryItems": []}


@pytest.mark.asyncio
async def test_describe_alarms(alarms_tool, mock_context, mock_alarm_service):
    """Test describe_alarms operation."""
    mock_alarm_service.describe_alarms.return_value = {"metricAlarms": [], "compositeAlarms": []}
    
    result = await alarms_tool.cloudwatch_alarms(
        mock_context,
        operation=AlarmsOperation.DESCRIBE_ALARMS,
        alarm_names=["test-alarm"]
    )
    
    mock_alarm_service.describe_alarms.assert_called_once_with(
        alarm_names=["test-alarm"],
        alarm_name_prefix=None,
        alarm_types=None,
        state_value=None,
        action_prefix=None,
        max_records=None,
        next_token=None
    )
    assert result == {"metricAlarms": [], "compositeAlarms": []}


@pytest.mark.asyncio
async def test_describe_alarms_for_metric(alarms_tool, mock_context, mock_alarm_service):
    """Test describe_alarms_for_metric operation."""
    mock_alarm_service.describe_alarms_for_metric.return_value = {"metricAlarms": []}
    
    result = await alarms_tool.cloudwatch_alarms(
        mock_context,
        operation=AlarmsOperation.DESCRIBE_ALARMS_FOR_METRIC,
        namespace="AWS/EC2",
        metric_name="CPUUtilization"
    )
    
    mock_alarm_service.describe_alarms_for_metric.assert_called_once_with(
        namespace="AWS/EC2",
        metric_name="CPUUtilization",
        dimensions=None,
        statistic=None,
        extended_statistic=None
    )
    assert result == {"metricAlarms": []}


@pytest.mark.asyncio
async def test_put_composite_alarm(alarms_tool, mock_context, mock_alarm_service):
    """Test put_composite_alarm operation."""
    mock_alarm_service.put_composite_alarm.return_value = {"status": "Successfully created or updated composite alarm: test-alarm"}
    
    result = await alarms_tool.cloudwatch_alarms(
        mock_context,
        operation=AlarmsOperation.PUT_COMPOSITE_ALARM,
        alarm_name="test-alarm",
        alarm_rule="ALARM(test-alarm-1) OR ALARM(test-alarm-2)"
    )
    
    mock_alarm_service.put_composite_alarm.assert_called_once_with(
        alarm_name="test-alarm",
        alarm_rule="ALARM(test-alarm-1) OR ALARM(test-alarm-2)",
        actions_enabled=None,
        alarm_actions=None,
        alarm_description=None,
        insufficient_data_actions=None,
        ok_actions=None
    )
    assert result == {"status": "Successfully created or updated composite alarm: test-alarm"}


@pytest.mark.asyncio
async def test_put_metric_alarm(alarms_tool, mock_context, mock_alarm_service):
    """Test put_metric_alarm operation."""
    mock_alarm_service.put_metric_alarm.return_value = {"status": "Successfully created or updated metric alarm: test-alarm"}
    
    result = await alarms_tool.cloudwatch_alarms(
        mock_context,
        operation=AlarmsOperation.PUT_METRIC_ALARM,
        alarm_name="test-alarm",
        comparison_operator="GreaterThanThreshold",
        evaluation_periods=1,
        metric_name="CPUUtilization",
        namespace="AWS/EC2",
        period=60,
        statistic="Average",
        threshold=80.0
    )
    
    mock_alarm_service.put_metric_alarm.assert_called_once_with(
        alarm_name="test-alarm",
        comparison_operator="GreaterThanThreshold",
        evaluation_periods=1,
        metric_name="CPUUtilization",
        namespace="AWS/EC2",
        period=60,
        statistic="Average",
        threshold=80.0,
        actions_enabled=None,
        alarm_actions=None,
        alarm_description=None,
        dimensions=None,
        insufficient_data_actions=None,
        ok_actions=None,
        unit=None
    )
    assert result == {"status": "Successfully created or updated metric alarm: test-alarm"}


@pytest.mark.asyncio
async def test_delete_alarms(alarms_tool, mock_context, mock_alarm_service):
    """Test delete_alarms operation."""
    mock_alarm_service.delete_alarms.return_value = {"status": "Successfully deleted 1 alarms"}
    
    result = await alarms_tool.cloudwatch_alarms(
        mock_context,
        operation=AlarmsOperation.DELETE_ALARMS,
        alarm_names=["test-alarm"]
    )
    
    mock_alarm_service.delete_alarms.assert_called_once_with(
        alarm_names=["test-alarm"]
    )
    assert result == {"status": "Successfully deleted 1 alarms"}


@pytest.mark.asyncio
async def test_disable_alarm_actions(alarms_tool, mock_context, mock_alarm_service):
    """Test disable_alarm_actions operation."""
    mock_alarm_service.disable_alarm_actions.return_value = {"status": "Successfully disabled actions for 1 alarms"}
    
    result = await alarms_tool.cloudwatch_alarms(
        mock_context,
        operation=AlarmsOperation.DISABLE_ALARM_ACTIONS,
        alarm_names=["test-alarm"]
    )
    
    mock_alarm_service.disable_alarm_actions.assert_called_once_with(
        alarm_names=["test-alarm"]
    )
    assert result == {"status": "Successfully disabled actions for 1 alarms"}


@pytest.mark.asyncio
async def test_enable_alarm_actions(alarms_tool, mock_context, mock_alarm_service):
    """Test enable_alarm_actions operation."""
    mock_alarm_service.enable_alarm_actions.return_value = {"status": "Successfully enabled actions for 1 alarms"}
    
    result = await alarms_tool.cloudwatch_alarms(
        mock_context,
        operation=AlarmsOperation.ENABLE_ALARM_ACTIONS,
        alarm_names=["test-alarm"]
    )
    
    mock_alarm_service.enable_alarm_actions.assert_called_once_with(
        alarm_names=["test-alarm"]
    )
    assert result == {"status": "Successfully enabled actions for 1 alarms"}


@pytest.mark.asyncio
async def test_set_alarm_state(alarms_tool, mock_context, mock_alarm_service):
    """Test set_alarm_state operation."""
    mock_alarm_service.set_alarm_state.return_value = {"status": "Successfully set alarm state for test-alarm to ALARM"}
    
    result = await alarms_tool.cloudwatch_alarms(
        mock_context,
        operation=AlarmsOperation.SET_ALARM_STATE,
        alarm_name="test-alarm",
        state_value="ALARM",
        state_reason="Testing alarm state"
    )
    
    mock_alarm_service.set_alarm_state.assert_called_once_with(
        alarm_name="test-alarm",
        state_value="ALARM",
        state_reason="Testing alarm state",
        state_reason_data=None
    )
    assert result == {"status": "Successfully set alarm state for test-alarm to ALARM"}