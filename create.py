# coding: utf-8
from model.db import DB

connection = DB("master.db")

document_master = '''
CREATE TABLE document_master (
    uid INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    link TEXT,
    update_at INTEGER
);
'''

term_dictionary = '''
CREATE TABLE term_dictionary (
    uid INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT,
    document_frequency INTEGER
);
'''

synonyms = '''
CREATE TABLE synonyms (
    uid INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT,
    synonym TEXT
);
'''

postings = '''
CREATE TABLE postings (
    uid INTEGER PRIMARY KEY AUTOINCREMENT,
    term_id INTEGER,
    document_id INTEGER,
    term_frequency INTEGER
);
'''

queries = [
    "DROP TABLE IF EXISTS document_master;",
    document_master,
    "DROP TABLE IF EXISTS term_dictionary;",
    term_dictionary,
    "DROP TABLE IF EXISTS synonyms;",
    synonyms,
    "DROP TABLE IF EXISTS postings;",
    postings
]

for query in queries:
    connection.query(query)

print connection.query("PRAGMA foreign_keys;")

connection.commit()