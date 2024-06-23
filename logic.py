# coding: utf-8
from model.db import DB
import unicodedata
import math

connection = DB("master.db")

synonyms_dictionary = {}

def sanitize(word):
    if type(word) is not unicode:
        word = unicode(word, 'utf-8')
    
    return unicodedata.normalize('NFKD', word).lower()

def create_synonyms(word, synonym):
    
    query = "INSERT INTO synonyms (word, synonym) VALUES (?, ?);"
    connection.query(query, (sanitize(word), sanitize(synonym)))
    connection.commit()

def create_term(term):
    query = "INSERT INTO term_dictionary (term, document_frequency) VALUES (?, 0);"
    connection.query(query, (sanitize(term),))
    connection.commit()

def load_synonyms_dictionary():
    query = "SELECT * FROM synonyms;"
    result = connection.query(query)
    
    for row in result:
        key = unicode(row['synonym'], 'utf-8')
        synonyms_dictionary[key] = unicode(row['word'], 'utf-8')

def tf_idf_weight(tf, df, N):
    return (1 + math.log(tf)) * math.log(N / df)

def query_parse(raw_query):
    # 表記の揺らぎを解決し、タームごとに分割し、配列に格納
    # その後類義語辞書を参照し、タームを拡張および統合
    # 最終的なクエリを配列で返す
    shaped_query = sanitize(raw_query)

    raw_terms = shaped_query.split(u" ")
    
    for i in range(len(raw_terms)):
        raw_term = raw_terms[i]
        raw_terms[i] = synonyms_dictionary.get(raw_term, raw_term)
    
    raw_terms = set(raw_terms)
    
    return raw_terms

def query_search(raw_terms):
    terms = connection.query(u"SELECT * FROM term_dictionary WHERE term IN ({0});".format(",".join(["?" for _ in raw_terms])), tuple(raw_terms))
    
    query_term_dict = {}
    for term in terms:
        query_term_dict[term['uid']] = term['document_frequency']

    term_ids = query_term_dict.keys()
    postings = connection.query(u"SELECT * FROM postings WHERE term_id IN ({0});".format(",".join(["?" for _ in term_ids])), term_ids)
    
    postings_term_dict = {}
    for posting in postings:
        if posting['term_id'] not in postings_term_dict:
            postings_term_dict[posting['term_id']] = []
        
        postings_term_dict[posting['term_id']].append((posting['document_id'], posting['term_frequency']))
    
    N = float(connection.query("SELECT COUNT(*) as cnt FROM document_master;")[0]['cnt'])
    
    tf_idf_dict = {}
    for term_id, df in query_term_dict.items():
        documents_data = postings_term_dict[term_id]
        for document_data in documents_data:
            document_id, tf = document_data
            tf_idf_dict[document_id] = tf_idf_dict.get(document_id, 0) + tf_idf_weight(tf, df, N)
    
    document_ids = tf_idf_dict.keys()
    documents = connection.query(u"SELECT * FROM document_master WHERE uid IN ({0});".format(",".join(["?" for _ in document_ids])), document_ids)
    
    sorted_documents = sorted(documents, key=lambda x: tf_idf_dict[x['uid']], reverse=True)
    
    return sorted_documents
    
def query(raw_query):
    raw_terms = query_parse(raw_query)
    return query_search(raw_terms)

load_synonyms_dictionary()

print query(u"内閣")