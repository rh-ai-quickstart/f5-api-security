# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

import os
from typing import Optional, Tuple, List
import requests

from llama_stack_client import LlamaStackClient

class LlamaStackApi:
    def __init__(self):
        self.client = LlamaStackClient(
            base_url=os.environ.get("LLAMA_STACK_ENDPOINT", "http://localhost:8321"),

            provider_data={
                "fireworks_api_key": os.environ.get("FIREWORKS_API_KEY", ""),
                "together_api_key": os.environ.get("TOGETHER_API_KEY", ""),
                "sambanova_api_key": os.environ.get("SAMBANOVA_API_KEY", ""),
                "openai_api_key": os.environ.get("OPENAI_API_KEY", ""),
                "tavily_search_api_key": os.environ.get("TAVILY_SEARCH_API_KEY", ""),
            },
        )

    def run_scoring(self, row, scoring_function_ids: list[str], scoring_params: Optional[dict]):
        """Run scoring on a single row"""
        if not scoring_params:
            scoring_params = {fn_id: None for fn_id in scoring_function_ids}
        return self.client.scoring.score(input_rows=[row], scoring_functions=scoring_params)

    def create_client_with_url(self, base_url: str) -> LlamaStackClient:
        """Create a LlamaStackClient with custom base URL"""
        return LlamaStackClient(base_url=base_url)

    def validate_llamastack_endpoint(self, url: str) -> Tuple[bool, Optional[List], Optional[str]]:
        """
        Validate if the URL is a LlamaStack endpoint and fetch models.
        
        Returns:
            Tuple[bool, Optional[List], Optional[str]]: 
            (is_valid, models_list, error_message)
        """
        try:
            # Remove trailing slash if present
            url = url.rstrip('/')
            
            # Basic URL format validation
            if not url.startswith(('http://', 'https://')):
                return False, None, "XC URL must start with http:// or https://"
            
            # Create client with custom URL
            client = self.create_client_with_url(url)
            
            # Try to fetch models - this will fail if not a LlamaStack endpoint
            models = client.models.list()
            
            if not models:
                return False, None, "XC URL must be a LlamaStack endpoint"
            
            return True, models, None
            
        except requests.exceptions.ConnectionError:
            return False, None, "Cannot connect to XC URL. Please check the URL and network connectivity."
        except requests.exceptions.Timeout:
            return False, None, "Connection to XC URL timed out. Please try again."
        except Exception as e:
            # This catches LlamaStack client errors (invalid endpoint structure, etc.)
            return False, None, "XC URL must be a LlamaStack endpoint"

    def fetch_models_from_url(self, url: str) -> Tuple[bool, Optional[List], Optional[str]]:
        """
        Fetch models from a custom LlamaStack URL.
        
        Returns:
            Tuple[bool, Optional[List], Optional[str]]: 
            (success, models_list, error_message)
        """
        return self.validate_llamastack_endpoint(url)

llama_stack_api = LlamaStackApi()
