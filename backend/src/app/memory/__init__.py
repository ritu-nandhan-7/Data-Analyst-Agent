# Enhanced memory store with persistence
import sqlite3
import pickle
import os
from typing import Any
import pandas as pd

# In-memory store with persistence
class PersistentMemoryStore:
    def __init__(self, persist_file='backend/data/memory_store.pkl'):
        self.persist_file = persist_file
        # Ensure data directory exists
        os.makedirs(os.path.dirname(persist_file), exist_ok=True)
        self.store = {}
        self.load()
    
    def load(self):
        """Load data from disk if it exists"""
        if os.path.exists(self.persist_file):
            try:
                with open(self.persist_file, 'rb') as f:
                    self.store = pickle.load(f)
                print(f"📁 Loaded memory store with {len(self.store)} items")
            except Exception as e:
                print(f"⚠️ Could not load memory store: {e}")
                self.store = {}
    
    def save(self):
        """Save data to disk"""
        try:
            with open(self.persist_file, 'wb') as f:
                pickle.dump(self.store, f)
            print(f"💾 Saved memory store with {len(self.store)} items")
        except Exception as e:
            print(f"⚠️ Could not save memory store: {e}")
    
    def get(self, key, default=None):
        return self.store.get(key, default)
    
    def set(self, key, value):
        self.store[key] = value
        self.save()  # Auto-save on changes
    
    def delete(self, key):
        if key in self.store:
            del self.store[key]
            self.save()
    
    def keys(self):
        return self.store.keys()
    
    def __getitem__(self, key):
        return self.store[key]
    
    def __setitem__(self, key, value):
        self.set(key, value)
    
    def __contains__(self, key):
        return key in self.store

# Create persistent memory store instance
memory_store = PersistentMemoryStore()

# For MVP, use in-memory dict. For persistence, use SQLite.
def get_db():
    conn = sqlite3.connect('backend/data/memory.db')
    return conn

def save_conversation(session_id: str, question: str, answer: Any):
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS memory (session_id TEXT, question TEXT, answer TEXT)''')
    c.execute('INSERT INTO memory VALUES (?, ?, ?)', (session_id, question, str(answer)))
    conn.commit()
    conn.close()

def get_conversation(session_id: str):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT question, answer FROM memory WHERE session_id=?', (session_id,))
    rows = c.fetchall()
    conn.close()
    return rows
