import os
import sys
import sqlite3
from datetime import datetime
from models import ExpiryTracker
from scrapers.sample_scrapers import (
    EmployeeVisaScraper,
    VehicleRegistrationScraper,
    InsurancePolicyScraper,
    ContractScraper
)
from ai_predictor import ExpiryPredictor
from notifications import NotificationManager

def initialize_system():
    """Initialize the complete expiry tracking system"""
    print("🚀 بدء تشغيل نظام تتبع تواريخ الانتهاء...")
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Initialize tracker
    tracker = ExpiryTracker()
    
    # Initialize AI predictor
    predictor = ExpiryPredictor(tracker)
    
    # Initialize notification manager
    notification_config = {
        'email': {
            'enabled': False,  # Configure with your email settings
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': 'your-email@gmail.com',
            'password': 'your-password'
        },
        'telegram': {
            'enabled': False,  # Configure with your bot token
            'bot_token': 'your-bot-token',
            'chat_id': 'your-chat-id'
        },
        'whatsapp': {
            'enabled': False  # Configure with WhatsApp Business API
        }
    }
    
    notifier = NotificationManager(notification_config)
    
    # Run initial data collection
    print("📊 جمع البيانات الأولية...")
    scrapers = [
        EmployeeVisaScraper(),
        VehicleRegistrationScraper(),
        InsurancePolicyScraper(),
        ContractScraper()
    ]
    
    total_items = 0
    for scraper in scrapers:
        items = scraper.scrape()
        for item in items:
            try:
                tracker.add_item(item)
                total_items += 1
            except Exception as e:
                print(f"⚠️ خطأ في إضافة العنصر: {e}")
    
    print(f"✅ تم إضافة {total_items} عنصر بنجاح")
    
    # Train AI model
    print("🤖 تدريب نموذج الذكاء الاصطناعي...")
    predictor.train_model()
    
    # Get initial statistics
    stats = tracker.get_statistics()
    print("\n📈 إحصائيات النظام:")
    print(f"   • إجمالي العناصر: {stats['total_items']}")
    print(f"   • عناصر نشطة: {stats['active_items']}")
    print(f"   • تنتهي قريباً: {stats['expiring_soon']}")
    print(f"   • منتهية: {stats['overdue_items']}")
    
    return tracker, predictor, notifier

def generate_sample_data():
    """Generate additional sample data for testing"""
    tracker = ExpiryTracker()
    
    # Add more diverse sample data
    sample_items = [
        {
            "title": "رخصة القيادة - أحمد محمد",
            "category": "رخص القيادة",
            "expiry_date": "2025-08-25",
            "source": "إدارة المرور",
            "description": "انتهاء رخصة القيادة",
            "priority": "high"
        },
        {
            "title": "شهادة ضريبية - الشركة ABC",
            "category": "الوثائق الضريبية",
            "expiry_date": "2025-09-30",
            "source": "مصلحة الضرائب",
            "description": "تجديد الشهادة الضريبية",
            "priority": "medium"
        },
        {
            "title": "تأمين صحي - عائلة محمد",
            "category": "وثائق التأمين",
            "expiry_date": "2025-10-15",
            "source": "شركة التأمين",
            "description": "تجديد التأمين الصحي",
            "priority": "high"
        },
        {
            "title": "عقد إيجار المكتب",
            "category": "العقود",
            "expiry_date": "2025-12-31",
            "source": "المكتب العقاري",
            "description": "تجديد عقد الإيجار",
            "priority": "medium"
        }
    ]
    
    for item in sample_items:
        try:
            tracker.add_item(item)
        except:
            pass
    
    print("✅ تم إضافة بيانات اختبار إضافية")

if __name__ == "__main__":
    # Initialize system
    tracker, predictor, notifier = initialize_system()
    
    # Generate sample data
    generate_sample_data()
    
    print("\n🎉 النظام جاهز للاستخدام!")
    print("\nلتشغيل لوحة التحكم:")
    print("   streamlit run dashboard.py")
    print("\nأو للوصول المباشر:")
    print("   python -m http.server 8000")
    print("   ثم افتح المتصفح على: http://localhost:8000")