import os
import json
import requests
import shutil
from pathlib import Path
import time
from datetime import datetime
from urllib.parse import urlparse
from config import PDF_BASE_DIR, PDF_DB_FILE, ORGANIZE_BY_DATE


class PDFDownloader:
    def __init__(self, base_dir=PDF_BASE_DIR, db_file=PDF_DB_FILE):
        """
        初始化PDF下载器

        Args:
            base_dir: PDF文件保存的基础目录
            db_file: 存储PDF文件位置的数据库文件
        """
        self.base_dir = Path(base_dir)
        self.db_file = Path(db_file)

        # 确保基础目录存在
        os.makedirs(self.base_dir, exist_ok=True)

        # 确保数据库文件所在目录存在
        os.makedirs(self.db_file.parent, exist_ok=True)

        # 加载PDF数据库
        self.pdf_db = self._load_pdf_database()

        print(f"PDF文件将保存到: {self.base_dir}")

    def _load_pdf_database(self):
        """加载PDF数据库"""
        if self.db_file.exists():
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载PDF数据库失败: {str(e)}")
                return {}
        return {}

    def _save_pdf_database(self):
        """保存PDF数据库"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.pdf_db, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存PDF数据库失败: {str(e)}")

    def _get_date_folder(self, date_str=None):
        """获取日期文件夹路径"""
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')

        if ORGANIZE_BY_DATE:
            # 按年/月/日组织
            date_parts = date_str.split('-')
            if len(date_parts) >= 3:
                year, month, day = date_parts[0], date_parts[1], date_parts[2]
                folder = self.base_dir / year / month / day
            else:
                # 如果日期格式不正确，直接使用完整日期作为文件夹名
                folder = self.base_dir / date_str
        else:
            # 不按日期组织，直接使用基础目录
            folder = self.base_dir

        # 确保文件夹存在
        os.makedirs(folder, exist_ok=True)
        return folder

    def download_pdf(self, pdf_url, arxiv_id=None, published_date=None, max_retries=3):
        """
        下载PDF文件

        Args:
            pdf_url: PDF的URL
            arxiv_id: arXiv ID，用于命名文件
            published_date: 发布日期，用于组织文件夹
            max_retries: 最大重试次数

        Returns:
            下载的PDF文件路径，如果下载失败则返回None
        """
        if not arxiv_id:
            # 从URL中提取文件名
            parsed_url = urlparse(pdf_url)
            filename = os.path.basename(parsed_url.path)
            if not filename.endswith('.pdf'):
                filename += '.pdf'
        else:
            filename = f"{arxiv_id}.pdf"

        # 检查数据库中是否已有该论文
        if arxiv_id in self.pdf_db:
            existing_path = Path(self.pdf_db[arxiv_id])
            if existing_path.exists():
                print(f"数据库中已有该论文: {existing_path}")
                return str(existing_path)

        # 获取保存文件夹
        save_folder = self._get_date_folder(published_date)
        file_path = save_folder / filename

        # 如果文件已存在，直接返回路径
        if file_path.exists():
            print(f"文件已存在: {file_path}")
            # 更新数据库
            self.pdf_db[arxiv_id] = str(file_path)
            self._save_pdf_database()
            return str(file_path)

        # 下载文件
        for attempt in range(max_retries):
            try:
                print(f"正在下载: {pdf_url} -> {file_path}")
                response = requests.get(pdf_url, stream=True, timeout=30)
                response.raise_for_status()

                with open(file_path, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)

                print(f"下载成功: {file_path}")

                # 更新数据库
                self.pdf_db[arxiv_id] = str(file_path)
                self._save_pdf_database()

                return str(file_path)

            except Exception as e:
                print(f"下载失败 (尝试 {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    # 指数退避
                    time.sleep(2 ** attempt)
                else:
                    print(f"达到最大重试次数，放弃下载: {pdf_url}")
                    return None

    def download_papers(self, papers):
        """
        批量下载论文

        Args:
            papers: 论文列表，每个论文应包含pdf_url、arxiv_id和published

        Returns:
            更新后的论文列表，每个论文增加pdf_path字段
        """
        for paper in papers:
            published_date = paper.get('published')
            pdf_path = self.download_pdf(
                paper['pdf_url'],
                paper['arxiv_id'],
                published_date
            )
            paper['pdf_path'] = pdf_path

        return papers

    def get_paper_path(self, arxiv_id):
        """
        获取论文的本地路径

        Args:
            arxiv_id: arXiv ID

        Returns:
            论文的本地路径，如果不存在则返回None
        """
        if arxiv_id in self.pdf_db:
            path = Path(self.pdf_db[arxiv_id])
            if path.exists():
                return str(path)
        return None
