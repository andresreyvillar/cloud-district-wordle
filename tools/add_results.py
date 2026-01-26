import json
import re
from datetime import datetime

def parse_slack_data(text):
    # Obtener fecha de hoy
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Expresión regular para capturar: Nombre, Número de Wordle y Puntuación
    # Busca un nombre seguido de una hora, luego "La palabra del día #XXXX X/6"
    pattern = r"([A-Za-z\s\.]+)\n\s+\d{2}:\d{2}\nLa palabra del día #(\d+) (X|\d)/6"
    
    matches = re.finditer(pattern, text)
    results = []
    
    for match in matches:
        user = match.group(1).strip()
        num = match.group(2)
        score_raw = match.group(3)
        
        # Convertir "X" (fallo) en 7 para las estadísticas
        score = 7 if score_raw == "X" else int(score_raw)
        
        results.append({
            "date": today,
            "user": user,
            "num": num,
            "score": score
        })
    
    return results

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
