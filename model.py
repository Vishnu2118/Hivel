import csv
import random
from flask import Flask, request, jsonify
from collections import defaultdict
from io import TextIOWrapper

app = Flask(__name__)

def load_menu(file_stream):
    menu = defaultdict(list)
    reader = csv.DictReader(TextIOWrapper(file_stream, encoding='utf-8'))

    for row in reader:
        try:
            category = row['category'].strip().lower()
            item = {
                'name': row['item_name'].strip(),
                'calories': int(float(row['calories'])),
                'popularity': float(row['popularity_score'])
            }
            # Normalize category names
            if category == 'main':
                menu['dish'].append(item)
            elif category == 'side':
                menu['sidedish'].append(item)
            elif category == 'drink':
                menu['drink'].append(item)
        except (ValueError, KeyError):
            continue

    return menu

def score_item(item):
    return item['popularity'] - item['calories'] / 100.0

def create_combo(menu):
    combo = {}
    reason = {}

    for category in ['dish', 'sidedish', 'drink']:
        items = random.sample(menu[category], min(5, len(menu[category])))
        best = max(items, key=score_item)
        combo[category] = best['name']
        reason[category] = (
            f"{best['name']} was chosen for high popularity "
            f"({best['popularity']}) and moderate calories ({best['calories']})."
        )

    return combo, reason

@app.route('/daily-combos', methods=['POST'])
def daily_combos():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    menu = load_menu(file)

    if not all(k in menu and menu[k] for k in ['dish', 'sidedish', 'drink']):
        return jsonify({"error": "CSV must contain at least one of each: main, side, drink"}), 400

    combos = []
    for _ in range(3):
        combo, reason = create_combo(menu)
        combos.append({
            'combo': combo,
            'reason': reason
        })

    return jsonify({"combos_for_the_day": combos})

if __name__ == '__main__':
    app.run(debug=True)
