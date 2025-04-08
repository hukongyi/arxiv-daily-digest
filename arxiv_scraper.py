import arxiv
from datetime import datetime, timedelta
from config import ARXIV_CONFIG
import pytz


class ArxivScraper:
    def __init__(self):
        self.client = arxiv.Client()
        self.config = ARXIV_CONFIG

    def get_papers(self, search_query, days_back=1):
        """获取最近几天的论文
        
        Args:
            search_query (dict): 包含query和name的字典
            days_back (int): 获取几天前的论文
        """
        utc = pytz.UTC
        end_date = datetime.now(utc)
        start_date = (end_date - timedelta(days=days_back)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        
        print(f"Searching papers for {search_query['name']} from {start_date} to {end_date}")
        
        search = arxiv.Search(
            query=search_query['query'],
            max_results=self.config["max_results"],
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        papers = []
        count = 0
        for result in self.client.results(search):
            paper_date = result.published
            if not paper_date.tzinfo:
                paper_date = utc.localize(paper_date)
            print(paper_date)
            if start_date <= paper_date <= end_date:
                count += 1
                print(f"Found paper_{count} for {search_query['name']}: {result.title}")
                papers.append({
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "abstract": result.summary,
                    "pdf_url": result.pdf_url,
                    "published": paper_date.strftime("%Y-%m-%d"),
                    "arxiv_id": result.entry_id.split("/")[-1],
                    "category": search_query['name'],
                    "category_description": search_query.get('description', '')
                })
            else:
                break

        return papers
