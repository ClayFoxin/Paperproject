"""Prompt templates for LLM calls."""
from __future__ import annotations

from typing import Dict, List


INFO_EXTRACTION_TEMPLATE = """
你是科研论文信息抽取助手。请阅读以下正文，提取并用简洁中文总结：
- 材料体系
- 工艺/制备方法
- 性能指标
- 创新点

请以 JSON 输出，对缺失信息填 null。
正文：
{content}
"""


def build_info_prompt(content: str) -> List[dict]:
    return [
        {"role": "system", "content": "你是精通材料科学的中文信息抽取助手。"},
        {"role": "user", "content": INFO_EXTRACTION_TEMPLATE.format(content=content)},
    ]


def build_data_prompt(content: str, fields: Dict[str, str]) -> List[dict]:
    field_lines = [f"- {name}: {desc}" for name, desc in fields.items()]
    template = """
请根据以下字段描述，从正文中抽取结构化数据。每个字段需要给出值和来源句子，无法确定请填 null。
字段：
{field_lines}

正文：
{content}
""".format(field_lines="\n".join(field_lines), content=content)

    return [
        {"role": "system", "content": "你是善于提取数据的助手，输出 JSON"},
        {"role": "user", "content": template},
    ]


def build_cleaning_prompt(raw_xml: str) -> List[dict]:
    """Ask the LLM to strip metadata/noise from XML content and return clean text."""
    user_prompt = """
请阅读以下期刊文章的 XML 原文，去掉标题、作者、期刊、参考文献等元信息，只保留正文的自然段落与表格/图像说明。请用 JSON 返回：
- text: 清洗后的正文纯文本
- tables: 如能识别，请列表说明表格要点；无法确定用空列表
- figures: 如能识别，请列表说明图像/示意内容；无法确定用空列表

XML 原文：
{content}
""".format(content=raw_xml[:6000])

    return [
        {"role": "system", "content": "你是文献预处理助手，专注从 XML 中提取正文。"},
        {"role": "user", "content": user_prompt},
    ]
