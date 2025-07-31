import os

# هيكل المجلدات المطلوب
folders = [
    "data",
    "scrapers"
]

# ملفات رئيسية (سيتم إنشاؤها فارغة إذا لم تكن موجودة)
root_files = [
    "main.py",
    "models.py",
    "ai_predictor.py",
    "notifications.py",
    "simple_dashboard.py",
    "requirements.txt",
    "dashboard.html",
    "README.md"
]

# ملفات داخل scrapers
scrapers_files = [
    "scrapers/sample_scrapers.py"
]

# ملفات داخل data (سيتولد تلقائياً من التشغيل الفعلي، لكن ننشئها كملفات فارغة)
data_files = [
    "data/expiry_tracker.db",
    "data/expiry_predictor.pkl"
]

def touch(filepath):
    if not os.path.exists(filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            pass

# أنشئ المجلدات
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# أنشئ الملفات الرئيسية
for filepath in root_files:
    touch(filepath)

# أنشئ ملفات scrapers
for filepath in scrapers_files:
    touch(filepath)

# أنشئ ملفات data (فارغة فقط للترتيب، سيتم استبدالها لاحقاً)
for filepath in data_files:
    touch(filepath)

print("✅ تم ترتيب هيكل المشروع بنجاح!")
