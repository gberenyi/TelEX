"""
Database Handler - Manages local SQLite database
Stores position history and trade data
"""
import sqlite3
from typing import List, Dict, Any

class DatabaseHandler:
    def __init__(self, db_path: str = 'positions.db'):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id TEXT PRIMARY KEY,
                exchange TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                amount REAL NOT NULL,
                entry_price REAL,
                current_price REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def add_position(self, position: Dict[str, Any]):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO positions (id, exchange, symbol, side, amount, entry_price, current_price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            position['id'],
            position['exchange'],
            position['symbol'],
            position['side'],
            position['amount'],
            position.get('price'),
            position.get('price')
        ))
        self.conn.commit()

    def remove_position(self, position_id: str):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM positions WHERE id = ?', (position_id,))
        self.conn.commit()

    def get_positions(self, exchange: str = None) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        if exchange:
            cursor.execute('SELECT * FROM positions WHERE exchange = ?', (exchange,))
        else:
            cursor.execute('SELECT * FROM positions')
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]