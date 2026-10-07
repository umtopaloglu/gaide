"""Pluggable LLM proposer: an LLM may PROPOSE a typed expression tree for a criterion; it never approves one.

Flow:  criterion text -> prompt + JSON schema -> provider.complete_json() -> deterministic validation
       (grammar, grounding of every quote in the source text) -> authored-spec -> proposals/llm/NCT.json
       -> overlaid as origin="llm_proposal", review_status="needs_review" -> dual sign-off as for any proposal.
Providers are configured in llm.config.json; add your own with {"class": "package.module:ClassName"}.
"""
from .base import LLMProvider, ProviderError, ProviderRefusal, ProviderResult  # noqa: F401
from .registry import get_provider, load_config  # noqa: F401
