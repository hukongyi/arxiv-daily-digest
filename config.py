import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(".env", override=True)

# 调试模式配置
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
DAYS_BACK = int(os.getenv("DAYS_BACK", "2"))

# PDF处理配置
DOWNLOAD_PDFS = os.getenv("DOWNLOAD_PDFS", "True").lower() == "true"
FULL_TEXT_ANALYSIS = os.getenv("FULL_TEXT_ANALYSIS", "True").lower() == "true"
PDF_MAX_PAGES = int(os.getenv("PDF_MAX_PAGES", "20"))  # 处理PDF的最大页数
PDF_BASE_DIR = os.getenv("PDF_BASE_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "papers"))  # PDF保存的基础目录
PDF_DB_FILE = os.getenv("PDF_DB_FILE", os.path.join(PDF_BASE_DIR, "pdf_database.json"))  # 存储PDF文件位置的数据库文件
ORGANIZE_BY_DATE = os.getenv("ORGANIZE_BY_DATE", "True").lower() == "true"  # 是否按日期组织文件夹
USE_OCR_FALLBACK = os.getenv("USE_OCR_FALLBACK", "False").lower() == "true"  # 是否在PDF提取失败时使用OCR

# arXiv 配置
ARXIV_CONFIG = {
    "search_queries": [
        {
            # "query": "cat:cs.AI OR cat:cs.CL OR cat:cs.HC OR cat:cs.CV OR cat:cs.LG OR cat:cs.NE OR cat:cs.IR OR cat:cs.CY OR cat:cs.DC OR cs.SE OR cs.RO",  # 计算机科学
            "query": "cat:cs.AI OR cat:cs.CL cat:cs.LG",  # 计算机科学
            "name": "计算机科学",
        },
        # {
        #     "query": "cat:astro-ph.HE",  # 高能天体物理
        #     "name": "高能天体物理论文",
        # },
    ],  # 可配置多个搜索主题
    "max_results": 1000,  # 每次获取的论文数量
    "sort_by": "submittedDate",
    "sort_order": "descending",
}

# Gemini API配置
GEMINI_API_KEYS = []
# 从环境变量中读取API密钥
for i in range(1, 101):  # 支持最多100个API密钥
    api_key = os.getenv(f"GEMINI_API_KEY_{i}")
    if api_key:
        GEMINI_API_KEYS.append(api_key)
    else:
        break

# 并行处理配置
USE_PARALLEL = os.getenv("USE_PARALLEL", "True").lower() == "true"  # 是否使用并行处理
USE_BATCH_PARALLEL = os.getenv("USE_BATCH_PARALLEL", "True").lower() == "true"  # 是否使用批处理
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "0"))  # 最大工作线程数，0表示使用所有可用的API密钥
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))  # 每批处理的论文数量

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-thinking-exp-01-21")

# OpenAI配置
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 邮件配置
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# 处理多个收件人
RECEIVER_EMAILS_STR = os.getenv("RECEIVER_EMAILS")
RECEIVER_EMAILS = RECEIVER_EMAILS_STR.split(",")

EMAIL_CONFIG = {
    "smtp_server": SMTP_SERVER,
    "smtp_port": SMTP_PORT,
    "sender_email": SENDER_EMAIL,
    "sender_password": SENDER_PASSWORD,
    "receiver_emails": RECEIVER_EMAILS,
}

# EMAIL_CONFIG = {
#     "smtp_server": os.getenv('SMTP_SERVER'),
#     "smtp_port": int(os.getenv('SMTP_PORT', '587')),
#     "sender_email": os.getenv('SENDER_EMAIL'),
#     "sender_password": os.getenv('SENDER_PASSWORD'),
#     "receiver_email": os.getenv('RECEIVER_EMAIL'),
# }

# 运行时间配置
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "09:00")  # 每天早上9点运行

proxy_url = "http://127.0.0.1:7890"
# proxy_url = "http://username:password@your_proxy_server_address:proxy_port" # With auth
os.environ['HTTPS_PROXY'] = proxy_url
os.environ['HTTP_PROXY'] = proxy_url
