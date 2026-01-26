import re
import json

try:
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Buscar el array JSON. Asumimos que empieza con 'const rawData = [' y termina con '];'
    # Usamos re.DOTALL por si acaso ocupa varias líneas, aunque parece estar en una sola.
    match = re.search(r'const rawData = (\[.*?\]);', content, re.DOTALL)
    
    if match:
        json_str = match.group(1)
        # Intentar parsear para asegurar que es válido
        try:
            data = json.loads(json_str)
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Éxito: Se extrajeron {len(data)} registros a data.json")
        except json.JSONDecodeError as e:
            print(f"Error: El contenido encontrado no es JSON válido. {e}")
    else:
        print("Error: No se encontró la variable rawData en index.html")

except Exception as e:
    print(f"Error inesperado: {e}")
