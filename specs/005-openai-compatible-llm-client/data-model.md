# Data Model: OpenAI-compatible LLM 调用收敛

## Entity: AIRouteConfig

描述服务进程当前打算采用的 LLM 路由配置。

| Field | Type | Description |
|-------|------|-------------|
| requested_model | str | 来自配置的原始模型名，如 `claude-sonnet-4-6` 或 `claude-sonnet-4-6-think` |
| effective_model | str | 服务内部用于诊断的标准化模型标识，如 `openai/claude-sonnet-4-6` 或 `ollama/gemma4:26b` |
| configured_base_url | str | 配置中声明的 LLM 基地址 |
| effective_base_url | str | 服务实际采用的标准化基地址 |
| mode | str | `remote_openai_compatible` 或 `local_explicit` |
| config_env_file | str | 当前命中的 `.env` 文件路径 |

## Entity: EffectiveAIRouteSnapshot

状态接口返回的运行时路由快照，帮助工程师确认服务进程实际使用的配置。

| Field | Type | Description |
|-------|------|-------------|
| llm_model | str | 配置层看到的模型名 |
| llm_base_url | str | 配置层看到的基地址 |
| llm_effective_model | str | 服务内部判定的 effective model |
| llm_effective_base_url | str | 服务内部判定的 effective base |
| config_env_file | str | 当前命中的配置文件来源 |

## Entity: LLMInvocationFailure

统一描述远端 LLM 调用失败时对外暴露的错误上下文。

| Field | Type | Description |
|-------|------|-------------|
| effective_model | str | 出错时的 effective model |
| effective_base_url | str | 出错时的 effective base |
| error_type | str | 失败类别，如认证错误、超时、模型不可用 |
| safe_message | str | 不含密钥的可诊断错误说明 |

## State Transitions

### LLM 路由选择

```text
读取 settings
  ├─ 显式本地模型 + 本地基地址 -> local_explicit
  └─ 其他非本地基地址 -> remote_openai_compatible
```

### 运行时诊断

```text
服务启动 -> 解析配置来源 -> 构建 AIRouteConfig
  -> 调用草稿生成 / 影响分析
  -> 状态端点暴露 EffectiveAIRouteSnapshot
```