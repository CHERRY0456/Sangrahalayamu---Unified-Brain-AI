import json
import time
import boto3
import logging
from typing import AsyncGenerator

from app.core.config import settings
from ..interfaces.llm_provider import BaseLLMProvider
from ..schemas.generation_models import GenerationRequest, GenerationResponse, StreamEvent

logger = logging.getLogger(__name__)

class BedrockQwenProvider(BaseLLMProvider):
    """
    AWS Bedrock provider using Converse and ConverseStream API for model-agnostic generation.
    Supports Claude, Llama, Qwen, etc.
    """
    def __init__(self):
        self.region = settings.aws.region
        kwargs = {"region_name": self.region}
        if settings.aws.access_key_id and settings.aws.secret_access_key:
            kwargs["aws_access_key_id"] = settings.aws.access_key_id
            kwargs["aws_secret_access_key"] = settings.aws.secret_access_key

        self.client = boto3.client("bedrock-runtime", **kwargs)
        self.model_id = settings.llm.default_model

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        start_time = time.time()

        # Prepare system prompt and messages
        system_prompts = []
        if request.system_prompt:
            system_prompts = [{"text": request.system_prompt}]

        messages = [{"role": "user", "content": [{"text": request.prompt}]}]

        try:
            response = self.client.converse(
                modelId=self.model_id,
                messages=messages,
                system=system_prompts,
                inferenceConfig={
                    "maxTokens": request.max_tokens,
                    "temperature": request.temperature
                }
            )

            text = response["output"]["message"]["content"][0]["text"]
            usage = response.get("usage", {})
            token_usage = {
                "input_tokens": usage.get("inputTokens", 0),
                "output_tokens": usage.get("outputTokens", 0)
            }
            finish_reason = response.get("stopReason", "completed")
            latency = time.time() - start_time

            return GenerationResponse(
                text=text,
                model_id=self.model_id,
                provider="Bedrock-Converse",
                usage=token_usage,
                latency=latency,
                finish_reason=finish_reason
            )
        except Exception as e:
            logger.error(f"Bedrock generation failed: {e}")
            raise RuntimeError(f"Bedrock generation failed: {e}")

    async def stream_generate(self, request: GenerationRequest) -> AsyncGenerator[StreamEvent, None]:
        start_time = time.time()

        system_prompts = []
        if request.system_prompt:
            system_prompts = [{"text": request.system_prompt}]

        messages = [{"role": "user", "content": [{"text": request.prompt}]}]

        try:
            response = self.client.converse_stream(
                modelId=self.model_id,
                messages=messages,
                system=system_prompts,
                inferenceConfig={
                    "maxTokens": request.max_tokens,
                    "temperature": request.temperature
                }
            )

            stream = response.get("stream")
            input_tokens = 0
            output_tokens = 0

            if stream:
                for event in stream:
                    # Capture content delta
                    if "contentBlockDelta" in event:
                        delta = event["contentBlockDelta"]["delta"]
                        if "text" in delta:
                            yield StreamEvent(chunk=delta["text"], is_final=False)

                    # Capture token usage from metadata or stop event
                    if "metadata" in event:
                        metadata = event["metadata"]
                        if "usage" in metadata:
                            usage = metadata["usage"]
                            input_tokens = usage.get("inputTokens", input_tokens)
                            output_tokens = usage.get("outputTokens", output_tokens)

            latency = time.time() - start_time
            yield StreamEvent(
                chunk="",
                is_final=True,
                metadata={
                    "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
                    "latency": latency,
                    "model": self.model_id
                }
            )
        except Exception as e:
            logger.error(f"Bedrock streaming failed: {e}")
            raise RuntimeError(f"Bedrock streaming failed: {e}")

    def health_check(self) -> bool:
        try:
            # Check model availability by testing a minimal request
            self.client.converse(
                modelId=self.model_id,
                messages=[{"role": "user", "content": [{"text": "ping"}]}],
                inferenceConfig={"maxTokens": 1}
            )
            return True
        except Exception:
            return False
