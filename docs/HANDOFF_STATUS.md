# 交接状态

更新时间：2026-06-02

## 已验证通过

本地旧试卷 worker：

- `/health` 正常
- 文本样例真实调用模型 API 成功
- 已生成 `clean_paper.docx`
- 已生成 `clean_paper.pdf`
- 已生成 `question_bank.json`
- 已生成 `analysis.md`
- 已生成 `asset_package.zip`

服务器侧 Hermes MCP：

- `teacher_ragflow_mcp.py` 语法检查通过
- 服务器能通过反向隧道访问本机 `http://127.0.0.1:18766/health`
- `teacher_paper_asset_package` 从服务器侧调用成功
- 生成结果成功下载到服务器 `/opt/hermes-ragflow/outputs/paper-assets/<job_id>/`

反向隧道：

- `18080 -> 8080`
- `19380 -> 9380`
- `19382 -> 9382`
- `18765 -> 18765`
- `18766 -> 18766`
- `15128 -> 5128`

Hermes：

- `hermes-gateway` 重启后 active
- `teacher_paper_asset_package` 已加入 MCP tool include 列表

## 待接手人继续做

1. 完成“组新卷”输出：
   - 从结构化题目中读取 `selected_for_new_paper`
   - 输出 `new_paper.docx`
   - 输出 `new_paper.pdf`
2. 完成“讲题 PPT”输出：
   - 每道好题生成讲题页
   - 每道好题生成相似题/变式题页
   - 输出 `lesson_ppt.pptx`
3. 调整 worker 返回文件列表：
   - 增加 `new_paper_docx`
   - 增加 `new_paper_pdf`
   - 增加 `lesson_ppt`
4. 调整 MCP 下载文件列表：
   - 把新卷和 PPT 一起下载到服务器
5. 调整 skill 文案：
   - 明确用户说“组新卷/上课 PPT/相似题”时调用 `teacher_paper_asset_package`
6. 根据老师真实科目改进 prompt：
   - 英语：听力、词汇、语法、阅读理解、作文
   - 数学：计算、应用题、几何、易错点
   - 语文：字词、阅读、古诗文、作文

## 当前可对用户承诺的结果

可以承诺：

- 旧试卷清版
- 题型/知识点/答案/解析识别
- 难度和适配度判断
- 变式题生成
- DOCX/PDF 输出
- 题库 JSON 输出
- 可选沉淀入 RAGFlow

不要承诺已经完整上线：

- 自动挑好题后重组一张新卷
- 同步生成讲题 PPT
- PPT 里按每道好题生成相似题

这些是下一步继续开发项。
