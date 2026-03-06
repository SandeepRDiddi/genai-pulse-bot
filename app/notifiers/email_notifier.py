"""
Email notifier — sends HTML digest emails via SMTP.
Works with Gmail, SendGrid, Mailgun, AWS SES, etc.
"""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict
from datetime import datetime

from app.config import settings
from app.database import AsyncSessionLocal, Subscriber
from sqlalchemy import select

logger = logging.getLogger(__name__)


async def send_email_digest(articles: List[Dict]) -> int:
    """Send HTML digest to all email subscribers. Returns count sent."""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("Email not configured — skipping")
        return 0

    # Get all active email subscribers
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Subscriber).where(
                Subscriber.is_active == True,
                Subscriber.email.isnot(None)
            )
        )
        subscribers = result.scalars().all()

    if not subscribers:
        logger.info("No email subscribers found")
        return 0

    html_body = _build_html_email(articles)
    sent_count = 0

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

            for subscriber in subscribers:
                try:
                    msg = MIMEMultipart("alternative")
                    msg["Subject"] = f"🤖 GenAI Pulse — {datetime.utcnow().strftime('%B %d, %Y')}"
                    msg["From"] = settings.EMAIL_FROM
                    msg["To"] = subscriber.email
                    msg.attach(MIMEText(html_body, "html"))
                    smtp.sendmail(settings.SMTP_USER, subscriber.email, msg.as_string())
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send to {subscriber.email}: {e}")

    except Exception as e:
        logger.error(f"SMTP connection failed: {e}")

    logger.info(f"✅ Email digest sent to {sent_count} subscribers")
    return sent_count


def _build_html_email(articles: List[Dict]) -> str:
    """Build a clean HTML email digest."""
    source_groups = {}
    for a in articles:
        source_groups.setdefault(a["source"], []).append(a)

    sections_html = ""
    source_config = {
        "arxiv": ("📄", "Arxiv Papers", "#667eea"),
        "huggingface": ("🤗", "HuggingFace", "#f6a623"),
        "reddit": ("💬", "Reddit Trending", "#ff4500"),
        "technews": ("📰", "Tech News", "#00b4d8"),
    }

    for source, (emoji, name, color) in source_config.items():
        items = source_groups.get(source, [])[:4]
        if not items:
            continue

        items_html = "".join([
            f"""
            <div style="margin-bottom:16px;padding:12px;background:#f8f9fa;border-radius:8px;border-left:4px solid {color}">
                <a href="{a['url']}" style="font-weight:600;color:#1a1a2e;text-decoration:none;font-size:14px;">{a['title'][:100]}</a>
                <p style="color:#666;font-size:13px;margin:6px 0 0;">{a.get('summary','')[:200]}...</p>
            </div>
            """ for a in items
        ])

        sections_html += f"""
        <div style="margin-bottom:32px;">
            <h2 style="color:{color};font-size:18px;border-bottom:2px solid {color};padding-bottom:8px;">
                {emoji} {name}
            </h2>
            {items_html}
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:640px;margin:0 auto;padding:24px;color:#1a1a2e;">
        <div style="text-align:center;margin-bottom:32px;">
            <h1 style="font-size:28px;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                🤖 GenAI Pulse
            </h1>
            <p style="color:#666;">{datetime.utcnow().strftime('%A, %B %d, %Y')} · Daily Digest</p>
        </div>
        {sections_html}
        <div style="text-align:center;padding:24px;color:#999;font-size:12px;border-top:1px solid #eee;margin-top:32px;">
            <p>GenAI Pulse Bot — Open Source AI News Tracker</p>
            <p><a href="https://github.com/SandeepRDiddi/genai-pulse-bot" style="color:#667eea;">GitHub</a></p>
        </div>
    </body>
    </html>
    """
