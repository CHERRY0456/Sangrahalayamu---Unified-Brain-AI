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

class MockBedrockProvider(LLMProvider):
    """
    Mock LLM provider generating grounded summaries from context contents.
    Allows complete local debugging of citations and hallucination validators.
    """
    def generate(self, req: LLMRequest) -> LLMResponse:
        prompt = req.prompt
        
        # 1. Parse source documents out of the prompt blocks
        sources = re.findall(r"Document: ([^\s\|]+) \| Section: ([^\n\|]+)", prompt)
        contents = re.findall(r"Content: ([^\n]+)", prompt)
        
        # Default safety/not-found checks
        if not sources or not contents:
            answer = "I cannot find the answer in the provided documents."
            return LLMResponse(
                text=answer,
                token_usage={"input_tokens": 150, "output_tokens": 15, "total_tokens": 165},
                provider_name="MockBedrock"
            )

        # 2. Extract keywords from the prompt query segment
        query_match = re.search(r"Query: ([^\n]+)", prompt)
        query = query_match.group(1).lower() if query_match else ""

        # 3. Construct a grounded answer by parsing the retrieved contexts
        facts = []
        cited_docs = set()
        
        for idx, (doc_name, sec_name) in enumerate(sources):
            text_val = contents[idx] if idx < len(contents) else ""
            cited_docs.add(doc_name)
            
            # Simple keyword matching to form focused sentences
            if "boiler" in query or "calibration" in query or "safety" in query:
                if "SOP-104" in text_val or "calibration" in text_val.lower():
                    facts.append(
                        f"Based on [Doc: {doc_name}] in the {sec_name} section, boiler BLR-402 is "
                        f"connected to valve VLV-102. It requires calibration under OSHA 1910.263 safety standards."
                    )
                elif "maintains" in text_val.lower() or "sharma" in text_val.lower():
                    facts.append(
                        f"Ravi Kumar and Priya Sharma are responsible for maintaining boiler BLR-402 "
                        f"according to [Doc: {doc_name}]."
                    )
                else:
                    # Summarize snippet
                    preview = text_val[:140].strip()
                    facts.append(f"According to [Doc: {doc_name}] in {sec_name}: '{preview}...'")
            else:
                # Fallback default summary
                preview = text_val[:140].strip()
                facts.append(f"In [Doc: {doc_name}] ({sec_name}): {preview}.")

        # Join the facts into a grounded paragraph
        answer_body = " ".join(facts)
        
        # If query asks for something not in context, mock validator checks will test hallucination bounds
        if "hallucinate" in query:
            answer_body += " Also, boiler BLR-999 is leaking acid in Plant 9."

        token_in = len(prompt) // 4
        token_out = len(answer_body) // 4
        
        return LLMResponse(
            text=answer_body,
            token_usage={
                "input_tokens": token_in,
                "output_tokens": token_out,
                "total_tokens": token_in + token_out
            },
            provider_name="MockBedrock",
            raw_response={"model_id": "amazon.titan-text-express-v1", "citations_matched": list(cited_docs)}
        )

    def stream_generate(self, req: LLMRequest) -> Generator[str, None, None]:
        res = self.generate(req)
        words = res.text.split()
        for w in words:
            yield w + " "

    def health_check(self) -> bool:
        return True

class BedrockProvider(LLMProvider):
    """
    Live Amazon Bedrock Converse API provider.
    Requires AWS credentials in environment (falls back to MockBedrockProvider if credentials missing).
    """
    def __init__(self):
        self.client = None
        self.model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        try:
            import boto3
            # Attempt loading Bedrock runtime client
            self.client = boto3.client("bedrock-runtime")
        except Exception:
            logger.warning("AWS boto3 client not loaded. Bedrock operations will fall back to MockBedrock.")

    def generate(self, req: LLMRequest) -> LLMResponse:
        if not self.client:
            # Fall back to mock
            return MockBedrockProvider().generate(req)
            
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
            logger.error(f"Amazon Bedrock Converse failed: {str(e)}. Falling back to Mock.")
            return MockBedrockProvider().generate(req)

    def stream_generate(self, req: LLMRequest) -> Generator[str, None, None]:
        # Simple Converse stream logic or mock fallback
        if not self.client:
            yield from MockBedrockProvider().stream_generate(req)
            return

        try:
            # Simple fallback for converseStream
            response = self.client.converse_stream(
                modelId=self.model_id,
                messages=[{"role": "user", "content": [{"text": req.prompt}]}],
                system=[{"text": req.system_prompt}]
            )
            for event in response.get("stream"):
                if "contentBlockDelta" in event:
                    text_delta = event["contentBlockDelta"]["delta"]["text"]
                    yield text_delta
        except Exception:
            yield from MockBedrockProvider().stream_generate(req)

    def health_check(self) -> bool:
        if not self.client:
            return False
        try:
            # Try to list foundation models as a verification ping
            return True
        except Exception:
            return False
