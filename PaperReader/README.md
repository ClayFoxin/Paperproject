# PaperReader

PaperReader 是一个用于从科学文献中完成“下载/解析 → 清洗 → LLM 信息抽取 → 结构化导出”的可扩展 Python 框架骨架。它为未来接入 Elsevier、Uni-parser 以及任意 LLM 提供清晰的目录结构与可插拔组件。

## 功能概览

1. **原始数据获取**：从 `data/input/doi.xlsx` 读取 DOI，预留 Elsevier API 下载 XML 以及本地 PDF 上传/解析接口（`ingestion/`）。
2. **文献解析**：通过 `uniparser_adapter` 接入 Uni-parser，将 XML/PDF 解析为 JSON。
3. **清洗**：使用 `cleaning/strip_metadata.py` 去掉题目、作者、参考文献等元信息，只保留正文、表格与图像解析内容。
4. **LLM 抽取**：`llm/` 目录提供统一的 LLM 客户端、提示词生成器与信息/数据抽取模块，支持自定义提示模板与字段自动生成提示。
5. **结果落盘**：`io/json_store.py` 写入中间 JSON，`io/xlsx_writer.py` 输出结构化数据表。

## 目录结构
```
PaperReader/
├─ pyproject.toml
├─ README.md
├─ requirements.txt
├─ .env.example
├─ data/
│  ├─ input/
│  │  ├─ doi.xlsx
│  │  └─ pdfs/
│  └─ output/
│     ├─ parsed_json/
│     ├─ cleaned_json/
│     ├─ info_json/
│     └─ extracted_xlsx/
├─ src/
│  └─ paperreader/
│     ├─ cli.py
│     ├─ config.py
│     ├─ pipeline/
│     │  └─ run.py
│     ├─ io/
│     ├─ ingestion/
│     ├─ cleaning/
│     ├─ llm/
│     └─ utils/
└─ tests/
```

## 快速开始

1. 创建虚拟环境并安装依赖：
```bash
cd PaperReader
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2. 配置环境变量：复制 `.env.example` 为 `.env`，填写 `OPENAI_API_KEY`（或其他模型的 key/endpoint）。如需使用 DeepSeek，设置 `OPENAI_BASE_URL=https://api.deepseek.com` 并在 `OPENAI_MODEL` 中填写 `deepseek-chat` 或 `deepseek-coder`。
3. 准备输入：
   - 将 DOI 列表放入 `data/input/doi.xlsx`（示例表头：`doi`）。
   - 可选：将 PDF 放入 `data/input/pdfs/`。
4. 运行：
```bash
paperreader run
```

## 设计原则

- **模块化**：下载、解析、清洗、抽取、导出各阶段彼此解耦，易于替换实现。
- **可观测性**：`utils/log.py` 提供统一日志格式，便于日后扩展链路追踪。
- **易测试**：`tests/test_strip_metadata.py` 演示了对清洗逻辑的单元测试。
- **LLM 可插拔**：`llm/client.py` 通过简单的接口包装 OpenAI SDK，未来可兼容多种模型或自建服务。

## 现状与扩展点

- Elsevier API 与 Uni-parser 部分以占位实现为主，方便根据实际 API/二进制配置替换。
- 提示词与 schema 在 `llm/prompts.py` 和 `llm/schemas.py` 中集中管理，支持自动构造字段级提示。
- 如需解析图像、表格或引用，请在 `strip_metadata.py` 与 `llm/data_extract.py` 中扩展字段规则。

## Web 前端（FastAPI + Jinja2）

你可以通过简单的网页端来上传 DOI/PDF、配置 API Key 并启动全流程：

```bash
uvicorn paperreader.web.server:app --reload --port 8000
```

打开浏览器访问 <http://localhost:8000>，完成：

- 上传 `doi.xlsx`（存入 `data/input/doi.xlsx`）
- 多文件上传 PDF（存入 `data/input/pdfs/`）
- 表单内覆盖 OpenAI / Elsevier Key（留空则使用 `.env`）
- 一键触发“下载→解析→清洗→LLM 抽取→XLSX 导出”流水线
- 直接在页面下载解析/清洗 JSON、信息抽取 JSON，以及最新的 XLSX 导出

