"""Claude via the official Anthropic Python SDK (pip install anthropic).

Credentials: the SDK's normal resolution (ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN, or an `ant auth login` profile).
Structured outputs (output_config.format = json_schema) constrain the reply to the proposal schema.
Server-side refusal fallback ("default") is enabled by default; set "fallbacks": null in the config to turn it off.
"""
import json

from .base import LLMProvider, ProviderError, ProviderRefusal, ProviderResult

FALLBACK_BETA = "server-side-fallback-2026-07-01"     # gates the `fallbacks: "default"` scalar form


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, client=None, **options):
        options.setdefault("model", "claude-opus-5-5")
        options.setdefault("effort", "high")          # Opus 5.5 defaults to medium; extraction fidelity wants high
        options.setdefault("max_tokens", 16000)
        options.setdefault("fallbacks", "default")
        super().__init__(**options)
        self._client = client                         # injectable for tests

    def _get_client(self):
        if self._client is None:
            try:
                import anthropic
            except ImportError as e:
                raise ProviderError("anthropic SDK not installed: pip install anthropic") from e
            self._client = anthropic.Anthropic(timeout=self.options.get("timeout_s", 600),
                                               max_retries=self.options.get("max_retries", 2))
        return self._client

    def complete_json(self, system, user, schema, schema_name):
        import anthropic
        o = self.options
        req = dict(model=o["model"], max_tokens=o["max_tokens"], system=system,
                   messages=[{"role": "user", "content": user}],
                   thinking={"type": "adaptive"},
                   output_config={"effort": o["effort"], "format": {"type": "json_schema", "schema": schema}})
        client = self._get_client()
        try:
            if o.get("fallbacks"):
                resp = client.beta.messages.create(betas=[FALLBACK_BETA], fallbacks=o["fallbacks"], **req)
            else:
                resp = client.messages.create(**req)
        except anthropic.AuthenticationError as e:
            raise ProviderError("authentication failed (check ANTHROPIC_API_KEY or `ant auth login`)") from e
        except anthropic.RateLimitError as e:
            raise ProviderError(f"rate limited: {e}") from e
        except anthropic.BadRequestError as e:
            raise ProviderError(f"bad request: {e.message}") from e
        except anthropic.APIStatusError as e:
            raise ProviderError(f"API error {e.status_code}: {e.message}") from e
        except anthropic.APIConnectionError as e:
            raise ProviderError(f"connection error: {e}") from e
        if resp.stop_reason == "refusal":
            cat = getattr(getattr(resp, "stop_details", None), "category", None)
            raise ProviderRefusal(f"model declined (category={cat})")
        if resp.stop_reason == "max_tokens":
            raise ProviderError("output truncated at max_tokens; raise max_tokens in llm.config.json")
        text = next((b.text for b in resp.content if b.type == "text"), None)
        if text is None:
            raise ProviderError("no text block in response")
        try:
            data = json.loads(text)
        except ValueError as e:
            raise ProviderError(f"response was not valid JSON: {e}") from e
        u = getattr(resp, "usage", None)
        return ProviderResult(data=data, provider=self.name, model_requested=o["model"], model_served=getattr(resp, "model", None),
                              request_id=getattr(resp, "_request_id", None), stop_reason=resp.stop_reason,
                              usage={"input_tokens": getattr(u, "input_tokens", None), "output_tokens": getattr(u, "output_tokens", None)},
                              raw_text=text)
