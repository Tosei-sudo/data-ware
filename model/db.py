# coding: utf-8
import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class DB:
    def __init__(self, filepath):
        self.filepath = filepath
        
        self.conn = sqlite3.connect(filepath)
        self.conn.row_factory = dict_factory
        self.conn.text_factory = str
        
        self.cur = self.conn.cursor()
    
    def query(self, query, params=None):
        if params is None:
            self.cur.execute(query)
        else:
            self.cur.execute(query, params)
        return self.cur.fetchall()

    def commit(self):
        self.conn.commit()
    
    def __del__(self):
        self.conn.close()