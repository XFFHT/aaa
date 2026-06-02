# 配置项总表

## Windows 本地旧试卷 worker

文件：

```text
D:\HermesRAG\paper-asset\.env
```

| 配置项 | 说明 | 示例 |
| --- | --- | --- |
| `OPENAI_BASE_URL` | OpenAI-compatible 模型接口地址 | `https://example.com/v1` |
| `OPENAI_API_KEY` | 模型 API Key | 不进 GitHub |
| `OPENAI_MODEL` | 模型名 | `gpt-5.5` |
| `WORKER_TOKEN` | 服务器调用本机 worker 的鉴权 token | 自己生成随机字符串 |
| `WORK_DIR` | 临时工作目录 | `D:\HermesRAG\paper-asset\work` |
| `OUTPUT_DIR` | 输出目录 | `D:\HermesRAG\paper-asset\outputs` |
| `LLM_TRUST_ENV_PROXY` | 是否继承系统代理 | 默认 `0` |

## Windows 反向隧道

PowerShell 环境变量：

| 配置项 | 说明 | 示例 |
| --- | --- | --- |
| `HERMES_SERVER` | 远程 Hermes 服务器 SSH 登录目标 | `root@YOUR_SERVER_IP` |
| `HERMES_TUNNEL_KEY` | SSH 私钥路径 | `D:\keys\server_tunnel_rsa` |

## 服务器 MCP

文件：

```text
/opt/hermes-ragflow/ragflow.env
```

| 配置项 | 说明 | 示例 |
| --- | --- | --- |
| `RAGFLOW_BASE_URL` | 服务器通过隧道访问本机 RAGFlow API | `http://127.0.0.1:19380` |
| `RAGFLOW_API_KEY` | RAGFlow API Key | 不进 GitHub |
| `TEACHER_FILE_ARCHIVE_URL` | 本机文件归档服务 | `http://127.0.0.1:18765/store` |
| `TEACHER_RESOURCE_API_URL` | teacher-resource 后端 API | `http://127.0.0.1:15128/api` |
| `PAPER_ASSET_WORKER_URL` | 旧试卷 worker | `http://127.0.0.1:18766` |
| `PAPER_ASSET_WORKER_TOKEN` | 和 Windows `WORKER_TOKEN` 一样 | 不进 GitHub |
| `PAPER_ASSET_OUTPUT_DIR` | 服务器下载生成文件的位置 | `/opt/hermes-ragflow/outputs/paper-assets` |

## teacher-resource-system

文件：

```text
D:\HermesRAG\teacher-resource-system\backend\TeacherResource.Api\appsettings.Development.json
```

建议开发配置：

```json
{
  "Database": { "Provider": "Sqlite" },
  "ConnectionStrings": {
    "DefaultConnection": "Data Source=D:\\HermesRAG\\teacher-resource.db"
  },
  "RagFlow": {
    "BaseUrl": "http://127.0.0.1:9380",
    "ApiKeyFile": "D:\\HermesRAG\\ragflow-api-key.txt"
  }
}
```

## 端口总表

| 本机端口 | 服务器端口 | 服务 |
| --- | --- | --- |
| `8080` | `18080` | RAGFlow Web |
| `9380` | `19380` | RAGFlow API |
| `9382` | `19382` | RAGFlow 相关服务 |
| `18765` | `18765` | 文件归档服务 |
| `18766` | `18766` | 旧试卷 worker |
| `5128` | `15128` | teacher-resource API |
