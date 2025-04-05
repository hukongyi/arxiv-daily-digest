from google import genai
from google.genai import types
from config import GEMINI_API_KEYS, GEMINI_MODEL
import itertools


class PaperSummarizer:
    def __init__(self):
        # 创建API key轮换器
        self.api_key_cycle = itertools.cycle(GEMINI_API_KEYS)
        self.current_client = None
        self._update_client()

    def _update_client(self):
        """更新当前使用的API key"""
        api_key = next(self.api_key_cycle)
        self.current_client = genai.Client(api_key=api_key)

    def summarize_paper(self, paper):
        """使用Gemini API总结论文（优化版）"""

        # 使用f-string更安全地处理可能包含特殊字符的内容
        title = paper.get("title", "N/A")
        authors = ", ".join(paper.get("authors", ["N/A"]))
        abstract = paper.get("abstract", "N/A")

        prompt = f"""
    请扮演一位专业的科研助理。
    你的任务是根据下面提供的论文信息（标题、作者、摘要），用简洁、专业的中文进行总结。请注意，总结应**完全基于**提供的摘要内容。

    **输入信息:**
    标题：{title}
    作者：{authors}
    摘要：{abstract}

    **输出要求:**
    请严格按照以下结构和编号进行回答，确保内容准确、精炼：

    1.  主要研究目标: (总结论文试图解决的核心问题或达成的具体目标)
    2.  关键方法: (总结论文采用的主要研究方法、技术路径或实验设计)
    3.  主要创新点: (总结论文相比现有研究的新颖之处或独特贡献)
    4.  主要结论: (总结论文得出的最重要研究结果、发现或核心观点)
    5.  研究意义: (总结该研究的理论价值、潜在应用前景或对相关领域的贡献)

    **格式与约束:**
    *   语言：简体中文。
    *   篇幅：每个部分的内容**严格限制在100字以内**。
    *   格式：**仅输出**编号和对应内容（例如："1. 主要研究目标: [内容]"），每个部分占一行。**绝对不要包含任何**引言、结语、问候语、解释性文字或任何与要求格式无关的内容。直接开始输出 "1. 主要研究目标: ..."。
    """

        try:
            # 准备请求内容
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                ),
            ]

            # 设置生成配置
            generate_content_config = types.GenerateContentConfig(
                response_mime_type="text/plain",
            )

            # 生成响应
            response = ""
            for chunk in self.current_client.models.generate_content_stream(
                model=GEMINI_MODEL,
                contents=contents,
                config=generate_content_config,
            ):
                response += chunk.text

            # 如果响应为空，尝试使用另一个API key
            if not response.strip():
                self._update_client()
                return self.summarize_paper(paper)
            print(response)
            return response

        except Exception as e:
            print(f"使用当前API key失败: {str(e)}")
            # 如果出错，尝试使用另一个API key
            self._update_client()
            return self.summarize_paper(paper)

    def generate_daily_report(self, papers):
        """生成每日报告"""
        summaries = []
        for paper in papers:
            summary = self.summarize_paper(paper)
            summaries.append(
                {
                    "title": paper["title"],
                    "authors": paper["authors"],
                    "arxiv_id": paper["arxiv_id"],
                    "pdf_url": paper["pdf_url"],
                    "published": paper.get("published", "N/A"),
                    "summary": summary,
                }
            )
        return summaries
