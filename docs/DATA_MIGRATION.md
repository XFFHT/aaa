# 数据迁移说明

GitHub 仓库只保存代码和说明，不保存用户资料、题库数据、API Key、数据库。

如果要把原电脑的数据迁移到另一台电脑，需要单独复制下面内容。

## 1. 老师原始资料

目录：

```text
D:\HermesRAG\teacher-files
```

作用：飞书上传入库时额外保存的一份普通文件副本。

迁移方式：直接复制整个目录到新电脑同路径。

## 2. 旧试卷加工输出

目录：

```text
D:\HermesRAG\paper-asset\outputs
```

作用：生成过的 DOCX、PDF、JSON、ZIP。

是否必须迁移：不是必须。新电脑可以重新生成。

## 3. teacher-resource 数据库

文件：

```text
D:\HermesRAG\teacher-resource.db
```

作用：teacher-resource-system 的 SQLite 开发数据库。

迁移方式：停止后端服务后复制到新电脑同路径。

## 4. RAGFlow 数据

RAGFlow 通常跑在 Docker 中，数据可能在：

```text
D:\HermesRAG\ragflow-data
```

或者 Docker volume 中。

迁移方式取决于当时 RAGFlow docker-compose 的 volume 配置：

1. 如果 volume 映射到了 `D:\HermesRAG\ragflow-data`，复制该目录。
2. 如果使用 Docker volume，需要用 Docker 导出/导入 volume。
3. 更稳妥的方式是在新电脑重建 RAGFlow，然后重新把 `teacher-files` 里的资料入库。

## 5. 密钥不要放进迁移包

这些不要打包进 GitHub，也不要放进公开压缩包：

```text
D:\HermesRAG\paper-asset\.env
D:\HermesRAG\ragflow-api-key.txt
SSH 私钥
服务器密码
飞书 AppSecret
模型 API Key
```

交接时由负责人私下发。
