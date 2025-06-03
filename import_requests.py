import requests
from datetime import datetime

# === DATENABFRAGE ===
germany_url = "https://api.aredl.net/v2/api/aredl/country/276"
response_germany = requests.get(germany_url)
if response_germany.status_code != 200:
    print("No Country Data received")
    exit()
germany_data = response_germany.json()

german_completed_ids = set()
for r in germany_data.get("records", []):
    german_completed_ids.add(r.get("level_id"))
for v in germany_data.get("verified", []):
    german_completed_ids.add(v.get("level_id"))

levels_url = "https://api.aredl.net/v2/api/aredl/levels"
response_levels = requests.get(levels_url)
if response_levels.status_code != 200:
    print("No List Data received")
    exit()
all_levels = response_levels.json()

# === FILTERN ===
not_completed_in_germany = []
for level in all_levels:
    if level.get("legacy"):
        continue
    level_id = level.get("id")
    if level_id not in german_completed_ids:
        not_completed_in_germany.append({
            "name": level.get("name"),
            "position": level.get("position")
        })
not_completed_in_germany.sort(key=lambda x: x["position"])

# === TEXT GENERIEREN ===
lines = [f"{level['position']:>3}: {level['name']}" for level in not_completed_in_germany]
full_text = "\n".join(lines)

now = datetime.now()

# === HTML AKTUALISIEREN ===
html_path = "index.html"
start_tag = "<!--CONTENT_START-->"
end_tag = "<!--CONTENT_END-->"

try:
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
except FileNotFoundError:
    print("Fehler: index.html nicht gefunden.")
    exit()

# Content ersetzen
start_index = html.find(start_tag)
end_index = html.find(end_tag)

if start_index == -1 or end_index == -1:
    print("Fehler: Platzhalter <!--CONTENT_START--> oder <!--CONTENT_END--> nicht gefunden.")
    exit()

start_index += len(start_tag)
new_html = html[:start_index] + "\n" + full_text + "\n" + html[end_index:]

# Jetzt Timestamp ersetzen
timestamp_start = "<!--TIMESTAMP_START-->"
timestamp_end = "<!--TIMESTAMP_END-->"

timestamp_index_start = new_html.find(timestamp_start)
timestamp_index_end = new_html.find(timestamp_end)

if timestamp_index_start != -1 and timestamp_index_end != -1:
    timestamp_index_start += len(timestamp_start)
    timestamp_str = f" Letzte Aktualisierung: {now.strftime('%Y-%m-%d %H:%M:%S')} "
    new_html = new_html[:timestamp_index_start] + timestamp_str + new_html[timestamp_index_end:]
else:
    print("Warnung: Timestamp-Platzhalter nicht gefunden.")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(new_html)

print("index.html wurde erfolgreich aktualisiert.")

