# 新电脑从零复刻指南

目标：让接手人在另一台 Windows 电脑上复刻这套系统，不依赖原电脑 `D:\HermesRAG` 的运行环境。

## 总体架构

```text
飞书用户
  -> 远程服务器 Hermes Gateway
  -> Hermes MCP: /opt/hermes-ragflow/teacher_ragflow_mcp.py
  -> SSH 反向隧道
  -> 新 Windows 电脑本地服务
       - RAGFlow Web/API
       - 旧试卷加工 worker
       - teacher-resource API
       - teacher file receiver
```

## 0. 新电脑需要准备

推荐系统：

```text
Windows 10/11
D 盘至少预留 50GB
内存建议 16GB+
```

必须安装：

1. Git for Windows
2. Python 3.10 或更高版本
3. Docker Desktop
4. Node.js LTS
5. .NET 9 SDK

下载地址见 [OPEN_SOURCE_DOWNLOADS.md](OPEN_SOURCE_DOWNLOADS.md)。

## 1. 克隆交接仓库

```powershell
New-Item -ItemType Directory -Force -Path D:\handoff | Out-Null
git clone https://github.com/XFFHT/aaa.git D:\handoff\aaa
cd D:\handoff\aaa
```

## 2. 安装本地 HermesRAG 文件

运行安装脚本：

```powershell
& D:\handoff\aaa\scripts\install-windows-local.ps1 -TargetRoot D:\HermesRAG -InstallPythonDeps
```

脚本会创建：

```text
D:\HermesRAG\paper-asset
D:\HermesRAG\scripts
D:\HermesRAG\skills
D:\HermesRAG\teacher-files
D:\HermesRAG\logs
D:\HermesRAG\downloads
```

并复制：

```text
src/paper-asset -> D:\HermesRAG\paper-asset
scripts         -> D:\HermesRAG\scripts
skills          -> D:\HermesRAG\skills
```

## 3. 配置模型 API

复制模板：

```powershell
Copy-Item D:\HermesRAG\paper-asset\.env.example D:\HermesRAG\paper-asset\.env
notepad D:\HermesRAG\paper-asset\.env
```

填写：

```text
OPENAI_BASE_URL=真实模型接口地址
OPENAI_API_KEY=真实模型 API Key
OPENAI_MODEL=gpt-5.5
WORKER_TOKEN=自己生成的随机 token
WORK_DIR=D:\HermesRAG\paper-asset\work
OUTPUT_DIR=D:\HermesRAG\paper-asset\outputs
LLM_TRUST_ENV_PROXY=0
```

注意：`.env` 不要提交到 GitHub。

## 4. 安装并启动 RAGFlow

RAGFlow 建议直接从官方 GitHub 下载：

```powershell
cd D:\HermesRAG
git clone https://github.com/infiniflow/ragflow.git ragflow
cd D:\HermesRAG\ragflow\docker
```

然后按 RAGFlow 官方 README 启动 Docker Compose。常见方式是：

```powershell
docker compose up -d
```

启动后确认：

```text
RAGFlow Web: http://127.0.0.1:8080
RAGFlow API: http://127.0.0.1:9380
```

创建 RAGFlow API Key 后，保存到：

```text
D:\HermesRAG\ragflow-api-key.txt
```

也可以直接写到服务器 `/opt/hermes-ragflow/ragflow.env` 的 `RAGFLOW_API_KEY`。

## 5. 启动旧试卷加工 worker

```powershell
& D:\HermesRAG\scripts\start-paper-asset-worker.ps1
& D:\HermesRAG\scripts\status-paper-asset-worker.ps1
```

健康检查应返回：

```json
{"ok":true,"has_api_key":true}
```

## 6. teacher-resource-system 复刻

拉原开源项目：

```powershell
cd D:\HermesRAG
git clone https://gitee.com/wh517415640/teacher-resource-system.git teacher-resource-system
cd D:\HermesRAG\teacher-resource-system
git apply D:\handoff\aaa\integrations\teacher-resource-system\teacher-resource-ragflow-integration.patch
```

创建开发配置：

```powershell
notepad D:\HermesRAG\teacher-resource-system\backend\TeacherResource.Api\appsettings.Development.json
```

内容示例：

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

启动后端：

```powershell
cd D:\HermesRAG\teacher-resource-system\backend\TeacherResource.Api
dotnet run
```

启动前端：

```powershell
cd D:\HermesRAG\teacher-resource-system\frontend\teacher-resource-web
npm install
npm run dev
```

默认：

```text
前端：http://localhost:5173
后端：http://127.0.0.1:5128/api/health
```

## 7. 配置远程 Hermes 服务器

把 MCP 复制到服务器：

```bash
mkdir -p /opt/hermes-ragflow/outputs/paper-assets
cp src/server/teacher_ragflow_mcp.py /opt/hermes-ragflow/teacher_ragflow_mcp.py
cp src/server/ragflow.env.example /opt/hermes-ragflow/ragflow.env
```

编辑 `/opt/hermes-ragflow/ragflow.env`：

```text
RAGFLOW_BASE_URL=http://127.0.0.1:19380
RAGFLOW_API_KEY=真实 RAGFlow API Key
TEACHER_FILE_ARCHIVE_URL=http://127.0.0.1:18765/store
TEACHER_RESOURCE_API_URL=http://127.0.0.1:15128/api
PAPER_ASSET_WORKER_URL=http://127.0.0.1:18766
PAPER_ASSET_WORKER_TOKEN=和 Windows .env 里的 WORKER_TOKEN 一样
PAPER_ASSET_OUTPUT_DIR=/opt/hermes-ragflow/outputs/paper-assets
```

检查：

```bash
/root/.hermes/hermes-agent/venv/bin/python -m py_compile /opt/hermes-ragflow/teacher_ragflow_mcp.py
```

Hermes config 加入工具：

```yaml
mcp_servers:
  teacher_ragflow:
    command: /root/.hermes/hermes-agent/venv/bin/python
    args:
      - /opt/hermes-ragflow/teacher_ragflow_mcp.py
    enabled: true
    timeout: 1200
    connect_timeout: 60
    tools:
      include:
        - ragflow_status
        - ragflow_create_dataset
        - ragflow_create_teacher_library
        - ragflow_list_datasets
        - ragflow_ingest_file
        - ragflow_retrieve
        - teacher_paper_asset_package
```

重启：

```bash
systemctl restart hermes-gateway
systemctl is-active hermes-gateway
```

## 8. 新电脑启动反向隧道

在 Windows 新电脑上设置：

```powershell
$env:HERMES_SERVER="root@服务器IP"
$env:HERMES_TUNNEL_KEY="D:\path\to\server_tunnel_rsa"
& D:\HermesRAG\scripts\start-ragflow-tunnel.ps1
```

检查：

```powershell
& D:\HermesRAG\scripts\status-ragflow-tunnel.ps1
```

服务器侧应能访问：

```bash
curl http://127.0.0.1:18766/health
curl http://127.0.0.1:15128/api/health
curl http://127.0.0.1:18765/healthz
```

## 9. 飞书测试话术

```text
帮我创建一个四年级英语题库。
```

```text
把我刚上传的这份四年级英语旧试卷清版，生成教学资产包，学科英语，年级四年级，输出 docx 和 pdf。
```

```text
把我刚上传的资料入库到四年级英语题库。
```

## 10. 迁移原电脑数据

如果要把原电脑的资料也迁过去，需要额外复制：

```text
D:\HermesRAG\teacher-files
D:\HermesRAG\ragflow-data 或 RAGFlow Docker volume
D:\HermesRAG\teacher-resource.db
```

这些属于用户数据，不应该放 GitHub。详见 [DATA_MIGRATION.md](DATA_MIGRATION.md)。
