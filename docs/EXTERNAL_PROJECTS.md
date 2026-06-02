# 用到的外部项目和下载来源

## RAGFlow

用途：作为老师自己的资料库/题库/知识库，负责文件入库、切分、检索。

官方下载：

```text
https://github.com/infiniflow/ragflow
```

本项目没有把 RAGFlow 源码放进仓库。接手人需要按 RAGFlow 官方方式安装，本地运行后暴露：

```text
Web: http://127.0.0.1:8080
API: http://127.0.0.1:9380
```

## teacher-resource-system

用途：老师资源管理 Web 系统，可以管理资料、上下文包，并通过补丁接入 RAGFlow。

原始项目：

```text
https://gitee.com/wh517415640/teacher-resource-system.git
```

本仓库提供的是补丁：

```text
integrations/teacher-resource-system/teacher-resource-ragflow-integration.patch
```

补丁内容：

- 后端新增 RAGFlow Controller / Service / Options / DTO
- Resource metadata 增加 RAGFlow 入库状态字段
- 支持 SQLite 开发模式
- 前端资源详情页增加入库按钮
- 前端上下文包页增加整体入库按钮

## Hermes / Claw-ED

用途：飞书机器人后台和 MCP 工具加载运行环境。

本仓库只提供 MCP 脚本：

```text
src/server/teacher_ragflow_mcp.py
```

服务器上实际运行路径建议：

```text
/opt/hermes-ragflow/teacher_ragflow_mcp.py
```

Hermes 需要在 `/root/.hermes/config.yaml` 里配置 MCP server。

## Python 依赖

旧试卷 worker 使用：

- `fastapi`
- `uvicorn`
- `python-multipart`
- `requests`
- `Pillow`
- `PyMuPDF`
- `python-docx`
- `reportlab`
- `python-pptx`

安装：

```powershell
pip install -r D:\HermesRAG\paper-asset\requirements.txt
```

## 大模型 API

代码按 OpenAI-compatible API 调用：

```text
POST {OPENAI_BASE_URL}/chat/completions
GET  {OPENAI_BASE_URL}/models
```

需要支持文本和图片输入时，模型端要支持 `image_url` multimodal content。

真实 API Key 不要提交到 GitHub，只写入本地：

```text
D:\HermesRAG\paper-asset\.env
```
