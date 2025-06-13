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

"""CloudWatch OAM (Observability Access Manager) service."""

from typing import Dict, List, Optional, Any
from loguru import logger


class OAMService:
    """Service for interacting with CloudWatch OAM APIs."""

    def __init__(self, oam_client):
        """Initialize the OAM service with a boto3 OAM client."""
        self.client = oam_client

    async def list_sinks(self, max_results: Optional[int] = None, next_token: Optional[str] = None) -> Dict[str, Any]:
        """
        List all sinks in the current account.
        
        Args:
            max_results: Maximum number of results to return
            next_token: Token for pagination
            
        Returns:
            Dictionary containing sink information
        """
        try:
            params = {}
            if max_results:
                params['MaxResults'] = max_results
            if next_token:
                params['NextToken'] = next_token
                
            response = self.client.list_sinks(**params)
            return response
        except Exception as e:
            logger.error(f"Error listing OAM sinks: {str(e)}")
            raise

    async def get_sink(self, sink_identifier: str) -> Dict[str, Any]:
        """
        Get details about a specific sink.
        
        Args:
            sink_identifier: The ARN or ID of the sink
            
        Returns:
            Dictionary containing sink details
        """
        try:
            response = self.client.get_sink(SinkIdentifier=sink_identifier)
            return response
        except Exception as e:
            logger.error(f"Error getting OAM sink {sink_identifier}: {str(e)}")
            raise

    async def create_sink(self, name: str, alias: Optional[str] = None, tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a new OAM sink.
        
        Args:
            name: The name of the sink
            alias: Optional alias for the sink
            tags: Optional tags to apply to the sink
            
        Returns:
            Dictionary containing the created sink details
        """
        try:
            params = {'Name': name}
            if alias:
                params['Alias'] = alias
            if tags:
                params['Tags'] = [{'Key': k, 'Value': v} for k, v in tags.items()]
                
            response = self.client.create_sink(**params)
            return response
        except Exception as e:
            logger.error(f"Error creating OAM sink {name}: {str(e)}")
            raise

    async def update_sink(self, sink_identifier: str, alias: str) -> Dict[str, Any]:
        """
        Update an existing OAM sink.
        
        Args:
            sink_identifier: The ARN or ID of the sink
            alias: The new alias for the sink
            
        Returns:
            Dictionary containing the updated sink details
        """
        try:
            response = self.client.update_sink(
                SinkIdentifier=sink_identifier,
                Alias=alias
            )
            return response
        except Exception as e:
            logger.error(f"Error updating OAM sink {sink_identifier}: {str(e)}")
            raise

    async def delete_sink(self, sink_identifier: str) -> Dict[str, Any]:
        """
        Delete an OAM sink.
        
        Args:
            sink_identifier: The ARN or ID of the sink
            
        Returns:
            Dictionary containing the deletion response
        """
        try:
            response = self.client.delete_sink(SinkIdentifier=sink_identifier)
            return response
        except Exception as e:
            logger.error(f"Error deleting OAM sink {sink_identifier}: {str(e)}")
            raise

    async def list_links(self, sink_identifier: Optional[str] = None, 
                         max_results: Optional[int] = None, 
                         next_token: Optional[str] = None) -> Dict[str, Any]:
        """
        List all links in the current account.
        
        Args:
            sink_identifier: Optional sink identifier to filter links
            max_results: Maximum number of results to return
            next_token: Token for pagination
            
        Returns:
            Dictionary containing link information
        """
        try:
            params = {}
            if sink_identifier:
                params['SinkIdentifier'] = sink_identifier
            if max_results:
                params['MaxResults'] = max_results
            if next_token:
                params['NextToken'] = next_token
                
            response = self.client.list_links(**params)
            return response
        except Exception as e:
            logger.error(f"Error listing OAM links: {str(e)}")
            raise

    async def get_link(self, link_identifier: str) -> Dict[str, Any]:
        """
        Get details about a specific link.
        
        Args:
            link_identifier: The ARN or ID of the link
            
        Returns:
            Dictionary containing link details
        """
        try:
            response = self.client.get_link(LinkIdentifier=link_identifier)
            return response
        except Exception as e:
            logger.error(f"Error getting OAM link {link_identifier}: {str(e)}")
            raise

    async def create_link(self, 
                         sink_identifier: str, 
                         label: str, 
                         resource_types: List[str],
                         tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a new OAM link.
        
        Args:
            sink_identifier: The ARN or ID of the sink to link to
            label: A label for the link
            resource_types: List of resource types to include in the link (e.g., ['METRICS', 'LOGS'])
            tags: Optional tags to apply to the link
            
        Returns:
            Dictionary containing the created link details
        """
        try:
            params = {
                'SinkIdentifier': sink_identifier,
                'Label': label,
                'ResourceTypes': resource_types
            }
            if tags:
                params['Tags'] = [{'Key': k, 'Value': v} for k, v in tags.items()]
                
            response = self.client.create_link(**params)
            return response
        except Exception as e:
            logger.error(f"Error creating OAM link to sink {sink_identifier}: {str(e)}")
            raise

    async def update_link(self, 
                         link_identifier: str, 
                         resource_types: List[str]) -> Dict[str, Any]:
        """
        Update an existing OAM link.
        
        Args:
            link_identifier: The ARN or ID of the link
            resource_types: Updated list of resource types to include in the link
            
        Returns:
            Dictionary containing the updated link details
        """
        try:
            response = self.client.update_link(
                LinkIdentifier=link_identifier,
                ResourceTypes=resource_types
            )
            return response
        except Exception as e:
            logger.error(f"Error updating OAM link {link_identifier}: {str(e)}")
            raise

    async def delete_link(self, link_identifier: str) -> Dict[str, Any]:
        """
        Delete an OAM link.
        
        Args:
            link_identifier: The ARN or ID of the link
            
        Returns:
            Dictionary containing the deletion response
        """
        try:
            response = self.client.delete_link(LinkIdentifier=link_identifier)
            return response
        except Exception as e:
            logger.error(f"Error deleting OAM link {link_identifier}: {str(e)}")
            raise

    async def list_attached_links(self, sink_identifier: str,
                                 max_results: Optional[int] = None,
                                 next_token: Optional[str] = None) -> Dict[str, Any]:
        """
        List links attached to a specific sink.
        
        Args:
            sink_identifier: The ARN or ID of the sink
            max_results: Maximum number of results to return
            next_token: Token for pagination
            
        Returns:
            Dictionary containing attached link information
        """
        try:
            params = {'SinkIdentifier': sink_identifier}
            if max_results:
                params['MaxResults'] = max_results
            if next_token:
                params['NextToken'] = next_token
                
            response = self.client.list_attached_links(**params)
            return response
        except Exception as e:
            logger.error(f"Error listing attached OAM links for sink {sink_identifier}: {str(e)}")
            raise