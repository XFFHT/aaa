# HermesRAG Teacher Handoff

这是给“老师资料库 / 旧试卷加工 / RAGFlow / Hermes 飞书机器人”项目的交接仓库。

仓库里只放可公开交接的代码、脚本和说明；真实服务器密码、API Key、飞书 AppSecret、RAGFlow Key 不放进 GitHub。

## 当前已经完成

1. Windows 本地 RAGFlow 作为老师自己的资料库。
2. Windows 本地文件归档服务：飞书上传入库时，可额外保存原文件到 `D:\HermesRAG\teacher-files\资料库名\`。
3. 反向 SSH 隧道：让服务器上的 Hermes 能访问本机 RAGFlow、teacher-resource API、文件归档服务和旧试卷加工 worker。
4. Hermes MCP 工具 `teacher_ragflow`：
   - 查看 RAGFlow 状态
   - 创建资料库/题库
   - 上传文件入库并触发解析
   - 检索资料库
   - 调用 teacher-resource 入库接口
   - 调用旧试卷加工 worker
5. 旧试卷加工 worker：
   - 支持 PDF、图片、docx、txt
   - 大模型识别印刷题目，忽略手写/批改痕迹
   - 输出题型、知识点、答案、解析、难度、适配度、变式题
   - 生成 `clean_paper.docx`
   - 生成 `clean_paper.pdf`
   - 生成 `question_bank.json`
   - 生成 `analysis.md`
   - 打包 `asset_package.zip`
6. teacher-resource-system 外部项目接入补丁：
   - 新增 RAGFlow 控制器/服务/配置
   - 新增 SQLite 开发模式
   - 前端资源详情页和上下文包页增加入库按钮

## 还没有完全完成

用户最新想要的完整闭环是：

旧试卷 -> 挑出好题 -> 重新组一张新卷 -> 新卷输出 docx/pdf -> 同步生成讲题 PPT -> PPT 里包含相似题 -> 优质资料沉淀入知识库。

目前已经完成“旧试卷识别、清版、题目分析、变式题、docx/pdf/json/zip、可入库”的基础部分。

“重新组新卷”和“同步生成讲题 PPT”还需要接手人继续补齐。代码里已经预留方向：`src/paper-asset/pipeline.py` 的大模型 prompt 已要求返回 `selected_for_new_paper`、`selection_reason`、`teaching_focus`、`lesson_steps` 等字段，接下来应把这些字段用于生成 `new_paper.docx`、`new_paper.pdf` 和 `lesson_ppt.pptx`。

## 仓库结构

```text
src/paper-asset/
  pipeline.py              # 旧试卷识别、结构化、docx/pdf/json/zip 生成
  worker.py                # FastAPI worker，Hermes 通过隧道调用
  .env.example             # 本地 worker 环境变量模板
  requirements.txt         # Python 依赖

src/server/
  teacher_ragflow_mcp.py   # 服务器上的 Hermes MCP 工具
  ragflow.env.example      # 服务器 MCP 环境变量模板

scripts/
  start-paper-asset-worker.ps1
  status-paper-asset-worker.ps1
  stop-paper-asset-worker.ps1
  start-ragflow-tunnel.ps1
  status-ragflow-tunnel.ps1
  stop-ragflow-tunnel.ps1
  teacher_file_receiver.py
  create_ragflow_token.py
  export_ragflow_chunks.py

skills/
  old-paper-asset-package/SKILL.md

integrations/teacher-resource-system/
  teacher-resource-ragflow-integration.patch
  HERMES_RAGFLOW_BRIDGE.md

docs/
  DEPLOYMENT.md
  EXTERNAL_PROJECTS.md
  SECRETS_AND_PASSWORDS.md
  HANDOFF_STATUS.md
```

## 最快使用方式

详见 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)。

最短流程：

1. 在 Windows 上创建 `D:\HermesRAG`。
2. 把 `src/paper-asset`、`scripts` 复制到 `D:\HermesRAG` 对应目录。
3. 复制 `src/paper-asset/.env.example` 为 `D:\HermesRAG\paper-asset\.env`，填入真实 API Key 和 worker token。
4. 安装 Python 依赖：

```powershell
pip install -r D:\HermesRAG\paper-asset\requirements.txt
```

5. 启动旧试卷 worker：

```powershell
& D:\HermesRAG\scripts\start-paper-asset-worker.ps1
```

6. 服务器上放置 `src/server/teacher_ragflow_mcp.py` 到 `/opt/hermes-ragflow/teacher_ragflow_mcp.py`，并配置 `/opt/hermes-ragflow/ragflow.env`。
7. 设置 Windows 环境变量 `HERMES_SERVER` 和 `HERMES_TUNNEL_KEY` 后启动隧道：

```powershell
$env:HERMES_SERVER="root@YOUR_SERVER_IP"
$env:HERMES_TUNNEL_KEY="D:\path\to\server_tunnel_rsa"
& D:\HermesRAG\scripts\start-ragflow-tunnel.ps1
```

8. Hermes 配置中把 `teacher_paper_asset_package` 加入 `teacher_ragflow` MCP tool include 列表，重启 `hermes-gateway`。

## 飞书里怎么说

旧试卷加工：

```text
把我刚上传的这份四年级英语旧试卷清版，生成教学资产包，学科英语，年级四年级，输出 docx 和 pdf。
```

入库：

```text
把我刚上传的这份四年级英语旧试卷清版，生成教学资产包，并入库到四年级英语题库。
```

创建资料库：

```text
创建一个四年级英语题库，用来沉淀旧试卷、变式题、答案解析和讲评资料。
```

## 安全原则

- 不要把 `.env`、`ragflow-api-key.txt`、SSH 私钥、服务器密码、飞书 AppSecret、模型 API Key 提交到 GitHub。
- GitHub 里只保留 `.env.example`。
- 接手人需要真实密钥时，由项目负责人线下或私聊发送。
