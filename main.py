import schedule
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from datetime import datetime
from arxiv_scraper import ArxivScraper
from summarizer import PaperSummarizer
from config import EMAIL_CONFIG, SCHEDULE_TIME, DEBUG_MODE, DAYS_BACK, GEMINI_MODEL


def send_email(summaries):
    """发送邮件"""
    msg = MIMEMultipart("alternative")

    # 使用formataddr正确格式化发件人和收件人
    sender_name = "arXiv论文助手"
    sender_email = EMAIL_CONFIG["sender_email"]
    receiver_emails = EMAIL_CONFIG["receiver_emails"]

    msg["From"] = formataddr((sender_name, sender_email))

    # 处理多个收件人
    if isinstance(receiver_emails, list):
        # 将多个收件人格式化为字符串
        formatted_receivers = []
        for email in receiver_emails:
            formatted_receivers.append(formataddr(("", email)))
        msg["To"] = ", ".join(formatted_receivers)
    else:
        # 兼容单个收件人的情况
        msg["To"] = formataddr(("", receiver_emails))

    msg["Subject"] = Header(
        f"arXiv论文日报 - {datetime.now().strftime('%Y-%m-%d')}", "utf-8"
    )

    # 添加邮件头信息
    msg["X-Priority"] = "3"
    msg["X-MSMail-Priority"] = "Normal"
    msg["Importance"] = "Normal"
    msg["X-Mailer"] = "arXiv Paper Summarizer"
    msg["List-Unsubscribe"] = f"<mailto:{sender_email}?subject=unsubscribe>"

    # 构建HTML邮件内容
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
            .paper-summary {{
                background-color: #f9f9f9;
                padding: 10px;
                border-radius: 3px;
                margin-top: 10px;
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
            <h2>arXiv论文日报 - {datetime.now().strftime('%Y-%m-%d')}</h2>
        </div>
    """

    for paper in summaries:
        summary = paper["summary"].replace("\n", "<br>")
        html_content += f"""
        <div class="paper">
            <div class="paper-title">{paper['title']}</div>
            <div class="paper-meta">
                <strong>作者：</strong>{', '.join(paper['authors'])}<br>
                <strong>arXiv ID：</strong>{paper['arxiv_id']}<br>
                <strong>发表日期：</strong>{paper['published']}<br>
                <strong>PDF链接：</strong><a href="{paper['pdf_url']}">{paper['pdf_url']}</a>
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
    text_content = "今日论文总结：\n\n"
    for paper in summaries:
        text_content += f"标题：{paper['title']}\n"
        text_content += f"作者：{', '.join(paper['authors'])}\n"
        text_content += f"arXiv ID：{paper['arxiv_id']}\n"
        text_content += f"发表日期：{paper['published']}\n"
        text_content += f"PDF链接：{paper['pdf_url']}\n"
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

    # 获取论文
    scraper = ArxivScraper()
    papers = scraper.get_papers(days_back=DAYS_BACK)

    if not papers:
        print("今日没有新论文")
        return

    # 生成总结
    summarizer = PaperSummarizer()
    summaries = summarizer.generate_daily_report(papers)

    # 发送邮件
    send_email(summaries)


def main():
    """主函数"""
    print("启动arXiv论文监控系统...")

    if DEBUG_MODE:
        print("调试模式：立即执行一次任务")
        run_task()
        print("任务执行完成！")
    else:
        print(f"正常模式：将在每天 {SCHEDULE_TIME} 执行任务")
        # 设置定时任务
        schedule.every().day.at(SCHEDULE_TIME).do(run_task)

        # 运行定时任务
        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    main()
