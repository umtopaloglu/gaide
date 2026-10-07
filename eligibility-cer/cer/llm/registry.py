"""Provider registry.  Built-ins: anthropic, replay.  Add any other API with a config entry:
    "my_llm": {"class": "my_package.my_module:MyProvider", "model": "...", ...}
where MyProvider subclasses cer.llm.base.LLMProvider and implements complete_json()."""
import importlib
import json
import os

from .anthropic_provider import AnthropicProvider
from .base import LLMProvider, ProviderError
from .replay_provider import ReplayProvider

BUILTIN = {"anthropic": AnthropicProvider, "replay": ReplayProvider}
HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG = os.path.join(HERE, "llm.config.json")


def load_config(path=CONFIG):
    if not os.path.exists(path):
        return {"default_provider": "anthropic", "providers": {"anthropic": {}}}
    return json.load(open(path, encoding="utf-8"))


def get_provider(name=None, config=None, **overrides) -> LLMProvider:
    cfg = config or load_config()
    name = name or cfg.get("default_provider", "anthropic")
    opts = dict(cfg.get("providers", {}).get(name, {}))
    opts.update({k: v for k, v in overrides.items() if v is not None})
    cls_ref = opts.pop("class", None)
    if cls_ref:
        mod, _, attr = cls_ref.partition(":")
        cls = getattr(importlib.import_module(mod), attr)
    elif name in BUILTIN:
        cls = BUILTIN[name]
    else:
        raise ProviderError(f"unknown provider '{name}': add it to llm.config.json with a \"class\" entry")
    if not issubclass(cls, LLMProvider):
        raise ProviderError(f"{cls_ref} must subclass cer.llm.base.LLMProvider")
    return cls(**opts)
