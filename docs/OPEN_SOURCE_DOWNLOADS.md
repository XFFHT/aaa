# 开源/外部组件下载清单

这些组件不是本仓库自带的，需要接手人在新电脑或服务器上下载/安装。

| 组件 | 用途 | 下载地址 |
| --- | --- | --- |
| RAGFlow | 老师资料库/题库/知识库，负责文件解析、切分、检索 | https://github.com/infiniflow/ragflow |
| Docker Desktop for Windows | 运行 RAGFlow 的 Docker 服务 | https://docs.docker.com/desktop/setup/install/windows-install/ |
| Git for Windows | 克隆 GitHub/Gitee 仓库、应用 patch | https://git-scm.com/download/win |
| Python 3.10+ | 运行旧试卷 worker、脚本、MCP 本地验证 | https://www.python.org/downloads/windows/ |
| Node.js LTS | 运行 teacher-resource-system 前端 | https://nodejs.org/en/download |
| .NET 9 SDK | 运行 teacher-resource-system 后端 | https://dotnet.microsoft.com/en-us/download/dotnet/9.0 |
| teacher-resource-system | 老师资源管理 Web 系统原项目 | https://gitee.com/wh517415640/teacher-resource-system.git |

## Python 包

本仓库已提供：

```text
src/paper-asset/requirements.txt
```

安装：

```powershell
pip install -r D:\HermesRAG\paper-asset\requirements.txt
```

包含：

```text
fastapi
uvicorn
python-multipart
requests
Pillow
PyMuPDF
python-docx
reportlab
python-pptx
```

## RAGFlow 安装提示

推荐目录：

```powershell
cd D:\HermesRAG
git clone https://github.com/infiniflow/ragflow.git ragflow
cd D:\HermesRAG\ragflow\docker
docker compose up -d
```

实际启动命令以 RAGFlow 官方 GitHub README 为准。

## teacher-resource-system 安装提示

```powershell
cd D:\HermesRAG
git clone https://gitee.com/wh517415640/teacher-resource-system.git teacher-resource-system
cd D:\HermesRAG\teacher-resource-system
git apply D:\handoff\aaa\integrations\teacher-resource-system\teacher-resource-ragflow-integration.patch
```

后端：

```powershell
cd D:\HermesRAG\teacher-resource-system\backend\TeacherResource.Api
dotnet run
```

前端：

```powershell
cd D:\HermesRAG\teacher-resource-system\frontend\teacher-resource-web
npm install
npm run dev
```
