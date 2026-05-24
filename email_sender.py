import smtplib
import json
import os
import html
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime

from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()


def _clean_text(text: str) -> str:
    """Strip HTML tags and normalize whitespace from RSS content."""
    if not text:
        return ''
    plain = BeautifulSoup(text, 'html.parser').get_text(separator=' ', strip=True)
    return re.sub(r'\s+', ' ', plain)


def _escape(value: str) -> str:
    return html.escape(value or '', quote=True)


class NewsEmailSender:
    def __init__(self):
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = os.getenv('SMTP_PORT', '587')
        self.smtp_port = int(smtp_port) if smtp_port else 587

    @property
    def recipients(self) -> list[str]:
        if not self.recipient_email:
            return []
        return [email.strip() for email in self.recipient_email.split(',') if email.strip()]

    def validate_config(self) -> bool:
        """Validate email configuration"""
        if not all([self.sender_email, self.sender_password, self.recipients]):
            print("❌ Missing required email configuration")
            print(f"SENDER_EMAIL: {self.sender_email}")
            print(f"RECIPIENT_EMAIL: {self.recipient_email or 'NOT SET'}")
            print(f"SENDER_PASSWORD: {'***' if self.sender_password else 'NOT SET'}")
            return False
        return True

    def load_news(self, filename: str = 'daily_news.json') -> dict:
        """Load news from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ News file not found: {filename}")
            return {'count': 0, 'news': []}
        except json.JSONDecodeError as e:
            print(f"❌ Invalid news file: {e}")
            return {'count': 0, 'news': []}

    def generate_html_email(self, news_data: dict) -> str:
        """Generate HTML email content"""
        today = datetime.now().strftime('%Y年%m月%d日')
        news_count = news_data.get('count', 0)
        news_list = news_data.get('news', [])

        html_content = f"""
        <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: 'Segoe UI', 'Microsoft YaHei', Arial, sans-serif;
                        color: #333;
                        line-height: 1.6;
                        margin: 0;
                        padding: 0;
                        background-color: #f5f5f5;
                    }}
                    .container {{
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #ffffff;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #76b900 0%, #1db942 100%);
                        color: white;
                        padding: 30px;
                        border-radius: 8px 8px 0 0;
                        margin: -20px -20px 30px -20px;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                        font-weight: bold;
                    }}
                    .header p {{
                        margin: 10px 0 0 0;
                        font-size: 14px;
                        opacity: 0.9;
                    }}
                    .stats {{
                        background: #f0f0f0;
                        padding: 15px;
                        border-radius: 4px;
                        margin-bottom: 20px;
                        text-align: center;
                    }}
                    .stats p {{
                        margin: 0;
                        font-size: 16px;
                        color: #1db942;
                        font-weight: bold;
                    }}
                    .news-item {{
                        background: #f9f9f9;
                        border-left: 4px solid #76b900;
                        padding: 15px;
                        margin-bottom: 15px;
                        border-radius: 4px;
                    }}
                    .news-item h3 {{
                        margin: 0 0 10px 0;
                        color: #1db942;
                        font-size: 16px;
                        line-height: 1.4;
                    }}
                    .news-item p {{
                        margin: 0 0 10px 0;
                        color: #666;
                        font-size: 14px;
                        line-height: 1.6;
                    }}
                    .news-item .source {{
                        color: #999;
                        font-size: 12px;
                    }}
                    .news-item a {{
                        color: #1db942;
                        text-decoration: none;
                        word-break: break-all;
                    }}
                    .news-item a:hover {{
                        text-decoration: underline;
                    }}
                    .footer {{
                        text-align: center;
                        color: #999;
                        font-size: 12px;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #eee;
                    }}
                    .divider {{
                        height: 1px;
                        background-color: #eee;
                        margin: 15px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📰 NVIDIA AI服务器供应链日报</h1>
                        <p>每日精选新闻汇总 · {_escape(today)}</p>
                    </div>

                    <div class="stats">
                        <p>今日共收集 <strong>{news_count}</strong> 条相关新闻</p>
                    </div>
        """

        for idx, news in enumerate(news_list, 1):
            title = _escape(_clean_text(news.get('title', '未知标题')))
            description = _escape(_clean_text(news.get('description', '')))
            url = _escape(news.get('url', '#'))
            source = _escape(_clean_text(news.get('source', {}).get('name', '未知来源')))

            html_content += f"""
                    <div class="news-item">
                        <h3>{idx}. {title}</h3>
                        <p>{description}</p>
                        <div class="divider"></div>
                        <p style="margin: 0;">
                            <a href="{url}" target="_blank">📖 阅读全文 →</a>
                            <span class="source" style="margin-left: 20px;">来源: {source}</span>
                        </p>
                    </div>
            """

        html_content += """
                    <div class="footer">
                        <p>这是一份自动生成的日报，由GitHub Actions每日定时发送。</p>
                        <p>如有任何问题，请访问仓库进行反馈。</p>
                        <p style="margin: 10px 0 0 0; opacity: 0.7;">Daily NVIDIA AI Server Supply Chain News Digest</p>
                    </div>
                </div>
            </body>
        </html>
        """

        return html_content

    def send_email(self, subject: str, html_content: str):
        """Send email with HTML content"""
        if not self.validate_config():
            raise ValueError("Email configuration is incomplete")

        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = Header(subject, 'utf-8')
            message["From"] = self.sender_email
            message["To"] = ", ".join(self.recipients)

            part = MIMEText(html_content, "html", "utf-8")
            message.attach(part)

            print(f"Connecting to {self.smtp_server}:{self.smtp_port}...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipients, message.as_string())

            print(f"✅ Email sent successfully to {', '.join(self.recipients)}")

        except Exception as e:
            print(f"❌ Error sending email: {e}")
            raise


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Send NVIDIA supply chain news digest email')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Generate HTML preview only, do not send email',
    )
    parser.add_argument(
        '--preview',
        default='email_preview.html',
        help='Output file for --dry-run (default: email_preview.html)',
    )
    parser.add_argument(
        '--check-config',
        action='store_true',
        help='Validate email configuration only',
    )
    args = parser.parse_args()

    sender = NewsEmailSender()

    if args.check_config:
        raise SystemExit(0 if sender.validate_config() else 1)

    news_data = sender.load_news()
    news_count = news_data.get('count', 0)

    if news_count <= 0:
        print("⚠️ No news found to send")
        raise SystemExit(1)

    today = datetime.now().strftime('%Y年%m月%d日')
    subject = f"📰 NVIDIA AI服务器供应链日报 - {today}"
    html_content = sender.generate_html_email(news_data)

    if args.dry_run:
        with open(args.preview, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Dry run complete")
        print(f"   News count: {news_count}")
        print(f"   Subject: {subject}")
        print(f"   Preview: {os.path.abspath(args.preview)}")
        raise SystemExit(0)

    sender.send_email(subject, html_content)
    print("✅ Daily digest email sent!")
