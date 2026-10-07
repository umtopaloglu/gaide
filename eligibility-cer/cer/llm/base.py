"""Provider interface.  Implement `complete_json` and register the class in llm.config.json."""
from dataclasses import dataclass, field


class ProviderError(Exception):
    """Technical failure (network, auth, rate limit, malformed output).  Never a clinical result."""


class ProviderRefusal(ProviderError):
    """The model declined.  The criterion simply stays as it was (rule-based / narrative)."""


@dataclass
class ProviderResult:
    data: dict                         # parsed JSON matching the requested schema
    provider: str
    model_requested: str
    model_served: str | None = None    # may differ when a server-side fallback answered
    request_id: str | None = None
    stop_reason: str | None = None
    usage: dict = field(default_factory=dict)
    raw_text: str | None = None


class LLMProvider:
    """Base class.  `options` comes from llm.config.json; secrets come ONLY from environment variables."""
    name = "base"

    def __init__(self, **options):
        self.options = options

    @property
    def model(self) -> str:
        return self.options.get("model", "unknown")

    def complete_json(self, system: str, user: str, schema: dict, schema_name: str) -> ProviderResult:
        raise NotImplementedError

    def describe(self) -> dict:
        """Recorded in provenance (no secrets)."""
        return {"provider": self.name, **{k: v for k, v in self.options.items() if "key" not in k.lower() and "token" not in k.lower()}}
