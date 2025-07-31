# models.py (الكود الكامل والنهائي)
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Any
import json

class ExpiryTracker:
    def __init__(self, db_path: str = "data/expiry_tracker.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create expiry items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expiry_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                expiry_date DATE NOT NULL,
                source TEXT NOT NULL,
                source_url TEXT,
                description TEXT,
                status TEXT DEFAULT 'active',
                priority TEXT DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                days_before_alert INTEGER DEFAULT 30
            )
        ''')
        
        # Create alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                alert_type TEXT,
                alert_date DATE,
                sent BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES expiry_items (id)
            )
        ''')
        
        # Create sources table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                config TEXT,
                last_sync TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_all_items(self) -> pd.DataFrame:
        """Get all items from the database and calculate remaining days."""
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM expiry_items WHERE status = 'active' ORDER BY expiry_date ASC"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            # Calculate days_remaining for all items
            df['expiry_date'] = pd.to_datetime(df['expiry_date'])
            df['days_remaining'] = (df['expiry_date'] - datetime.now()).dt.days
        
        return df

    def add_item(self, item_data: Dict[str, Any]) -> int:
        """Add a new expiry item"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO expiry_items 
            (title, category, expiry_date, source, source_url, description, 
             priority, status, metadata, days_before_alert)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item_data['title'],
            item_data['category'],
            item_data['expiry_date'],
            item_data['source'],
            item_data.get('source_url', ''),
            item_data.get('description', ''),
            item_data.get('priority', 'medium'),
            item_data.get('status', 'active'),
            json.dumps(item_data.get('metadata', {})),
            item_data.get('days_before_alert', 30)
        ))
        
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return item_id

    def update_item(self, item_id: int, item_data: Dict[str, Any]):
        """Update an existing item's data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE expiry_items SET
                title = ?,
                category = ?,
                expiry_date = ?,
                source = ?,
                description = ?,
                priority = ?,
                status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            item_data['title'],
            item_data['category'],
            item_data['expiry_date'],
            item_data['source'],
            item_data['description'],
            item_data['priority'],
            item_data['status'],
            item_id
        ))
        
        conn.commit()
        conn.close()

    def delete_item(self, item_id: int):
        """Delete an item from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expiry_items WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
    
    def get_upcoming_expirations(self, days: int = 30) -> pd.DataFrame:
        """Get items expiring within specified days"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT *, 
                   julianday(expiry_date) - julianday('now') as days_remaining
            FROM expiry_items 
            WHERE expiry_date <= date('now', '+' || ? || ' days')
            AND status = 'active'
            ORDER BY expiry_date ASC
        '''
        
        df = pd.read_sql_query(query, conn, params=[days])
        conn.close()
        
        return df
    
    def get_overdue_items(self) -> pd.DataFrame:
        """Get items that have already expired"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT *, 
                   julianday('now') - julianday(expiry_date) as days_overdue
            FROM expiry_items 
            WHERE expiry_date < date('now')
            AND status = 'active'
            ORDER BY expiry_date DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def update_item_status(self, item_id: int, status: str):
        """Update item status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE expiry_items 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, item_id))
        
        conn.commit()
        conn.close()
    
    def get_items_by_category(self, category: str) -> pd.DataFrame:
        """Get items by category"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT * FROM expiry_items 
            WHERE category = ? AND status = 'active'
            ORDER BY expiry_date ASC
        '''
        
        df = pd.read_sql_query(query, conn, params=[category])
        conn.close()
        
        return df
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total items
        cursor.execute("SELECT COUNT(*) FROM expiry_items")
        stats['total_items'] = cursor.fetchone()[0]
        
        # Active items
        cursor.execute("SELECT COUNT(*) FROM expiry_items WHERE status = 'active'")
        stats['active_items'] = cursor.fetchone()[0]
        
        # Expiring soon (next 7 days)
        cursor.execute("""
            SELECT COUNT(*) FROM expiry_items 
            WHERE expiry_date <= date('now', '+7 days') 
            AND expiry_date >= date('now')
            AND status = 'active'
        """)
        stats['expiring_soon'] = cursor.fetchone()[0]
        
        # Overdue items
        cursor.execute("""
            SELECT COUNT(*) FROM expiry_items 
            WHERE expiry_date < date('now') 
            AND status = 'active'
        """)
        stats['overdue_items'] = cursor.fetchone()[0]
        
        # Items by category
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM expiry_items 
            WHERE status = 'active'
            GROUP BY category
        """)
        stats['by_category'] = dict(cursor.fetchall())
        
        conn.close()
        
        return stats
