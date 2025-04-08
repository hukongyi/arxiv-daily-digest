import schedule
import time
import smtplib
import os
import shutil
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from datetime import datetime
from arxiv_scraper import ArxivScraper
from summarizer import PaperSummarizer
from parallel_summarizer import ParallelPaperSummarizer, BatchParallelPaperSummarizer
from pdf_downloader import PDFDownloader
from pdf_extractor import PDFExtractor
from config import (
    EMAIL_CONFIG, SCHEDULE_TIME, DEBUG_MODE, DAYS_BACK,
    GEMINI_MODEL, ARXIV_CONFIG, DOWNLOAD_PDFS, FULL_TEXT_ANALYSIS,
    PDF_MAX_PAGES, PDF_BASE_DIR, PDF_DB_FILE, USE_OCR_FALLBACK, ORGANIZE_BY_DATE,
    USE_PARALLEL, USE_BATCH_PARALLEL, MAX_WORKERS, BATCH_SIZE
)


def send_email(summaries, category_info):
    """发送邮件

    Args:
        summaries (list): 论文总结列表
        category_info (dict): 包含category name和description的字典
    """
    msg = MIMEMultipart("alternative")

    sender_name = "arXiv论文助手"
    sender_email = EMAIL_CONFIG["sender_email"]
    receiver_emails = EMAIL_CONFIG["receiver_emails"]

    msg["From"] = formataddr((sender_name, sender_email))

    if isinstance(receiver_emails, list):
        formatted_receivers = [formataddr(("", email)) for email in receiver_emails]
        msg["To"] = ", ".join(formatted_receivers)
    else:
        msg["To"] = formataddr(("", receiver_emails))

    # 修改邮件主题，加入分类信息
    msg["Subject"] = Header(
        f"arXiv {category_info['name']} - {datetime.now().strftime('%Y-%m-%d')}",
        "utf-8"
    )

    # 添加邮件头信息
    msg["X-Priority"] = "3"
    msg["X-MSMail-Priority"] = "Normal"
    msg["Importance"] = "Normal"
    msg["X-Mailer"] = "arXiv Paper Summarizer"
    msg["List-Unsubscribe"] = f"<mailto:{sender_email}?subject=unsubscribe>"

    # 修改HTML内容头部，加入分类描述
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Microsoft YaHei', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
                text-align: center;
                border-left: 5px solid #4285f4;
            }}
            .paper {{
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 15px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }}
            .paper-title {{
                color: #4285f4;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .paper-meta {{
                color: #666;
                font-size: 14px;
                margin-bottom: 10px;
            }}
            .paper-abstract {{
                background-color: #f0f8ff;
                padding: 10px;
                border-radius: 3px;
                margin-bottom: 10px;
            }}
            .paper-summary {{
                background-color: #f9f9f9;
                padding: 10px;
                border-radius: 3px;
                margin-top: 10px;
            }}
            details summary {{
                cursor: pointer;
                font-weight: bold;
            }}
            details p {{
                margin-top: 10px;
                line-height: 1.5;
            }}
            .paper-rating {{
                display: inline-block;
                background-color: #4285f4;
                color: white;
                font-weight: bold;
                padding: 3px 8px;
                border-radius: 12px;
                margin-right: 10px;
                font-size: 14px;
            }}
            .rating-high {{
                background-color: #0f9d58; /* 绿色 */
            }}
            .rating-medium {{
                background-color: #4285f4; /* 蓝色 */
            }}
            .rating-low {{
                background-color: #db4437; /* 红色 */
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #e0e0e0;
                font-size: 12px;
                color: #777;
                text-align: center;
            }}
            a {{
                color: #4285f4;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .divider {{
                border-top: 1px dashed #e0e0e0;
                margin: 15px 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>arXiv {category_info['name']} - {datetime.now().strftime('%Y-%m-%d')}</h2>
            <p>{category_info.get('description', '')}</p>
        </div>
    """

    for paper in summaries:
        summary = paper["summary"].replace("\n", "<br>").replace("  ", "&nbsp;")

        # 根据评分决定样式类名
        rating = paper.get('rating', 50)
        rating_class = "rating-medium"
        if rating >= 90:
            rating_class = "rating-high"
        elif rating <= 60:
            rating_class = "rating-low"

        html_content += f"""
        <div class="paper">
            <div class="paper-title">
                <span class="paper-rating {rating_class}">{rating}/100</span>
                {paper['title']}
            </div>
            <div class="paper-meta">
                <strong>作者：</strong>{', '.join(paper['authors'])}<br>
                <strong>arXiv ID：</strong>{paper['arxiv_id']}<br>
                <strong>发表日期：</strong>{paper['published']}<br>
                <strong>PDF链接：</strong><a href="{paper['pdf_url']}">{paper['pdf_url']}</a>
            </div>
            <div class="paper-abstract">
                <details>
                    <summary>原文摘要</summary>
                    <p>{paper.get('abstract', '无摘要')}</p>
                </details>
            </div>
            <div class="paper-summary">
                <strong>总结：</strong><br>
                {summary}
            </div>
        </div>
        """

    html_content += f"""
        <div class="footer">
            <p>此邮件由arXiv论文自动总结系统发送，使用模型{GEMINI_MODEL}总结，如有问题请联系管理员。</p>
            <p>如需退订，请回复并注明'退订'。</p>
        </div>
    </body>
    </html>
    """

    # html_content += f"""
    #     <div class="footer">
    #         <p>此邮件由arXiv论文自动总结系统发送，使用模型{GEMINI_MODEL}总结，如有问题请联系管理员（<a href="mailto:hukongyi@ihep.ac.cn">hukongyi@ihep.ac.cn</a>）。</p>
    #         <p>如需退订，请发送退订至<a href="mailto:hukongyi@ihep.ac.cn">hukongyi@ihep.ac.cn</a>并注明'退订'。</p>
    #     </div>
    # </body>
    # </html>
    # """

    # 添加纯文本版本（作为备用）
    text_content = "今日论文总结（按评分排序）：\n\n"
    for paper in summaries:
        rating = paper.get('rating', 50)
        text_content += f"评分：{rating}/100\n"
        text_content += f"标题：{paper['title']}\n"
        text_content += f"作者：{', '.join(paper['authors'])}\n"
        text_content += f"arXiv ID：{paper['arxiv_id']}\n"
        text_content += f"发表日期：{paper['published']}\n"
        text_content += f"PDF链接：{paper['pdf_url']}\n"
        text_content += f"\n原文摘要：\n{paper.get('abstract', '无摘要')}\n"
        text_content += f"\n总结：\n{paper['summary']}\n"
        text_content += "\n" + "=" * 50 + "\n\n"

    # 添加免责声明
    text_content += f"\n\n此邮件由arXiv论文自动总结系统发送，使用模型{GEMINI_MODEL}总结，\n如有问题请联系管理员（hukongyi@ihep.ac.cn）。\n"
    text_content += "如需退订，请发送退订至此（hukongyi@ihep.ac.cn）并注明'退订'。\n"

    # 添加HTML和纯文本版本
    msg.attach(MIMEText(text_content, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        # 使用SSL连接
        server = smtplib.SMTP_SSL(
            EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]
        )
        server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])

        # 发送给所有收件人
        if isinstance(receiver_emails, list):
            server.sendmail(sender_email, receiver_emails, msg.as_string())
        else:
            server.send_message(msg)

        server.quit()
        print("邮件发送成功！")
    except Exception as e:
        print(f"邮件发送失败：{str(e)}")
        # 尝试使用备用端口
        try:
            print("尝试使用备用端口发送...")
            server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], 587)
            server.starttls()
            server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])

            # 发送给所有收件人
            if isinstance(receiver_emails, list):
                server.sendmail(sender_email, receiver_emails, msg.as_string())
            else:
                server.send_message(msg)

            server.quit()
            print("使用备用端口发送成功！")
        except Exception as e2:
            print(f"备用端口发送也失败：{str(e2)}")
            print("请检查邮箱配置和授权码是否正确")


def run_task():
    """执行任务"""
    print(f"开始执行任务 - {datetime.now()}")

    # 初始化组件
    scraper = ArxivScraper()

    # 选择要使用的总结器
    if USE_PARALLEL:
        if USE_BATCH_PARALLEL:
            print(f"使用批处理并行总结器，批大小: {BATCH_SIZE}, 最大线程数: {MAX_WORKERS if MAX_WORKERS > 0 else '自动'}")
            summarizer = BatchParallelPaperSummarizer(max_workers=MAX_WORKERS or None, batch_size=BATCH_SIZE)
        else:
            print(f"使用并行总结器，最大线程数: {MAX_WORKERS if MAX_WORKERS > 0 else '自动'}")
            summarizer = ParallelPaperSummarizer(max_workers=MAX_WORKERS or None)
    else:
        print("使用串行总结器")
        summarizer = PaperSummarizer()

    pdf_downloader = None
    pdf_extractor = None

    # 如果启用了PDF下载和分析
    if DOWNLOAD_PDFS:
        pdf_downloader = PDFDownloader(base_dir=PDF_BASE_DIR, db_file=PDF_DB_FILE)
        pdf_extractor = PDFExtractor(ocr_fallback=USE_OCR_FALLBACK, max_pages=PDF_MAX_PAGES)

    try:
        # 为每个搜索主题获取并发送论文
        for search_query in ARXIV_CONFIG["search_queries"]:
            print(f"处理分类: {search_query['name']}")

            # 获取该主题的论文
            papers = scraper.get_papers(search_query, days_back=DAYS_BACK)

            if not papers:
                print(f"{search_query['name']} 今日没有新论文")
                continue

            # 如果启用了PDF下载和分析
            if DOWNLOAD_PDFS and pdf_downloader and pdf_extractor:
                print("开始下载论文PDF...")
                # 下载PDF
                papers = pdf_downloader.download_papers(papers)

                # 提取PDF文本
                print("开始提取PDF文本...")
                papers = pdf_extractor.process_papers(papers)

            # 生成总结
            summaries = summarizer.generate_daily_report(papers)

            # 发送邮件
            send_email(summaries, search_query)
    finally:
        # 在处理不同主题之间添加延时，避免API限制
        time.sleep(5)


def main():
    """主函数"""
    print("启动arXiv论文监控系统...")

    if DEBUG_MODE:
        print("调试模式：立即执行一次任务")
        run_task()
        print("任务执行完成！")
    else:
        print(f"正常模式：将在每天 {SCHEDULE_TIME} 执行任务")
        schedule.every().day.at(SCHEDULE_TIME).do(run_task)

        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    main()
