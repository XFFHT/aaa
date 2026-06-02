# teacher-resource-system 集成说明

原始项目：

```text
https://gitee.com/wh517415640/teacher-resource-system.git
```

本目录提供本地已做的 RAGFlow 集成补丁：

```text
teacher-resource-ragflow-integration.patch
```

## 应用方式

```bash
git clone https://gitee.com/wh517415640/teacher-resource-system.git
cd teacher-resource-system
git apply /path/to/teacher-resource-ragflow-integration.patch
```

如果换行符导致 patch 失败，可以先执行：

```bash
git config core.autocrlf false
git apply --ignore-space-change --ignore-whitespace /path/to/teacher-resource-ragflow-integration.patch
```

## 补丁主要内容

- 后端增加 `RagFlowController`
- 后端增加 `RagFlowService`
- 后端增加 `RagFlowOptions`
- 后端增加 RAGFlow DTO
- Resource metadata 增加 RAGFlow 文档 ID、数据集 ID、切片数量、解析状态、可调用状态
- `Program.cs` 支持 SQLite 开发模式
- `Program.cs` 增加 127.0.0.1 前端 CORS
- 前端增加 `src/api/ragflow.js`
- 资源详情页增加“入库到 RAGFlow / 同步状态 / 查看切片”
- 上下文包页增加整体入库

## 本地 SQLite 开发配置

在 `backend/TeacherResource.Api/appsettings.Development.json` 中配置：

```json
{
  "Database": { "Provider": "Sqlite" },
  "ConnectionStrings": {
    "DefaultConnection": "Data Source=D:\\HermesRAG\\teacher-resource.db"
  },
  "RagFlow": {
    "BaseUrl": "http://127.0.0.1:9380",
    "ApiKey": "replace_with_ragflow_api_key"
  }
}
```

真实 `ApiKey` 不要提交。

## 运行方式

后端：

```bash
cd backend/TeacherResource.Api
dotnet run
```

前端：

```bash
cd frontend/teacher-resource-web
npm install
npm run dev
```

默认前端：

```text
http://localhost:5173
```

默认后端：

```text
http://127.0.0.1:5128/api/health
```
