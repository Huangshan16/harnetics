# [INPUT]: 依赖 litellm、httpx、harnetics.llm.prompts
# [OUTPUT]: 对外提供 HarneticsLLM 与旧版 LocalLlmClient 后向/兼容
# [POS]: llm 包的 HTTP 客户端，harnetics 与本地 LLM 服务之间的最小适配层
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from __future__ import annotations

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

    def __init__(self, model: str = "ollama/gemma4:26b-it-a4b-q4_K_M") -> None:
        self.model = model

    def generate_draft(self, system_prompt: str, context: str, user_request: str) -> str:
        """调用 LLM 生成草稿 Markdown。"""
        import litellm  # 延迟导入，避免冷启动时加载
        response = litellm.completion(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"## 参考文档\n\n{context}\n\n## 任务\n\n{user_request}"},
            ],
            temperature=0.3,
            max_tokens=8192,
            top_p=0.9,
        )
        return response.choices[0].message.content  # type: ignore[union-attr]

    def check_availability(self) -> bool:
        """测试 Ollama 是否在线（快速 HTTP 探测，不发起 LLM 请求）。"""
        try:
            base_url = "http://localhost:11434"
            if "ollama" in self.model:
                # 仅做 TCP 连通性检查，避免 litellm 长阻塞
                resp = httpx.get(f"{base_url}/api/tags", timeout=2.0)
                return resp.status_code == 200
            return False
        except Exception:
            return False

