# ourModules/database_manager.py

import sqlite3

class DatabaseManager:
    def __init__(self, db_path="publishing_house.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.open_connection()

        return;
    
    def open_connection(self):
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

        return;
    
    def close_connection(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None
            self.cursor = None

        return;
    
    def execute(self, query, params=None):
        """Execute a single query with optional parameters."""
        if params is None:
            params = ()
        self.cursor.execute(query, params)
        self.conn.commit()

        return;
    
    def fetchall(self, query, params=None):
        """Execute a query and return all rows."""
        if params is None:
            params = ()
        self.cursor.execute(query, params)

        return self.cursor.fetchall();
    
    def get_table_list(self):
        """Returns a list of all user tables in the database."""
        tables = self.fetchall(
            "SELECT name "
            "FROM sqlite_master "
            "WHERE type='table';"
        )

        return [t[0] for t in tables if not t[0].startswith('sqlite_')];
    
    def get_table_columns(self, table_name):
        """Use PRAGMA table_info to get columns in a table."""
        return self.fetchall(f'PRAGMA table_info("{table_name}");');
