# Hermes / RAGFlow 对接说明

本项目已经补上 TeacherResource -> RAGFlow -> Hermes 的第一版链路。

## 本地后台

TeacherResource 后端读取：

- `RagFlow:BaseUrl`，默认 `http://127.0.0.1:9380`
- `RagFlow:ApiKeyFile`，默认 `D:\HermesRAG\ragflow-api-key.txt`
- `RagFlow:TeacherFilesRoot`，默认 `D:\HermesRAG\teacher-files`

资源详情页可以对单个文件执行：

1. 入库 RAGFlow
2. 同步 RAGFlow 解析状态
3. 查看 RAGFlow 切片

上下文包页可以把一组资源整体入库到同一个 RAGFlow 资料库。

## 后端接口

- `GET /api/ragflow/status`
- `GET /api/ragflow/datasets`
- `POST /api/ragflow/datasets`
- `POST /api/ragflow/resources/{resourceId}/files/{fileId}/ingest`
- `POST /api/ragflow/resources/{resourceId}/sync`
- `GET /api/ragflow/resources/{resourceId}/chunks`
- `POST /api/ragflow/context-packs/{contextPackId}/ingest`
- `POST /api/ragflow/retrieve`

## Hermes 访问方式

本机脚本 `D:\HermesRAG\scripts\start-ragflow-tunnel.ps1` 已增加：

```text
127.0.0.1:15128 on server -> 127.0.0.1:5128 on this PC
```

所以 Hermes 服务器上的 MCP 使用：

```text
TEACHER_RESOURCE_API_URL=http://127.0.0.1:15128/api
```

可用 MCP 工具：

- `teacher_resource_status`
- `teacher_resource_list_resources`
- `teacher_resource_ingest_file`
- `teacher_resource_sync_resource`
- `teacher_resource_chunks`
- `teacher_resource_ingest_context_pack`

## 使用顺序

1. 启动 RAGFlow：`D:\HermesRAG\scripts\start-ragflow.ps1`
2. 启动反向隧道：`D:\HermesRAG\scripts\start-ragflow-tunnel.ps1`
3. 启动 TeacherResource 后端：`dotnet run`，监听 `http://127.0.0.1:5128`
4. 启动前端：`npm run dev`
5. 在资源详情页上传文件，点击“入库 RAGFlow”
6. 等待解析后点击“同步 RAGFlow 状态”或“查看切片”

