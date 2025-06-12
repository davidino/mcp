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

"""Unit tests for the CloudWatch Insight Rule service."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from awslabs.cloudwatch_mcp_server.services.insight_rule_service import InsightRuleService


@pytest.fixture
def mock_cloudwatch_client():
    """Create a mock CloudWatch client."""
    mock_client = MagicMock()
    return mock_client


@pytest.fixture
def insight_rule_service(mock_cloudwatch_client):
    """Create an InsightRuleService instance with a mock client."""
    return InsightRuleService(mock_cloudwatch_client)


class TestInsightRuleService:
    """Tests for the InsightRuleService class."""

    async def test_put_insight_rule_success(self, insight_rule_service, mock_cloudwatch_client):
        """Test successful put_insight_rule call with string input."""
        # Setup mock response
        mock_cloudwatch_client.put_insight_rule.return_value = {
            'RuleArn': 'arn:aws:cloudwatch:us-east-1:123456789012:insight-rule/TestRule'
        }
        
        # Call the service method
        result = await insight_rule_service.put_insight_rule(
            rule_name='TestRule',
            rule_definition='{"Source": "AWS/EC2", "Schema": {"Name": "InstanceId"}}'
        )
        
        # Verify the result
        assert result['status'] == 'Successfully created or updated insight rule: TestRule'
        assert result['ruleArn'] == 'arn:aws:cloudwatch:us-east-1:123456789012:insight-rule/TestRule'
        
        # Verify the client was called correctly
        mock_cloudwatch_client.put_insight_rule.assert_called_once_with(
            RuleName='TestRule',
            RuleDefinition='{"Source": "AWS/EC2", "Schema": {"Name": "InstanceId"}}'
        )
    
    async def test_put_insight_rule_invalid_json(self, insight_rule_service):
        """Test put_insight_rule with invalid JSON string."""
        # Call the service method with invalid JSON
        with pytest.raises(ValueError) as excinfo:
            await insight_rule_service.put_insight_rule(
                rule_name='TestRule',
                rule_definition='{invalid json}'
            )
        
        # Verify the error message
        assert "must be a valid JSON string" in str(excinfo.value)