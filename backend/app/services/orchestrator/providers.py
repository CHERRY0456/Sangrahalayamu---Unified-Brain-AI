import re
import json
import logging
from abc import ABC, abstractmethod
from typing import Generator, Dict, Any, Optional

from .models import LLMRequest, LLMResponse

logger = logging.getLogger("sangrahalayamu.orchestrator.providers")

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, req: LLMRequest) -> LLMResponse:
        """
        Executes synchronous text generation.
        """
        pass

    @abstractmethod
    def stream_generate(self, req: LLMRequest) -> Generator[str, None, None]:
        """
        Executes streaming token generation.
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Checks connection status to the LLM backend.
        """
        pass

class BedrockProvider(LLMProvider):
    """
    Live Amazon Bedrock Converse API provider.
    Requires AWS credentials in environment. No mock fallbacks allowed (Zero-Mock Mandate).
    """
    def __init__(self):
        self.client = None
        self.model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        try:
            import boto3
            # Attempt loading Bedrock runtime client
            self.client = boto3.client("bedrock-runtime", region_name="us-east-1")
        except Exception as e:
            logger.error(f"AWS boto3 client failed to load: {e}")
            raise RuntimeError("Live Bedrock connection is required in production. No mock fallbacks allowed.") from e

    def generate(self, req: LLMRequest) -> LLMResponse:
        if not self.client:
            raise RuntimeError("Live Bedrock client not initialized.")
            
        try:
            # Call Bedrock Converse API
            messages = [{"role": "user", "content": [{"text": req.prompt}]}]
            if req.history:
                # Map history roles to Bedrock format
                messages = []
                for h in req.history:
                    role = h.get("role", "user")
                    # Ensure alternating role structure
                    messages.append({"role": role, "content": [{"text": h.get("content", "")}]})
                messages.append({"role": "user", "content": [{"text": req.prompt}]})

            system_prompts = [{"text": req.system_prompt}]

            response = self.client.converse(
                modelId=self.model_id,
                messages=messages,
                system=system_prompts,
                inferenceConfig={
                    "maxTokens": req.max_tokens,
                    "temperature": req.temperature
                }
            )

            response_text = response["output"]["message"]["content"][0]["text"]
            usage = response.get("usage", {})
            token_usage = {
                "input_tokens": usage.get("inputTokens", 0),
                "output_tokens": usage.get("outputTokens", 0),
                "total_tokens": usage.get("totalTokens", 0)
            }

            return LLMResponse(
                text=response_text,
                token_usage=token_usage,
                provider_name="AWSBedrock",
                raw_response=response
            )

        except Exception as e:
            logger.error(f"Amazon Bedrock Converse failed: {str(e)}")
            raise

    def stream_generate(self, req: LLMRequest) -> Generator[str, None, None]:
        if not self.client:
            raise RuntimeError("Live Bedrock client not initialized.")

        try:
            response = self.client.converse_stream(
                modelId=self.model_id,
                messages=[{"role": "user", "content": [{"text": req.prompt}]}],
                system=[{"text": req.system_prompt}]
            )
            for event in response.get("stream"):
                if "contentBlockDelta" in event:
                    text_delta = event["contentBlockDelta"]["delta"]["text"]
                    yield text_delta
        except Exception as e:
            logger.error(f"Amazon Bedrock Converse stream failed: {str(e)}")
            raise

    def health_check(self) -> bool:
        if not self.client:
            return False
        try:
            return True
        except Exception:
            return False
