# 密钥和密码说明

这个文件只说明需要哪些密钥，不包含真实值。

## 不要提交到 GitHub 的内容

- 服务器 root 密码
- SSH 私钥文件
- 模型 API Key
- 飞书 AppSecret
- RAGFlow API Key
- worker token
- `.env`
- `ragflow-api-key.txt`
- 数据库文件
- 生成出来的用户资料、试卷、PDF、PPT、日志

## Windows 本地需要配置

`D:\HermesRAG\paper-asset\.env`：

```text
OPENAI_BASE_URL=真实模型接口地址
OPENAI_API_KEY=真实模型 API Key
OPENAI_MODEL=模型名
WORKER_TOKEN=本地 worker token
WORK_DIR=D:\HermesRAG\paper-asset\work
OUTPUT_DIR=D:\HermesRAG\paper-asset\outputs
LLM_TRUST_ENV_PROXY=0
```

反向隧道环境变量：

```powershell
$env:HERMES_SERVER="root@服务器 IP"
$env:HERMES_TUNNEL_KEY="SSH 私钥路径"
```

## 服务器需要配置

`/opt/hermes-ragflow/ragflow.env`：

```text
RAGFLOW_BASE_URL=http://127.0.0.1:19380
RAGFLOW_API_KEY=真实 RAGFlow API Key
TEACHER_FILE_ARCHIVE_URL=http://127.0.0.1:18765/store
TEACHER_RESOURCE_API_URL=http://127.0.0.1:15128/api
PAPER_ASSET_WORKER_URL=http://127.0.0.1:18766
PAPER_ASSET_WORKER_TOKEN=和 Windows WORKER_TOKEN 一样
PAPER_ASSET_OUTPUT_DIR=/opt/hermes-ragflow/outputs/paper-assets
```

## 飞书机器人

Hermes 里如果要继续接飞书，需要飞书：

- App ID
- App Secret
- 事件/消息权限
- WebSocket 或事件订阅配置

这些真实值只应该放在服务器环境变量或 Hermes 配置中，不应该写进 GitHub。

## 建议

交接后建议重新生成或轮换：

- 模型 API Key
- 飞书 AppSecret
- 服务器 root 密码或改用 SSH key
- RAGFlow API Key
- worker token
