import json
import re
from datetime import datetime

import json
import re
import os
from datetime import datetime

def load_known_users():
    """Load known users from data.json to help with parsing"""
    file_path = 'data/data.json'
    if not os.path.exists(file_path):
        return set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {r['user'] for r in data}
    except Exception:
        return set()

def parse_slack_data(text):
    # Obtener fecha de hoy
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Load known users for better matching
    known_users = load_known_users()

    # 1. Split by timestamp pattern: "  [HH:MM]"
    # This divides the text into chunks. 
    # Chunk 0 is User 0.
    # Chunk i (i>0) contains Message of User i-1 + User i.
    chunks = re.split(r'\s\s\[\d{2}:\d{2}\]', text)
    
    results = []
    
    # Needs at least one chunk + user
    if not chunks:
        return []

    # First user is at the start of the text
    users = [chunks[0].strip()]

    for i in range(1, len(chunks)):
        prev_user = users[-1]
        content = chunks[i]
        
        # A. Extract score for prev_user from this chunk (which is their message)
        # Regex to find the Wordle result: "La palabra del día #1482 2/6"
        score_match = re.search(r'La palabra del día #(\d+) (X|\d)/6', content)
        if score_match:
            num = score_match.group(1)
            score_raw = score_match.group(2)
            score = 7 if score_raw == "X" else int(score_raw)
            
            # Add result for the previous user
            results.append({
                "date": today,
                "user": prev_user,
                "num": num,
                "score": score
            })
        
        # B. Extract the next user from the end of this chunk
        next_user = _clean_username(content, known_users)
        if next_user:
            users.append(next_user)
        else:
            # If we can't identify a name, use a placeholder or the raw tail
            # But "Unknown" prevents mixing data
            users.append("Unknown")
            
    return results

def _clean_username(raw_text, known_users=None):
    """
    Heuristic to extract the user name from the tail of a text chunk.
    The chunk ends with the User Name, but is preceded by the previous User's message.
    """
    # 1. Find the last "stopper" to strip known message artifacts
    # - Specific URL root
    # - Score pattern (X/6)
    # - Closing bracket of a timestamp (if nested)
    stoppers = [r'https://lapalabradeldia\.com/', r'\d/6', r'X/6', r'\]']
    last_idx = -1
    for s in stoppers:
        for m in re.finditer(s, raw_text):
            if m.end() > last_idx:
                last_idx = m.end()
    
    if last_idx != -1:
        candidate = raw_text[last_idx:]
    else:
        candidate = raw_text

    # 0. Check against known users (Longest match first)
    if known_users:
        # Sort by length desc to match longest possible name first
        sorted_users = sorted(known_users, key=len, reverse=True)
        for user in sorted_users:
            if candidate.endswith(user):
                return user

    # 2. Extract from first Capital letter (heuristic for names)
    # Takes the suffix of the string that forms a sequence of capitalized words.
    # e.g. "... último Iria Dorado" -> "Iria Dorado"
    # e.g. "Raquel" -> "Raquel"
    match = re.search(r'((?:[A-Z][^\s]*\s*)+)$', candidate)
    if match:
        return match.group(1).strip()
    
    # Fallback: take the last word if regex fails
    tokens = candidate.split()
    if tokens:
        return tokens[-1]
    
    return ""

def update_json(new_results):
    file_path = 'data/data.json'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    # Evitar duplicados (mismo usuario, mismo número de wordle)
    existing_keys = {(r['user'], r['num']) for r in data}
    added_count = 0
    
    for res in new_results:
        if (res['user'], res['num']) not in existing_keys:
            data.append(res)
            added_count += 1
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return added_count

if __name__ == "__main__":
    print("Pega aquí el contenido de Slack (Presiona Ctrl+D en Linux/Mac o Ctrl+Z en Windows al terminar):")
    import sys
    input_text = sys.stdin.read()
    
    results = parse_slack_data(input_text)
    if not results:
        print("No se encontraron resultados válidos en el texto.")
    else:
        added = update_json(results)
        print(f"¡Éxito! Se han añadido {added} nuevos registros a data/data.json")
