from google import genai
from google.genai import types
from config import GEMINI_API_KEYS, GEMINI_MODEL, FULL_TEXT_ANALYSIS
import re
import threading
import queue
import time
import concurrent.futures
from typing import List, Dict, Any, Optional


class ParallelPaperSummarizer:
    """使用多线程并行处理论文总结的类"""

    def __init__(self, max_workers=None):
        """
        初始化并行论文总结器

        Args:
            max_workers: 最大工作线程数，默认为None（使用所有可用的API密钥）
        """
        # 初始化API客户端
        self.api_clients = self._initialize_clients()

        # 设置最大工作线程数
        self.max_workers = max_workers or len(self.api_clients)
        if self.max_workers > len(self.api_clients):
            self.max_workers = len(self.api_clients)

        print(f"初始化并行论文总结器，使用 {self.max_workers} 个工作线程")

    def _initialize_clients(self):
        """初始化所有API客户端"""
        clients = []
        for api_key in GEMINI_API_KEYS:
            try:
                client = genai.Client(api_key=api_key)
                # 测试客户端是否有效
                clients.append(client)
                print(f"成功初始化API客户端: {api_key}")
            except Exception as e:
                print(f"初始化API客户端失败: {api_key} - {str(e)}")

        if not clients:
            raise ValueError("没有可用的API客户端，请检查API密钥")

        return clients

    def _summarize_paper_with_client(self, paper: Dict[str, Any], client_index: int) -> Dict[str, Any]:
        """
        使用指定的客户端总结论文

        Args:
            paper: 论文数据
            client_index: 客户端索引

        Returns:
            包含总结文本和评分的字典
        """
        client = self.api_clients[client_index]

        # 使用f-string更安全地处理可能包含特殊字符的内容
        title = paper.get("title", "N/A")
        authors = ", ".join(paper.get("authors", ["N/A"]))
        abstract = paper.get("abstract", "N/A")

        # 检查是否有全文可用
        has_full_text = 'full_text' in paper and paper['full_text'] and len(paper['full_text']) > 200

        # 根据配置和全文可用性决定使用哪种提示
        if FULL_TEXT_ANALYSIS and has_full_text:
            # 提取全文
            full_text = paper['full_text']

            prompt = f"""
请扮演一位专业的科研助理。
你的任务是根据下面提供的论文信息（标题、作者、摘要、全文），用简洁、专业的中文进行总结和评分。

**输入信息:**
标题：{title}
作者：{authors}
摘要：{abstract}
全文：{full_text}

**输出要求:**
第一部分：请严格按照以下结构和编号进行总结，确保内容准确、精炼：

1.  主要研究目标: (总结论文试图解决的核心问题或达成的具体目标)
2.  关键方法: (总结论文采用的主要研究方法、技术路径或实验设计)
3.  主要创新点: (总结论文相比现有研究的新颖之处或独特贡献)
4.  主要结论: (总结论文得出的最重要研究结果、发现或核心观点)
5.  研究意义: (总结该研究的理论价值、潜在应用前景或对相关领域的贡献)

第二部分：请对论文进行评分（1-100分），并简要说明理由：

6.  论文评分: (1-100分，100分为最高，50分以上为合格，80分以上为优秀)
7.  评分理由: (简要说明评分理由，包括创新性、方法学严谨性、结果可靠性和影响力等方面)

**格式与约束:**
*   语言：简体中文。
*   篇幅：每个部分的内容**严格限制在200字以内**。
*   格式：**仅输出**编号和对应内容（例如："1. 主要研究目标: [内容]"），每个部分占一行。**绝对不要包含任何**引言、结语、问候语、解释性文字或任何与要求格式无关的内容。直接开始输出 "1. 主要研究目标: ..."。
"""
        else:
            # 使用原来的只基于摘要的提示
            prompt = f"""
请扮演一位专业的科研助理。
你的任务是根据下面提供的论文信息（标题、作者、摘要），用简洁、专业的中文进行总结和评分。

**输入信息:**
标题：{title}
作者：{authors}
摘要：{abstract}

**输出要求:**
第一部分：请严格按照以下结构和编号进行总结，确保内容准确、精炼：

1.  主要研究目标: (总结论文试图解决的核心问题或达成的具体目标)
2.  关键方法: (总结论文采用的主要研究方法、技术路径或实验设计)
3.  主要创新点: (总结论文相比现有研究的新颖之处或独特贡献)
4.  主要结论: (总结论文得出的最重要研究结果、发现或核心观点)
5.  研究意义: (总结该研究的理论价值、潜在应用前景或对相关领域的贡献)

第二部分：请对论文进行评分（1-100分），并简要说明理由：

6.  论文评分: (1-100分，100分为最高，50分以上为合格，80分以上为优秀)
7.  评分理由: (简要说明评分理由，包括创新性、方法学严谨性、结果可靠性和影响力等方面)

**格式与约束:**
*   语言：简体中文。
*   篇幅：每个部分的内容**严格限制在200字以内**。
*   格式：**仅输出**编号和对应内容（例如："1. 主要研究目标: [内容]"），每个部分占一行。**绝对不要包含任何**引言、结语、问候语、解释性文字或任何与要求格式无关的内容。直接开始输出 "1. 主要研究目标: ..."。
"""

        max_retries = 3
        for attempt in range(max_retries):
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
                for chunk in client.models.generate_content_stream(
                    model=GEMINI_MODEL,
                    contents=contents,
                    config=generate_content_config,
                ):
                    response += chunk.text

                # 如果响应为空，重试
                if not response.strip():
                    if attempt < max_retries - 1:
                        print(f"API响应为空，重试 ({attempt+1}/{max_retries})...")
                        time.sleep(60)
                        continue
                    else:
                        return {"summary_text": "API响应为空，请稍后重试。", "rating": 50}

                # 提取评分
                rating = self._extract_rating(response)

                print(f"线程 {client_index} 成功总结论文: {title[:30]}...")
                return {
                    "summary_text": response,
                    "rating": rating
                }

            except Exception as e:
                print(f"线程 {client_index} 总结失败: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"重试 ({attempt+1}/{max_retries})...")
                    time.sleep(60)
                else:
                    return {
                        "summary_text": f"总结失败: {str(e)}",
                        "rating": 50
                    }

    def _extract_rating(self, summary_text: str) -> int:
        """从总结文本中提取评分"""
        try:
            # 使用正则表达式查找评分行
            rating_match = re.search(r'6\.\s*论文评分:\s*(\d+)', summary_text)
            if rating_match:
                rating = int(rating_match.group(1))
                # 确保评分在1-100范围内
                rating = max(1, min(100, rating))
                return rating
            return 50  # 如果无法提取评分，返回默认值
        except Exception as e:
            print(f"提取评分失败: {str(e)}")
            return 50  # 出错时返回默认值

    def generate_daily_report(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        并行生成每日报告

        Args:
            papers: 论文列表

        Returns:
            包含总结和评分的论文列表
        """
        if not papers:
            return []

        print(f"开始并行处理 {len(papers)} 篇论文，使用 {self.max_workers} 个线程...")

        # 使用线程池并行处理
        summaries = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 创建任务
            future_to_paper = {}
            for i, paper in enumerate(papers):
                client_index = i % len(self.api_clients)
                future = executor.submit(self._summarize_paper_with_client, paper, client_index)
                future_to_paper[future] = paper

            # 收集结果
            for future in concurrent.futures.as_completed(future_to_paper):
                paper = future_to_paper[future]
                try:
                    summary_result = future.result()

                    # 提取摘要文本和评分
                    summary_text = summary_result.get("summary_text", "")
                    rating = summary_result.get("rating", 50)

                    summaries.append({
                        "title": paper["title"],
                        "authors": paper["authors"],
                        "arxiv_id": paper["arxiv_id"],
                        "pdf_url": paper["pdf_url"],
                        "published": paper.get("published", "N/A"),
                        "abstract": paper.get("abstract", ""),
                        "summary": summary_text,
                        "rating": rating,
                        "pdf_path": paper.get("pdf_path", None),
                    })
                except Exception as e:
                    print(f"处理论文失败: {str(e)}")
                    # 添加一个失败的条目
                    summaries.append({
                        "title": paper["title"],
                        "authors": paper["authors"],
                        "arxiv_id": paper["arxiv_id"],
                        "pdf_url": paper["pdf_url"],
                        "published": paper.get("published", "N/A"),
                        "abstract": paper.get("abstract", ""),
                        "summary": f"总结失败: {str(e)}",
                        "rating": 50,
                        "pdf_path": paper.get("pdf_path", None),
                    })

        # 按评分排序（从高到低）
        summaries.sort(key=lambda x: x.get("rating", 0), reverse=True)

        print(f"并行处理完成，共处理 {len(summaries)} 篇论文")
        return summaries


# 批处理版本，可以处理大量论文
class BatchParallelPaperSummarizer(ParallelPaperSummarizer):
    """使用批处理和多线程并行处理大量论文总结的类"""

    def __init__(self, max_workers=None, batch_size=10):
        """
        初始化批处理并行论文总结器

        Args:
            max_workers: 最大工作线程数，默认为None（使用所有可用的API密钥）
            batch_size: 每批处理的论文数量
        """
        super().__init__(max_workers)
        self.batch_size = batch_size
        print(f"初始化批处理并行论文总结器，批大小: {batch_size}")

    def generate_daily_report(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        分批并行生成每日报告

        Args:
            papers: 论文列表

        Returns:
            包含总结和评分的论文列表
        """
        if not papers:
            return []

        total_papers = len(papers)
        print(f"开始分批并行处理 {total_papers} 篇论文，批大小: {self.batch_size}...")

        all_summaries = []

        # 分批处理
        for i in range(0, total_papers, self.batch_size):
            batch = papers[i:i+self.batch_size]
            print(f"处理批次 {i//self.batch_size + 1}/{(total_papers+self.batch_size-1)//self.batch_size}，包含 {len(batch)} 篇论文")

            # 使用父类的方法处理当前批次
            batch_summaries = super().generate_daily_report(batch)
            all_summaries.extend(batch_summaries)

            # 在批次之间添加延时，避免API限制
            if i + self.batch_size < total_papers:
                print("批次处理完成，等待60秒后处理下一批...")
                time.sleep(60)

        # 按评分排序（从高到低）
        all_summaries.sort(key=lambda x: x.get("rating", 0), reverse=True)

        print(f"所有批次处理完成，共处理 {len(all_summaries)} 篇论文")
        return all_summaries
