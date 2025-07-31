import sqlite3
import json
from datetime import datetime, timedelta
import os

class SimpleDashboard:
    def __init__(self):
        self.db_path = "data/expiry_tracker.db"
    
    def get_dashboard_data(self):
        """Get all dashboard data"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Get all items
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM expiry_items 
            WHERE status = 'active' 
            ORDER BY expiry_date ASC
        """)
        
        items = cursor.fetchall()
        
        # Get statistics
        today = datetime.now().date()
        thirty_days = today + timedelta(days=30)
        
        stats = {
            'total': len(items),
            'expiring_soon': 0,
            'overdue': 0,
            'safe': 0
        }
        
        processed_items = []
        for item in items:
            item_dict = dict(item)
            expiry_date = datetime.strptime(item_dict['expiry_date'], '%Y-%m-%d').date()
            days_left = (expiry_date - today).days
            
            item_dict['days_left'] = days_left
            
            if days_left < 0:
                stats['overdue'] += 1
                item_dict['status_class'] = 'overdue'
            elif days_left <= 30:
                stats['expiring_soon'] += 1
                item_dict['status_class'] = 'expiring'
            else:
                stats['safe'] += 1
                item_dict['status_class'] = 'safe'
            
            processed_items.append(item_dict)
        
        conn.close()
        return processed_items, stats
    
    def generate_html_dashboard(self):
        """Generate HTML dashboard"""
        items, stats = self.get_dashboard_data()
        
        html = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام تتبع تواريخ الانتهاء</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .stat-label {
            color: #666;
            font-size: 1.2em;
        }
        
        .total { color: #667eea; }
        .expiring { color: #ff9800; }
        .overdue { color: #f44336; }
        .safe { color: #4caf50; }
        
        .items-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .item-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border-left: 5px solid;
        }
        
        .item-card.expiring {
            border-left-color: #ff9800;
        }
        
        .item-card.overdue {
            border-left-color: #f44336;
        }
        
        .item-card.safe {
            border-left-color: #4caf50;
        }
        
        .item-title {
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }
        
        .item-details {
            color: #666;
            margin-bottom: 15px;
        }
        
        .item-date {
            font-size: 1.1em;
            font-weight: bold;
        }
        
        .days-left {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .days-left.expiring {
            background: #fff3e0;
            color: #ff9800;
        }
        
        .days-left.overdue {
            background: #ffebee;
            color: #f44336;
        }
        
        .days-left.safe {
            background: #e8f5e8;
            color: #4caf50;
        }
        
        .filter-section {
            background: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .filter-buttons {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .filter-btn {
            padding: 10px 20px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 1em;
        }
        
        .filter-btn.active {
            background: #667eea;
            color: white;
        }
        
        .filter-btn:hover {
            transform: scale(1.05);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📅 نظام تتبع تواريخ الانتهاء</h1>
            <p>مراقبة وإدارة جميع تواريخ الانتهاء في مكان واحد</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number total">''' + str(stats['total']) + '''</div>
                <div class="stat-label">إجمالي العناصر</div>
            </div>
            <div class="stat-card">
                <div class="stat-number expiring">''' + str(stats['expiring_soon']) + '''</div>
                <div class="stat-label">تنتهي قريباً</div>
            </div>
            <div class="stat-card">
                <div class="stat-number overdue">''' + str(stats['overdue']) + '''</div>
                <div class="stat-label">منتهية</div>
            </div>
            <div class="stat-card">
                <div class="stat-number safe">''' + str(stats['safe']) + '''</div>
                <div class="stat-label">آمنة</div>
            </div>
        </div>
        
        <div class="filter-section">
            <h3>تصفية النتائج</h3>
            <div class="filter-buttons">
                <button class="filter-btn active" onclick="filterItems('all')">الكل</button>
                <button class="filter-btn" onclick="filterItems('expiring')">تنتهي قريباً</button>
                <button class="filter-btn" onclick="filterItems('overdue')">منتهية</button>
                <button class="filter-btn" onclick="filterItems('safe')">آمنة</button>
            </div>
        </div>
        
        <div class="items-grid" id="itemsGrid">
        '''
        
        for item in items:
            html += f'''
            <div class="item-card {item['status_class']}" data-status="{item['status_class']}">
                <div class="item-title">{item['title']}</div>
                <div class="item-details">
                    <strong>التصنيف:</strong> {item['category']}<br>
                    <strong>المصدر:</strong> {item['source']}<br>
                    <strong>الوصف:</strong> {item['description']}
                </div>
                <div class="item-date">
                    تاريخ الانتهاء: {item['expiry_date']}
                </div>
                <div class="days-left {item['status_class']}">
                    {abs(item['days_left'])} يوم {'متبقي' if item['days_left'] > 0 else 'منذ الانتهاء'}
                </div>
            </div>
            '''
        
        html += '''
        </div>
    </div>
    
    <script>
        function filterItems(status) {
            const items = document.querySelectorAll('.item-card');
            const buttons = document.querySelectorAll('.filter-btn');
            
            // Update active button
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Filter items
            items.forEach(item => {
                if (status === 'all' || item.dataset.status === status) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
        '''
        
        return html
    
    def save_dashboard(self):
        """Save dashboard to file"""
        html = self.generate_html_dashboard()
        with open('dashboard.html', 'w', encoding='utf-8') as f:
            f.write(html)
        return 'dashboard.html'

# Create and save dashboard
if __name__ == "__main__":
    dashboard = SimpleDashboard()
    filename = dashboard.save_dashboard()
    print(f"✅ تم إنشاء لوحة التحكم: {filename}")