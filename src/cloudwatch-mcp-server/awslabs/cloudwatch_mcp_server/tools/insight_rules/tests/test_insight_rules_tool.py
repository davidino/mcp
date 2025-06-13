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

"""Tests for CloudWatch Insight Rules tool."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from awslabs.cloudwatch_mcp_server.tools.insight_rules.insight_rules_tool import (
    InsightRulesTool,
    InsightRulesOperation,
)


@pytest.fixture
def mock_context():
    """Create a mock MCP context."""
    ctx = MagicMock()
    ctx.error = AsyncMock()
    return ctx


@pytest.fixture
def mock_insight_rule_service():
    """Create a mock InsightRuleService."""
    service = MagicMock()
    service.delete_insight_rules = AsyncMock()
    service.describe_insight_rules = AsyncMock()
    service.disable_insight_rules = AsyncMock()
    service.enable_insight_rules = AsyncMock()
    service.get_insight_rule_report = AsyncMock()
    service.list_managed_insight_rules = AsyncMock()
    service.put_insight_rule = AsyncMock()
    service.put_managed_insight_rules = AsyncMock()
    return service


@pytest.fixture
def insight_rules_tool(mock_insight_rule_service):
    """Create an InsightRulesTool with mocked service."""
    with patch('awslabs.cloudwatch_mcp_server.tools.insight_rules.insight_rules_tool.ClientFactory') as mock_factory:
        mock_factory.get_cloudwatch_client.return_value = MagicMock()
        tool = InsightRulesTool()
        tool.insight_rule_service = mock_insight_rule_service
        return tool


class TestInsightRulesTool:
    """Tests for the InsightRulesTool class."""

    async def test_delete_insight_rules(self, insight_rules_tool, mock_context, mock_insight_rule_service):
        """Test delete_insight_rules operation."""
        rule_names = ["TestRule1", "TestRule2"]
        mock_insight_rule_service.delete_insight_rules.return_value = {
            "status": "Successfully deleted 2 insight rules"
        }
        
        result = await insight_rules_tool.cloudwatch_insight_rules(
            mock_context,
            operation=InsightRulesOperation.DELETE_INSIGHT_RULES,
            rule_names=rule_names,
        )
        
        mock_insight_rule_service.delete_insight_rules.assert_called_once_with(
            rule_names=rule_names,
        )
        assert result["status"] == "Successfully deleted 2 insight rules"

    async def test_describe_insight_rules(self, insight_rules_tool, mock_context, mock_insight_rule_service):
        """Test describe_insight_rules operation."""
        mock_insight_rule_service.describe_insight_rules.return_value = {
            "insightRules": [{"RuleName": "TestRule", "State": "ENABLED"}],
            "nextToken": None
        }
        
        result = await insight_rules_tool.cloudwatch_insight_rules(
            mock_context,
            operation=InsightRulesOperation.DESCRIBE_INSIGHT_RULES,
            max_results=10,
        )
        
        mock_insight_rule_service.describe_insight_rules.assert_called_once_with(
            max_results=10,
            next_token=None,
        )
        assert len(result["insightRules"]) == 1
        assert result["insightRules"][0]["RuleName"] == "TestRule"

    async def test_disable_insight_rules(self, insight_rules_tool, mock_context, mock_insight_rule_service):
        """Test disable_insight_rules operation."""
        rule_names = ["TestRule1", "TestRule2"]
        mock_insight_rule_service.disable_insight_rules.return_value = {
            "status": "Successfully disabled 2 insight rules"
        }
        
        result = await insight_rules_tool.cloudwatch_insight_rules(
            mock_context,
            operation=InsightRulesOperation.DISABLE_INSIGHT_RULES,
            rule_names=rule_names,
        )
        
        mock_insight_rule_service.disable_insight_rules.assert_called_once_with(
            rule_names=rule_names,
        )
        assert result["status"] == "Successfully disabled 2 insight rules"

    async def test_enable_insight_rules(self, insight_rules_tool, mock_context, mock_insight_rule_service):
        """Test enable_insight_rules operation."""
        rule_names = ["TestRule1", "TestRule2"]
        mock_insight_rule_service.enable_insight_rules.return_value = {
            "status": "Successfully enabled 2 insight rules"
        }
        
        result = await insight_rules_tool.cloudwatch_insight_rules(
            mock_context,
            operation=InsightRulesOperation.ENABLE_INSIGHT_RULES,
            rule_names=rule_names,
        )
        
        mock_insight_rule_service.enable_insight_rules.assert_called_once_with(
            rule_names=rule_names,
        )
        assert result["status"] == "Successfully enabled 2 insight rules"

    async def test_get_insight_rule_report(self, insight_rules_tool, mock_context, mock_insight_rule_service):
        """Test get_insight_rule_report operation."""
        mock_insight_rule_service.get_insight_rule_report.return_value = {
            "keyLabels": ["InstanceId"],
            "contributors": [{"Keys": ["i-1234567890abcdef0"], "ApproximateAggregateValue": 1.0}]
        }
        
        result = await insight_rules_tool.cloudwatch_insight_rules(
            mock_context,
            operation=InsightRulesOperation.GET_INSIGHT_RULE_REPORT,
            rule_name="TestRule",
            start_time="2025-01-01T00:00:00Z",
            end_time="2025-01-02T00:00:00Z",
            period=60,
        )
        
        mock_insight_rule_service.get_insight_rule_report.assert_called_once_with(
            rule_name="TestRule",
            start_time="2025-01-01T00:00:00Z",
            end_time="2025-01-02T00:00:00Z",
            period=60,
            max_contributor_count=None,
            metrics=None,
            order_by=None,
        )
        assert result["keyLabels"] == ["InstanceId"]
        assert len(result["contributors"]) == 1

    async def test_list_managed_insight_rules(self, insight_rules_tool, mock_context, mock_insight_rule_service):
        """Test list_managed_insight_rules operation."""
        resource_arn = "arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0"
        mock_insight_rule_service.list_managed_insight_rules.return_value = {
            "managedRules": [{"RuleName": "TestRule", "State": "ENABLED"}],
            "nextToken": None
        }
        
        result = await insight_rules_tool.cloudwatch_insight_rules(
            mock_context,
            operation=InsightRulesOperation.LIST_MANAGED_INSIGHT_RULES,
            resource_arn=resource_arn,
        )
        
        mock_insight_rule_service.list_managed_insight_rules.assert_called_once_with(
            resource_arn=resource_arn,
            max_results=None,
            next_token=None,
        )
        assert len(result["managedRules"]) == 1
        assert result["managedRules"][0]["RuleName"] == "TestRule"

    async def test_put_insight_rule_with_string(self, insight_rules_tool, mock_context, mock_insight_rule_service):
        """Test put_insight_rule operation with string rule definition."""
        rule_definition = json.dumps({"Source": "AWS/EC2", "Schema": "CloudWatchMetrics"})
        mock_insight_rule_service.put_insight_rule.return_value = {
            "status": "Successfully created or updated insight rule: TestRule",
            "ruleArn": "arn:aws:cloudwatch:us-east-1:123456789012:insight-rule/TestRule"
        }
        
        result = await insight_rules_tool.cloudwatch_insight_rules(
            mock_context,
            operation=InsightRulesOperation.PUT_INSIGHT_RULE,
            rule_name="TestRule",
            rule_definition=rule_definition,
        )
        
        mock_insight_rule_service.put_insight_rule.assert_called_once_with(
            rule_name="TestRule",
            rule_definition=rule_definition,
            rule_state=None,
            tags=None,
        )
        assert "ruleArn" in result
        assert result["status"] == "Successfully created or updated insight rule: TestRule"

    async def test_put_insight_rule_with_dict(self, insight_rules_tool, mock_context, mock_insight_rule_service):
        """Test put_insight_rule operation with dictionary rule definition."""
        rule_definition = {"Source": "AWS/EC2", "Schema": "CloudWatchMetrics"}
        mock_insight_rule_service.put_insight_rule.return_value = {
            "status": "Successfully created or updated insight rule: TestRule",
            "ruleArn": "arn:aws:cloudwatch:us-east-1:123456789012:insight-rule/TestRule"
        }
        
        result = await insight_rules_tool.cloudwatch_insight_rules(
            mock_context,
            operation=InsightRulesOperation.PUT_INSIGHT_RULE,
            rule_name="TestRule",
            rule_definition=rule_definition,
        )
        
        # Verify the dictionary was converted to a JSON string
        mock_insight_rule_service.put_insight_rule.assert_called_once()
        call_args = mock_insight_rule_service.put_insight_rule.call_args[1]
        assert call_args["rule_name"] == "TestRule"
        assert isinstance(call_args["rule_definition"], str)
        assert json.loads(call_args["rule_definition"]) == rule_definition
        
        assert "ruleArn" in result
        assert result["status"] == "Successfully created or updated insight rule: TestRule"

    async def test_put_managed_insight_rules(self, insight_rules_tool, mock_context, mock_insight_rule_service):
        """Test put_managed_insight_rules operation."""
        managed_rules = [
            {
                "ResourceARN": "arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0",
                "RuleId": "TestRule"
            }
        ]
        mock_insight_rule_service.put_managed_insight_rules.return_value = {
            "status": "Successfully created 1 managed insight rules"
        }
        
        result = await insight_rules_tool.cloudwatch_insight_rules(
            mock_context,
            operation=InsightRulesOperation.PUT_MANAGED_INSIGHT_RULES,
            managed_rules=managed_rules,
        )
        
        mock_insight_rule_service.put_managed_insight_rules.assert_called_once_with(
            managed_rules=managed_rules,
        )
        assert result["status"] == "Successfully created 1 managed insight rules"

    async def test_missing_required_parameters(self, insight_rules_tool, mock_context):
        """Test error handling for missing required parameters."""
        with pytest.raises(ValueError) as excinfo:
            await insight_rules_tool.cloudwatch_insight_rules(
                mock_context,
                operation=InsightRulesOperation.DELETE_INSIGHT_RULES,
                rule_names=None,
            )
        assert "rule_names is required" in str(excinfo.value)
        
        with pytest.raises(ValueError) as excinfo:
            await insight_rules_tool.cloudwatch_insight_rules(
                mock_context,
                operation=InsightRulesOperation.GET_INSIGHT_RULE_REPORT,
                rule_name="TestRule",
                # Missing start_time, end_time, period
            )
        assert "rule_name, start_time, end_time, and period are required" in str(excinfo.value)

    async def test_unsupported_operation(self, insight_rules_tool, mock_context):
        """Test error handling for unsupported operations."""
        with pytest.raises(ValueError) as excinfo:
            await insight_rules_tool.cloudwatch_insight_rules(
                mock_context,
                operation="INVALID_OPERATION",
            )
        assert "Unsupported operation" in str(excinfo.value)