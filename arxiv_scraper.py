import arxiv
from datetime import datetime, timedelta
from config import ARXIV_CONFIG
import pytz


class ArxivScraper:
    def __init__(self):
        self.client = arxiv.Client()
        self.config = ARXIV_CONFIG

    def get_papers(self, days_back=1):
        """获取最近几天的论文"""
        # 计算日期范围，使用UTC时区
        utc = pytz.UTC
        end_date = datetime.now(utc)
        # 将start_date设置为指定天数的0点
        start_date = (end_date - timedelta(days=days_back)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        print(start_date)
        print(end_date)
        # 构建搜索查询
        search = arxiv.Search(
            query=self.config["search_query"],
            max_results=self.config["max_results"],
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        papers = []
        count = 0
        for result in self.client.results(search):
            # 确保paper_date是UTC时区
            paper_date = result.published
            if not paper_date.tzinfo:
                paper_date = utc.localize(paper_date)

            if start_date <= paper_date <= end_date:
                count += 1
                print(f"Found paper_{count}: {result.title}")
                papers.append(
                    {
                        "title": result.title,
                        "authors": [author.name for author in result.authors],
                        "abstract": result.summary,
                        "pdf_url": result.pdf_url,
                        "published": paper_date.strftime("%Y-%m-%d"),
                        "arxiv_id": result.entry_id.split("/")[-1],
                    }
                )
            else:
                break

        return papers
