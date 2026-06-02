# 部署说明

下面按“Windows 本地机器 + 远程 Hermes 服务器”的方式说明。

## 1. Windows 本地目录

推荐固定使用：

```text
D:\HermesRAG
```

创建目录：

```powershell
New-Item -ItemType Directory -Force -Path D:\HermesRAG | Out-Null
```

复制仓库内容：

```powershell
Copy-Item -Recurse -Force .\src\paper-asset D:\HermesRAG\paper-asset
Copy-Item -Recurse -Force .\scripts D:\HermesRAG\scripts
Copy-Item -Recurse -Force .\skills D:\HermesRAG\skills
```

## 2. Python 依赖

需要 Python 3.10+。

```powershell
pip install -r D:\HermesRAG\paper-asset\requirements.txt
```

主要依赖：

- FastAPI / Uvicorn：本地 worker 服务
- requests：调用大模型 API
- PyMuPDF / Pillow：PDF 和图片预处理
- python-docx：生成 DOCX
- reportlab：生成 PDF
- python-pptx：后续生成讲题 PPT 用

## 3. 配置旧试卷 worker

复制环境变量模板：

```powershell
Copy-Item D:\HermesRAG\paper-asset\.env.example D:\HermesRAG\paper-asset\.env
```

编辑 `D:\HermesRAG\paper-asset\.env`：

```text
OPENAI_BASE_URL=https://your-openai-compatible-endpoint/v1
OPENAI_API_KEY=真实模型 API Key
OPENAI_MODEL=gpt-5.5

WORKER_TOKEN=自己生成一个随机 token
WORK_DIR=D:\HermesRAG\paper-asset\work
OUTPUT_DIR=D:\HermesRAG\paper-asset\outputs
LLM_TRUST_ENV_PROXY=0
```

启动：

```powershell
& D:\HermesRAG\scripts\start-paper-asset-worker.ps1
```

检查：

```powershell
& D:\HermesRAG\scripts\status-paper-asset-worker.ps1
```

健康返回应类似：

```json
{"ok":true,"root":"D:\\HermesRAG\\paper-asset","has_api_key":true}
```

## 4. 本地文件归档服务

`scripts/teacher_file_receiver.py` 用来把服务器上传来的原文件保存到本机：

```text
D:\HermesRAG\teacher-files\资料库名\
```

它会随 `start-ragflow-tunnel.ps1` 一起启动，监听：

```text
http://127.0.0.1:18765
```

## 5. 反向 SSH 隧道

因为 Hermes 在远程服务器上，RAGFlow/worker 在 Windows 本机，所以需要反向隧道。

脚本会转发：

```text
服务器 127.0.0.1:18080 -> 本机 127.0.0.1:8080   # RAGFlow Web
服务器 127.0.0.1:19380 -> 本机 127.0.0.1:9380   # RAGFlow API
服务器 127.0.0.1:19382 -> 本机 127.0.0.1:9382
服务器 127.0.0.1:18765 -> 本机 127.0.0.1:18765 # 文件归档
服务器 127.0.0.1:18766 -> 本机 127.0.0.1:18766 # 旧试卷 worker
服务器 127.0.0.1:15128 -> 本机 127.0.0.1:5128  # teacher-resource API
```

设置环境变量：

```powershell
$env:HERMES_SERVER="root@YOUR_SERVER_IP"
$env:HERMES_TUNNEL_KEY="D:\path\to\server_tunnel_rsa"
```

启动：

```powershell
& D:\HermesRAG\scripts\start-ragflow-tunnel.ps1
```

检查：

```powershell
& D:\HermesRAG\scripts\status-ragflow-tunnel.ps1
```

## 6. 服务器 Hermes MCP

在服务器上创建目录：

```bash
mkdir -p /opt/hermes-ragflow/outputs/paper-assets
```

复制：

```bash
cp src/server/teacher_ragflow_mcp.py /opt/hermes-ragflow/teacher_ragflow_mcp.py
```

复制环境变量模板并填真实值：

```bash
cp src/server/ragflow.env.example /opt/hermes-ragflow/ragflow.env
```

`/opt/hermes-ragflow/ragflow.env` 需要：

```text
RAGFLOW_BASE_URL=http://127.0.0.1:19380
RAGFLOW_API_KEY=真实 RAGFlow API Key
TEACHER_FILE_ARCHIVE_URL=http://127.0.0.1:18765/store
TEACHER_RESOURCE_API_URL=http://127.0.0.1:15128/api
PAPER_ASSET_WORKER_URL=http://127.0.0.1:18766
PAPER_ASSET_WORKER_TOKEN=和 Windows .env 一样的 WORKER_TOKEN
PAPER_ASSET_OUTPUT_DIR=/opt/hermes-ragflow/outputs/paper-assets
```

语法检查：

```bash
/root/.hermes/hermes-agent/venv/bin/python -m py_compile /opt/hermes-ragflow/teacher_ragflow_mcp.py
```

## 7. Hermes config 需要加入的 MCP 工具

在 `/root/.hermes/config.yaml` 的 `mcp_servers.teacher_ragflow.tools.include` 中至少包含：

```yaml
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

## 8. teacher-resource-system 接入

原项目地址：

```text
https://gitee.com/wh517415640/teacher-resource-system.git
```

应用补丁：

```bash
git clone https://gitee.com/wh517415640/teacher-resource-system.git
cd teacher-resource-system
git apply /path/to/teacher-resource-ragflow-integration.patch
```

补丁文件在：

```text
integrations/teacher-resource-system/teacher-resource-ragflow-integration.patch
```

本地开发建议使用 SQLite，连接串示例：

```json
{
  "Database": { "Provider": "Sqlite" },
  "ConnectionStrings": {
    "DefaultConnection": "Data Source=D:\\HermesRAG\\teacher-resource.db"
  }
}
```

## 9. 常见问题

如果 worker 调大模型时报代理/TLS 错：

```text
ProxyError / SSLError / EOF occurred in violation of protocol
```

保持：

```text
LLM_TRUST_ENV_PROXY=0
```

这样 requests 不继承 Windows/Clash 系统代理。

如果服务器访问不到本机 worker，先查：

```powershell
& D:\HermesRAG\scripts\status-ragflow-tunnel.ps1
```

确认服务器上能访问：

```bash
curl http://127.0.0.1:18766/health
```
