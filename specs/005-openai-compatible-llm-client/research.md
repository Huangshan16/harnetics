# Research: OpenAI-compatible LLM 调用收敛

## Decision 1: 远端 LLM 调用改为 OpenAI-compatible 原生客户端

**Decision**: 对 OpenAI-compatible 网关使用 OpenAI SDK 直接调用会话接口，传递原始模型名与 `base_url`。

**Rationale**: 用户当前痛点不是“能不能接远端模型”，而是远端调用仍然依赖 LiteLLM 特有的 provider/model 语义，导致运行时误路由和难以诊断的本地回退。直接采用 OpenAI-compatible 原生语义，可以把“配置中的模型名”与“请求体中的模型名”统一起来。

**Alternatives considered**:
- 保留 litellm 远端调用：仍然需要 provider 前缀或额外归一化规则，不能从根上消除路由歧义。
- 直接用 `httpx` 手写请求：可以工作，但错误类型、超时语义和响应解析都需要自己维护，不如官方 SDK 收敛。

## Decision 2: 诊断层继续保留 normalized effective model

**Decision**: 远端请求体使用原始模型名；系统内部诊断与状态端点继续保留 normalized effective model / effective base 这类字段。

**Rationale**: 用户需要两种视角：请求时发给网关的原始模型名，以及服务内部判定当前走的是哪条路由。两者分开才能既满足 OpenAI-compatible 语义，又保留稳定诊断面。

**Alternatives considered**:
- 只保留原始模型名：排查本地/远端路由时信息不够。
- 请求体也发送 normalized model：会重新引入 LiteLLM 风格的 provider 前缀耦合。

## Decision 3: 显式本地配置路径保留，不做隐式本地回退

**Decision**: 本地 Ollama 仍支持，但必须通过显式本地模型/本地基地址配置进入；远端配置异常时不再静默回退到本地默认模型。

**Rationale**: 当前最大的排障成本来自“配置坏了，却看起来像系统偷偷改走本地”。保留本地能力没问题，但必须让进入本地路径的条件显式可见。

**Alternatives considered**:
- 远端失败时自动改走本地：表面上更“稳”，实际上会制造错误结果和调试假象。
- 完全删除本地路径：会破坏当前离线联调和已有默认工作流。

## Decision 4: `.env` 解析以显式文件 > cwd > repo-root 收敛

**Decision**: `get_settings()` 优先读取 `HARNETICS_ENV_FILE`，其次 `cwd/.env`，最后仓库根目录 `.env`。

**Rationale**: 当前服务可能从仓库子目录、热重载子进程或测试目录启动。只有把配置来源顺序明确下来，状态端点才有意义，运行时行为也才稳定。

**Alternatives considered**:
- 只读 `cwd/.env`：对子目录启动和热重载进程不稳定。
- 只读仓库根 `.env`：会破坏显式临时环境文件和测试目录覆盖场景。

## Decision 5: 当前特性不扩大到 embedding 主路径改造

**Decision**: 本特性只收敛 LLM completion/judgement 调用链；embedding 路由保持现状。

**Rationale**: 用户请求明确针对“AI 调用逻辑”与 OpenAI-compatible 会话接口。把 embedding 一起重构会扩大测试面和风险，且不是当前阻塞点。

**Alternatives considered**:
- 同时改造 embedding：范围更“完整”，但会把当前特性扩成两类协议迁移。
- 顺手删除 litellm：如果 embedding 仍依赖它，会制造新的非目标破坏。