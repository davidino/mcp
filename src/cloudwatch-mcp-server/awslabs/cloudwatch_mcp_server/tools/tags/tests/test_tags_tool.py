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

"""Tests for CloudWatch Tags tool."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from awslabs.cloudwatch_mcp_server.tools.tags.tags_tool import (
    TagsTool,
    TagsOperation,
)


@pytest.fixture
def mock_context():
    """Create a mock MCP context."""
    ctx = MagicMock()
    ctx.error = AsyncMock()
    return ctx


@pytest.fixture
def mock_tag_service():
    """Create a mock TagService."""
    service = MagicMock()
    service.list_tags_for_resource = AsyncMock()
    service.tag_resource = AsyncMock()
    service.untag_resource = AsyncMock()
    return service


@pytest.fixture
def tags_tool(mock_tag_service):
    """Create a TagsTool with mocked service."""
    with patch('awslabs.cloudwatch_mcp_server.tools.tags.tags_tool.ClientFactory') as mock_factory:
        mock_factory.get_cloudwatch_client.return_value = MagicMock()
        tool = TagsTool()
        tool.tag_service = mock_tag_service
        return tool


class TestTagsTool:
    """Tests for the TagsTool class."""

    async def test_list_tags_for_resource(self, tags_tool, mock_context, mock_tag_service):
        """Test list_tags_for_resource operation."""
        resource_arn = "arn:aws:cloudwatch:us-east-1:123456789012:alarm:TestAlarm"
        mock_tag_service.list_tags_for_resource.return_value = {
            "tags": [{"Key": "Environment", "Value": "Production"}]
        }
        
        result = await tags_tool.cloudwatch_tags(
            mock_context,
            operation=TagsOperation.LIST_TAGS_FOR_RESOURCE,
            resource_arn=resource_arn,
        )
        
        mock_tag_service.list_tags_for_resource.assert_called_once_with(
            resource_arn=resource_arn,
        )
        assert len(result["tags"]) == 1
        assert result["tags"][0]["Key"] == "Environment"
        assert result["tags"][0]["Value"] == "Production"

    async def test_tag_resource(self, tags_tool, mock_context, mock_tag_service):
        """Test tag_resource operation."""
        resource_arn = "arn:aws:cloudwatch:us-east-1:123456789012:alarm:TestAlarm"
        tags = [{"Key": "Environment", "Value": "Production"}]
        mock_tag_service.tag_resource.return_value = {
            "status": "Successfully tagged resource: arn:aws:cloudwatch:us-east-1:123456789012:alarm:TestAlarm"
        }
        
        result = await tags_tool.cloudwatch_tags(
            mock_context,
            operation=TagsOperation.TAG_RESOURCE,
            resource_arn=resource_arn,
            tags=tags,
        )
        
        mock_tag_service.tag_resource.assert_called_once_with(
            resource_arn=resource_arn,
            tags=tags,
        )
        assert "status" in result
        assert "Successfully tagged resource" in result["status"]

    async def test_untag_resource(self, tags_tool, mock_context, mock_tag_service):
        """Test untag_resource operation."""
        resource_arn = "arn:aws:cloudwatch:us-east-1:123456789012:alarm:TestAlarm"
        tag_keys = ["Environment"]
        mock_tag_service.untag_resource.return_value = {
            "status": "Successfully untagged resource: arn:aws:cloudwatch:us-east-1:123456789012:alarm:TestAlarm"
        }
        
        result = await tags_tool.cloudwatch_tags(
            mock_context,
            operation=TagsOperation.UNTAG_RESOURCE,
            resource_arn=resource_arn,
            tag_keys=tag_keys,
        )
        
        mock_tag_service.untag_resource.assert_called_once_with(
            resource_arn=resource_arn,
            tag_keys=tag_keys,
        )
        assert "status" in result
        assert "Successfully untagged resource" in result["status"]

    async def test_missing_required_parameters(self, tags_tool, mock_context):
        """Test error handling for missing required parameters."""
        resource_arn = "arn:aws:cloudwatch:us-east-1:123456789012:alarm:TestAlarm"
        
        with pytest.raises(ValueError) as excinfo:
            await tags_tool.cloudwatch_tags(
                mock_context,
                operation=TagsOperation.TAG_RESOURCE,
                resource_arn=resource_arn,
                tags=None,
            )
        assert "tags is required" in str(excinfo.value)
        
        with pytest.raises(ValueError) as excinfo:
            await tags_tool.cloudwatch_tags(
                mock_context,
                operation=TagsOperation.UNTAG_RESOURCE,
                resource_arn=resource_arn,
                tag_keys=None,
            )
        assert "tag_keys is required" in str(excinfo.value)

    async def test_unsupported_operation(self, tags_tool, mock_context):
        """Test error handling for unsupported operations."""
        resource_arn = "arn:aws:cloudwatch:us-east-1:123456789012:alarm:TestAlarm"
        
        with pytest.raises(ValueError) as excinfo:
            await tags_tool.cloudwatch_tags(
                mock_context,
                operation="INVALID_OPERATION",
                resource_arn=resource_arn,
            )
        assert "Unsupported operation" in str(excinfo.value)