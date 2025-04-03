#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import datetime
from typing import List, Dict, Any

def get_recent_entries(db_path: str, hours_back: int = 8) -> List[Dict[Any, Any]]:
    """
    Retrieve entries from the past few hours from the FreshRSS database
    
    Args:
        db_path: Path to the SQLite database
        hours_back: How many hours back to look for entries
        
    Returns:
        List of dictionaries containing feed entries with their content
    """
    # Calculate timestamp for N hours ago
    now = datetime.datetime.now()
    timestamp = int((now - datetime.timedelta(hours=hours_back)).timestamp())
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Query for recent entries including their content
    query = """
    SELECT 
        e.id, e.title, e.author, e.content, e.link, e.date, 
        c.name as category, f.name as feed_name 
    FROM entry e
    JOIN feed f ON e.id_feed = f.id
    LEFT JOIN category c ON f.category = c.id
    WHERE e.date >= ?
    ORDER BY e.date DESC
    """
    
    cursor.execute(query, (timestamp,))
    results = cursor.fetchall()
    
    # Convert to list of dictionaries
    entries = []
    for row in results:
        entry = {
            'id': row['id'],
            'title': row['title'],
            'author': row['author'],
            'content': row['content'],
            'link': row['link'],
            'date': datetime.datetime.fromtimestamp(row['date']),
            'category': row['category'] or 'Uncategorized',
            'feed_name': row['feed_name']
        }
        entries.append(entry)
    
    conn.close()
    return entries

def group_entries_by_category(entries: List[Dict[Any, Any]]) -> Dict[str, List[Dict[Any, Any]]]:
    """
    Group entries by their category
    
    Args:
        entries: List of entry dictionaries
        
    Returns:
        Dictionary with categories as keys and lists of entries as values
    """
    grouped = {}
    
    for entry in entries:
        category = entry['category']
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(entry)
        
    return grouped 