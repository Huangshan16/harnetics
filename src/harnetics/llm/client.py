# [INPUT]: 依赖 os、litellm、httpx
# [OUTPUT]: 对外提供 HarneticsLLM 与旧版 LocalLlmClient 后向/兼容
# [POS]: llm 包的模型调用适配层，统一本地 Ollama 与 OpenAI-compatible 提供方接入
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from __future__ import annotations

import os

import httpx


class LocalLlmClient:
    """旧版客户端，保留后向兼容。"""
    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate_markdown(self, *, prompt: str) -> str:
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"]


class HarneticsLLM:
    """litellm 封装的主 LLM 客户端，用于草稿生成。"""

    def __init__(
        self,
        model: str = "ollama/gemma4:26b-it-a4b-q4_K_M",
        api_base: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self.model = model
        self.api_base = api_base or _default_api_base(model)
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")

    def generate_draft(self, system_prompt: str, context: str, user_request: str) -> str:
        """调用 LLM 生成草稿 Markdown。"""
        import litellm  # 延迟导入，避免冷启动时加载

        request_kwargs: dict[str, str] = {}
        if self.api_base:
            request_kwargs["api_base"] = self.api_base
        if self.api_key:
            request_kwargs["api_key"] = self.api_key

        response = litellm.completion(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"## 参考文档\n\n{context}\n\n## 任务\n\n{user_request}"},
            ],
            temperature=0.3,
            max_tokens=8192,
            top_p=0.9,
            **request_kwargs,
        )
        return response.choices[0].message.content  # type: ignore[union-attr]

    def check_availability(self) -> bool:
        """返回当前 LLM 是否可用或已完成最小配置。"""
        try:
            if "ollama" in self.model:
                base_url = (self.api_base or "http://localhost:11434").rstrip("/")
                if base_url.endswith("/v1"):
                    base_url = base_url[:-3]
                # 仅做 TCP 连通性检查，避免 litellm 长阻塞
                resp = httpx.get(f"{base_url}/api/tags", timeout=2.0)
                return resp.status_code == 200
            # 云端 / OpenAI-compatible: 这里不强依赖外网探活，凭证存在即可视为可调用。
            return bool(self.api_key)
        except Exception:
            return False


def _default_api_base(model: str) -> str | None:
    custom_base = os.environ.get("HARNETICS_LLM_BASE_URL")
    if custom_base:
        return custom_base.rstrip("/")

    openai_base = os.environ.get("OPENAI_BASE_URL")
    if openai_base:
        return openai_base.rstrip("/")

    if "ollama" in model:
        return "http://localhost:11434"
    return None

