---
name: old-paper-asset-package
description: Use when a teacher asks to turn an old exam paper, scanned PDF, photo, worksheet, or handwritten/marked test into a clean deliverable teaching asset package with cleaned questions, question type recognition, knowledge points, difficulty, suitability, variants, automatic layout, question-bank JSON, DOCX, and PDF output. Trigger on Chinese requests such as 旧试卷清版, 去字迹, 生成题库, 自动排版, 变式题, 难度适配, 教学资源包.
---

# Old Paper Asset Package

Use this skill for “旧试卷 -> 可交付教学资产包” tasks.

## Workflow

1. If the user uploaded a file in Feishu, locate the local server path of the uploaded PDF/image/docx.
2. Call the MCP tool `teacher_paper_asset_package`.
3. Pass:
   - `source_path`: uploaded file path
   - `title`: user supplied title if present
   - `subject`: 学科, for example 英语/语文/数学
   - `grade`: 年级, for example 四年级
   - `dataset_name`: optional RAGFlow library name if the user wants the result入库
   - `ingest_to_ragflow`: true when the user says入库/沉淀题库/放进资料库
4. Return the generated deliverables to the user:
   - `clean_paper.docx`
   - `clean_paper.pdf`
   - `question_bank.json`
   - `analysis.md`
   - `asset_package.zip`

## User-Facing Behavior

Explain that the pipeline performs:

- 去除手写/批改痕迹并清版
- 题型、知识点、答案、解析识别
- 难度与年级适配度判断
- 同知识点变式题生成
- 自动排版成 DOCX 和 PDF
- 结构化沉淀为题库 JSON
- 可选入库到 RAGFlow

If the scan is blurry, continue processing and mark uncertain items instead of stopping.

## Minimal Example

“把我刚上传的这份四年级英语旧试卷清版，生成教学资产包，并入库到四年级英语题库。”

Tool call:

```json
{
  "source_path": "/path/to/uploaded.pdf",
  "title": "四年级英语旧试卷教学资产包",
  "subject": "英语",
  "grade": "四年级",
  "dataset_name": "四年级英语题库",
  "ingest_to_ragflow": true
}
```
