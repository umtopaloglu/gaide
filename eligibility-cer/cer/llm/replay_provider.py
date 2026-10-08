"""Offline provider: returns recorded responses (tests, demos, reproducible re-runs).  No network, no key.
Recording file: {"responses": {"<criterion display number>": <proposal JSON>, ...}}"""
import json

from .base import LLMProvider, ProviderError, ProviderResult


class ReplayProvider(LLMProvider):
    name = "replay"

    def __init__(self, **options):
        options.setdefault("model", "replay")
        super().__init__(**options)
        self._data = json.load(open(options["path"], encoding="utf-8"))["responses"]

    def complete_json(self, system, user, schema, schema_name):
        key = next((k for k in self._data if f"Criterion: {k}\n" in user), None)
        if key is None:
            raise ProviderError("no recorded response for this criterion")
        return ProviderResult(data=self._data[key], provider=self.name, model_requested=self.model,
                              model_served=self.model, stop_reason="end_turn", raw_text=json.dumps(self._data[key]))
