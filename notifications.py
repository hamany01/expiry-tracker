import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
from datetime import datetime, timedelta
import os
from typing import List, Dict, Any

class NotificationManager:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.setup_providers()
    
    def setup_providers(self):
        """Setup notification providers"""
        self.email_config = self.config.get('email', {})
        self.telegram_config = self.config.get('telegram', {})
        self.whatsapp_config = self.config.get('whatsapp', {})
    
    def send_email(self, to_email: str, subject: str, message: str, html: bool = True):
        """Send email notification"""
        try:
            smtp_server = self.email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = self.email_config.get('smtp_port', 587)
            username = self.email_config.get('username')
            password = self.email_config.get('password')
            
            if not all([username, password]):
                return False
            
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if html:
                msg.attach(MIMEText(message, 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False
    
    def send_telegram(self, chat_id: str, message: str):
        """Send Telegram notification"""
        try:
            bot_token = self.telegram_config.get('bot_token')
            if not bot_token:
                return False
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Telegram sending failed: {e}")
            return False
    
    def send_whatsapp(self, phone: str, message: str):
        """Send WhatsApp notification via WhatsApp Business API"""
        try:
            # This is a placeholder for WhatsApp Business API
            # In real implementation, you'd use Twilio or similar service
            api_key = self.whatsapp_config.get('api_key')
            if not api_key:
                return False
            
            # WhatsApp Business API implementation would go here
            print(f"WhatsApp message to {phone}: {message}")
            return True
        except Exception as e:
            print(f"WhatsApp sending failed: {e}")
            return False
    
    def create_expiry_alert(self, item: Dict[str, Any], days_left: int) -> Dict[str, str]:
        """Create formatted expiry alert"""
        if days_left <= 0:
            urgency = "منتهية"
            emoji = "🔴"
            action = "فوري"
        elif days_left <= 7:
            urgency = "عاجلة"
            emoji = "🟠"
            action = "خلال أسبوع"
        elif days_left <= 30:
            urgency = "قريبة"
            emoji = "🟡"
            action = "خلال شهر"
        else:
            urgency = "مخططة"
            emoji = "🟢"
            action = "مراقبة"
        
        message = f"""
{emoji} <b>تنبيه انتهاء الصلاحية</b>

<b>العنصر:</b> {item['title']}
<b>الفئة:</b> {item['category']}
<b>تاريخ الانتهاء:</b> {item['expiry_date']}
<b>الأيام المتبقية:</b> {days_left} يوم
<b>الأولوية:</b> {urgency}
<b>الإجراء المطلوب:</b> {action}

المصدر: {item['source']}
        """
        
        return {
            'subject': f"تنبيه: {item['title']} - {urgency}",
            'message': message,
            'urgency': urgency
        }
    
    def send_bulk_notifications(self, items: List[Dict[str, Any]], notification_config: Dict[str, Any]):
        """Send bulk notifications for multiple items"""
        results = []
        
        for item in items:
            days_left = int(item['days_remaining'])
            alert = self.create_expiry_alert(item, days_left)
            
            # Send based on configuration
            if notification_config.get('email', {}).get('enabled'):
                email_result = self.send_email(
                    notification_config['email']['to'],
                    alert['subject'],
                    alert['message']
                )
                results.append({'type': 'email', 'success': email_result})
            
            if notification_config.get('telegram', {}).get('enabled'):
                telegram_result = self.send_telegram(
                    notification_config['telegram']['chat_id'],
                    alert['message']
                )
                results.append({'type': 'telegram', 'success': telegram_result})
            
            if notification_config.get('whatsapp', {}).get('enabled'):
                whatsapp_result = self.send_whatsapp(
                    notification_config['whatsapp']['phone'],
                    alert['message']
                )
                results.append({'type': 'whatsapp', 'success': whatsapp_result})
        
        return results
    
    def schedule_daily_notifications(self, tracker, notification_config: Dict[str, Any]):
        """Schedule daily notifications for upcoming expirations"""
        upcoming = tracker.get_upcoming_expirations(30)
        
        if not upcoming.empty:
            urgent_items = upcoming[upcoming['days_remaining'] <= 30]
            
            if not urgent_items.empty:
                return self.send_bulk_notifications(
                    urgent_items.to_dict('records'),
                    notification_config
                )
        
        return []

# Notification templates
class NotificationTemplates:
    @staticmethod
    def weekly_summary(items: List[Dict[str, Any]]) -> str:
        """Create weekly summary notification"""
        total_items = len(items)
        urgent_count = sum(1 for item in items if item['days_remaining'] <= 7)
        warning_count = sum(1 for item in items if 7 < item['days_remaining'] <= 30)
        
        message = f"""
📊 <b>ملخص أسبوعي لتنبيهات الانتهاء</b>

إجمالي العناصر: {total_items}
عناصر عاجلة: {urgent_count}
عناصر تحت المراقبة: {warning_count}

<b>أهم العناصر:</b>
"""
        
        for item in items[:5]:
            days_left = int(item['days_remaining'])
            emoji = "🔴" if days_left <= 7 else "🟡"
            message += f"\n{emoji} {item['title']} - {days_left} يوم"
        
        return message
    
    @staticmethod
    def monthly_report(items: List[Dict[str, Any]]) -> str:
        """Create monthly report"""
        categories = {}
        for item in items:
            cat = item['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        message = f"""
📈 <b>تقرير شهري لتنبيهات الانتهاء</b>

<b>إجمالي العناصر:</b> {len(items)}
<b>التصنيفات:</b>
"""
        
        for cat, count in categories.items():
            message += f"\n• {cat}: {count} عنصر"
        
        return message