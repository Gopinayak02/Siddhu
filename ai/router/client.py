from __future__ import annotations

import json
import urllib.error
import urllib.request


class RouterError(RuntimeError):
    pass


class OmniRouterClient:
    """
    Generic adapter for an OpenAI-compatible router endpoint.

    Configure:
      OMNI_ROUTER_URL
      OMNI_ROUTER_API_KEY
      OMNI_ROUTER_MODEL

    The exact private Omni Router contract may differ. Keep that
    integration detail here instead of spreading it through SIDDHU.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str = "",
        model: str = "",
        timeout: float = 60.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def chat(self, text: str) -> str:
        if not self.base_url or not self.model:
            raise RouterError(
                "OMNI_ROUTER_URL and OMNI_ROUTER_MODEL must be configured."
            )

        url = self.base_url
        if not url.endswith("/chat/completions"):
            url += "/chat/completions"

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": text,
                }
            ],
        }

        body = json.dumps(payload).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
        }

        if self.api_key:
            headers["Authorization"] = (
                f"Bearer {self.api_key}"
            )

        request = urllib.request.Request(
            url,
            data=body,
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                result = json.loads(
                    response.read().decode("utf-8")
                )
        except urllib.error.URLError as exc:
            raise RouterError(
                f"AI Router request failed: {exc}"
            ) from exc

        try:
            return (
                result["choices"][0]["message"]["content"]
                .strip()
            )
        except (KeyError, IndexError, TypeError) as exc:
            raise RouterError(
                f"Unexpected router response: {result}"
            ) from exc

    def health_check(self) -> bool:
        return bool(self.base_url and self.model)
