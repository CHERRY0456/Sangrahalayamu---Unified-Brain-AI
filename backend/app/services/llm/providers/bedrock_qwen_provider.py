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
    AWS Bedrock implementation for Alibaba Qwen text models.
    """
    def __init__(self):
        self.region = settings.aws.region
        kwargs = {"region_name": self.region}
        if settings.aws.access_key_id and settings.aws.secret_access_key:
            kwargs["aws_access_key_id"] = settings.aws.access_key_id
            kwargs["aws_secret_access_key"] = settings.aws.secret_access_key
            
        self.client = boto3.client("bedrock-runtime", **kwargs)
        # Using a Qwen model ID as per the requirement. E.g., 'qwen2-72b-instruct' if available on Bedrock,
        # or defaulting to what is provided in settings.
        self.model_id = getattr(settings.llm, "model", "qwen2-72b-instruct")

    def _format_prompt(self, request: GenerationRequest) -> str:
        """
        Formats the prompt for the Qwen model.
        Qwen typically uses ChatML or a standard Instruction format.
        For raw text endpoints, we might wrap it if required, but usually Bedrock handles standard messages API.
        We will use Bedrock's Converse API or invoke_model depending on exact support.
        Assuming standard invoke_model with a typical Qwen payload here.
        """
        # A simple string concatenation if using base completion API, 
        # but modern Bedrock uses Converse API or messages array for instruction models.
        # Assuming Converse API format or standard json payload:
        system = request.system_prompt + "\n\n" if request.system_prompt else ""
        return f"{system}{request.prompt}"

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        start_time = time.time()
        prompt = self._format_prompt(request)
        
        # Structure for typical text completion
        body = {
            "prompt": prompt,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "stop": request.stop_sequences if request.stop_sequences else []
        }

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                accept="application/json",
                contentType="application/json"
            )
            response_body = json.loads(response.get('body').read())
            
            # The exact response schema depends on how Qwen is deployed on Bedrock. 
            # Assuming standard fields:
            text = response_body.get("generation", "")
            usage = {
                "input_tokens": response_body.get("prompt_token_count", 0),
                "output_tokens": response_body.get("generation_token_count", 0)
            }
            finish_reason = response_body.get("stop_reason", "completed")
            
            latency = time.time() - start_time
            return GenerationResponse(
                text=text,
                model_id=self.model_id,
                provider="Bedrock-Qwen",
                usage=usage,
                latency=latency,
                finish_reason=finish_reason
            )
        except Exception as e:
            logger.error(f"Bedrock Qwen generation failed: {e}")
            raise RuntimeError(f"Bedrock Qwen generation failed: {e}")

    async def stream_generate(self, request: GenerationRequest) -> AsyncGenerator[StreamEvent, None]:
        # Boto3 is synchronous by default. To do true async we'd use aiobotocore.
        # For this implementation, we simulate the async generator using the sync invoke_model_with_response_stream.
        start_time = time.time()
        prompt = self._format_prompt(request)
        
        body = {
            "prompt": prompt,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "stop": request.stop_sequences if request.stop_sequences else []
        }

        try:
            response = self.client.invoke_model_with_response_stream(
                modelId=self.model_id,
                body=json.dumps(body),
                accept="application/json",
                contentType="application/json"
            )
            
            stream = response.get("body")
            if stream:
                for event in stream:
                    chunk = event.get("chunk")
                    if chunk:
                        chunk_obj = json.loads(chunk.get("bytes").decode())
                        text_chunk = chunk_obj.get("generation", "")
                        # Yield just the answer tokens as requested by user
                        yield StreamEvent(chunk=text_chunk, is_final=False)

                # Stream final event with metadata
                latency = time.time() - start_time
                yield StreamEvent(
                    chunk="",
                    is_final=True,
                    metadata={
                        "usage": {"input_tokens": 0, "output_tokens": 0}, # Would be parsed from final stream event in real Bedrock response
                        "latency": latency,
                        "model": self.model_id
                    }
                )
        except Exception as e:
            logger.error(f"Bedrock Qwen streaming failed: {e}")
            raise RuntimeError(f"Bedrock Qwen streaming failed: {e}")

    def health_check(self) -> bool:
        try:
            # Simple check if client can list models (or just rely on IAM configuration)
            # A lighter check could just be checking client instantiation
            self.client.list_foundation_models(byProvider="alibaba")
            return True
        except Exception:
            return False
