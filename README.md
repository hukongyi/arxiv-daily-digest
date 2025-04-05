# arXiv 论文自动总结系统

这是一个自动获取和总结 arXiv 论文的 Python 项目。系统会每天自动获取指定主题的最新论文，使用 Google Gemini AI 生成总结，并通过邮件发送给您。

## 功能特点

- 自动获取 arXiv 最新论文
- 使用 Google Gemini AI 生成论文总结
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
- `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, ...：Gemini API 密钥，支持多个密钥轮换使用
- `GEMINI_MODEL`：使用的 Gemini 模型名称
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
- `summarizer.py`：论文总结生成模块，使用 Gemini AI
- `config.py`：项目配置文件
- `.env`：环境变量配置文件（包含敏感信息）
- `requirements.txt`：项目依赖列表

## 注意事项

- 确保 Gemini API 密钥有效
- 邮件服务器需要开启 SMTP 服务
- 建议使用虚拟环境运行项目
- 如果使用 QQ 邮箱，需要使用授权码而非登录密码
- 请勿将包含敏感信息的 `.env` 文件提交到版本控制系统

## 许可证

MIT License 