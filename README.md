# arXiv 论文自动总结系统

这是一个自动获取和总结 arXiv 论文的 Python 项目。系统会每天自动获取指定主题的最新论文，使用 Google Gemini AI 生成总结，并通过邮件发送给您。

## 功能特点

- 自动获取 arXiv 最新论文
- 自动下载论文PDF并提取全文内容
- 使用 Google Gemini AI 生成论文总结
- 对论文进行评分（1-10分）并按评分排序
- 支持多个 API 密钥轮换使用
- 每日定时发送邮件报告
- 可配置的论文主题和关键词
- 支持自定义运行时间
- 美观的 HTML 邮件格式
- 支持多个收件人

## 安装要求

- Python 3.8+
- 依赖包：见 requirements.txt

## 安装步骤

1. 克隆项目到本地
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 配置项目：
   - 创建 `.env` 文件并配置以下环境变量：
     ```
     # 调试模式配置
     DEBUG_MODE=False
     DAYS_BACK=2

     # PDF处理配置
     DOWNLOAD_PDFS=True
     FULL_TEXT_ANALYSIS=True
     PDF_MAX_PAGES=20
     # PDF保存目录和数据库文件
     PDF_BASE_DIR=./papers
     # PDF_DB_FILE=./papers/pdf_database.json
     # 是否按日期组织文件夹（年/月/日）
     ORGANIZE_BY_DATE=True
     # 是否在PDF提取失败时使用OCR
     USE_OCR_FALLBACK=False

     # Gemini API配置
     GEMINI_API_KEY_1=你的Gemini API密钥1
     GEMINI_API_KEY_2=你的Gemini API密钥2
     GEMINI_MODEL=gemini-2.0-flash-thinking-exp-01-21

     # 邮件配置
     SMTP_SERVER=smtp.qq.com
     SMTP_PORT=465
     SENDER_EMAIL=你的发件人邮箱
     SENDER_PASSWORD=你的邮箱授权码
     RECEIVER_EMAILS=收件人1@example.com,收件人2@example.com

     # 运行时间配置
     SCHEDULE_TIME=09:00
     ```
   - 或者直接在 `config.py` 文件中修改配置（不推荐，敏感信息应放在.env文件中）

## 配置说明

在 `.env` 文件中可以修改以下配置：

- `DEBUG_MODE`：调试模式，设置为 True 时程序会立即执行一次任务
- `DAYS_BACK`：获取最近几天的论文

**PDF处理配置：**
- `DOWNLOAD_PDFS`：是否下载PDF文件（默认为True）
- `FULL_TEXT_ANALYSIS`：是否使用全文分析（默认为True）
- `PDF_MAX_PAGES`：处理PDF的最大页数（默认为20）
- `PDF_BASE_DIR`：PDF文件保存的基础目录（默认为./papers）
- `PDF_DB_FILE`：存储PDF文件位置的数据库文件（默认为./papers/pdf_database.json）
- `ORGANIZE_BY_DATE`：是否按日期组织文件夹（默认为True）
- `USE_OCR_FALLBACK`：当PDF文本提取失败时是否使用OCR（默认为False）

**Gemini API配置：**
- `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, ...：Gemini API 密钥，支持多个密钥轮换使用
- `GEMINI_MODEL`：使用的 Gemini 模型名称

**邮件配置：**
- `SMTP_SERVER`：邮件服务器地址
- `SMTP_PORT`：邮件服务器端口
- `SENDER_EMAIL`：发件人邮箱
- `SENDER_PASSWORD`：发件人邮箱授权码
- `RECEIVER_EMAILS`：收件人邮箱列表，多个邮箱用逗号分隔
- `SCHEDULE_TIME`：每日运行时间（默认为 "09:00"）

在 `config.py` 文件中可以修改以下非敏感配置：

- `ARXIV_CONFIG`：arXiv 搜索配置
  - `search_query`：搜索关键词（默认为 "astro-ph.HE"）
  - `max_results`：每次获取的论文数量
  - `sort_by`：排序方式
  - `sort_order`：排序顺序

## 使用方法

1. 配置项目（创建 `.env` 文件）
2. 运行程序：
   ```bash
   python main.py
   ```

## 项目结构

- `main.py`：主程序入口，包含邮件发送和定时任务功能
- `arxiv_scraper.py`：arXiv 论文获取模块
- `pdf_downloader.py`：PDF下载模块
- `pdf_extractor.py`：PDF文本提取模块
- `summarizer.py`：论文总结生成和评分模块，使用 Gemini AI
- `config.py`：项目配置文件
- `.env`：环境变量配置文件（包含敏感信息）
- `.env.example`：环境变量配置示例文件
- `requirements.txt`：项目依赖列表

## 注意事项

- 确保 Gemini API 密钥有效
- 邮件服务器需要开启 SMTP 服务
- 建议使用虚拟环境运行项目
- 如果使用 QQ 邮箱，需要使用授权码而非登录密码
- 请勿将包含敏感信息的 `.env` 文件提交到版本控制系统

## 许可证

MIT License