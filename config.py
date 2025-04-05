import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 调试模式配置
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
DAYS_BACK = int(os.getenv("DAYS_BACK", "2"))

# arXiv 配置
ARXIV_CONFIG = {
    "search_query": "astro-ph.HE",  # 默认搜索AI相关论文
    "max_results": 100,  # 每次获取的论文数量
    "sort_by": "submittedDate",
    "sort_order": "descending",
}

# Gemini API配置
GEMINI_API_KEYS = []
# 从环境变量中读取API密钥
for i in range(1, 10):  # 支持最多9个API密钥
    api_key = os.getenv(f"GEMINI_API_KEY_{i}")
    if api_key:
        GEMINI_API_KEYS.append(api_key)
    else:
        break


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
