# coding: utf-8
from model.db import DB
import unicodedata
import math
import time
import datetime as dt

connection = DB("master.db")

synonyms_dictionary = {}

all_terms = {}

def create_term(term):
    query = "INSERT INTO term_dictionary (term, document_frequency) VALUES (?, 0);"
    connection.query(query, (sanitize(term),))
    
    load_all_terms()

def load_all_terms():
    terms = connection.query("SELECT * FROM term_dictionary;")
    
    for term in terms:
        key = unicode(term['term'], 'utf-8')
        all_terms[key] = term['uid']

def unixTime(d):
    return int(time.mktime(d.timetuple()))

def sanitize(word):
    if type(word) is not unicode:
        word = unicode(word, 'utf-8')
    
    return unicodedata.normalize('NFKD', word).lower()

def create_document(title, author, link):
    update_at = unixTime(dt.datetime.now())
    
    query = "INSERT INTO document_master (title, author, link, update_at) VALUES (?, ?, ?, ?);"
    connection.query(query, (sanitize(title), sanitize(author), sanitize(link), update_at))
    
    document = connection.query("SELECT * FROM document_master WHERE rowid = last_insert_rowid();")[0]

    return document

def update_document_frequency(term_id):
    document_frequency = connection.query("SELECT COUNT(*) as cnt FROM postings WHERE term_id = ?;", (term_id,))[0]['cnt']
    
    query = "UPDATE term_dictionary SET document_frequency = {0} WHERE uid = ?;".format(document_frequency)
    connection.query(query, (term_id,))

def create_postings(term_id, document_id, term_frequency):
    query = "INSERT INTO postings (term_id, document_id, term_frequency) VALUES (?, ?, ?);"
    connection.query(query, (term_id, document_id, term_frequency))

# ①本文を受け取り、タームごとに分割し、配列に格納
# document_master テーブルに新規レコードを追加
# タームごとに、postings テーブルに出現回数および文書 ID を追加
# ②タームの文書頻度を更新
import collections

def create(title, link, body):
    document = create_document(title, 'indexer', link)
    document_id = document['uid']
    
    raw_terms = body.split(u" ")
    terms_count = collections.Counter(raw_terms)
    
    term_count_dict = {}
    for term, count in terms_count.items():
        term_id = all_terms.get(term, None)
        
        if term_id is None:
            create_term(term)
            term_id = all_terms.get(term)
        
        term_count_dict[term_id] = count
    
    for term_id, term_frequency in term_count_dict.items():
        create_postings(term_id, document_id, term_frequency)
        update_document_frequency(term_id)
    
    connection.commit()

load_all_terms()
# create("鉄道うぃき", "http://example.com", u"鉄道 運行 遅延 遅れ 事故 列車 遅延")

with open('data7.txt') as f:
    body = sanitize(f.read())
    create(u"Wikipedia-警察庁", "https://ja.wikipedia.org/wiki/%E5%86%85%E9%96%A3_(%E6%97%A5%E6%9C%AC)", body)