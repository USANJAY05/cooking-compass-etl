from pathlib import Path
from flask import Flask, render_template_string, request, send_from_directory

from .config import IMAGE_DIR
from .db import get_ingredients

app = Flask(__name__)

HTML = '''
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Ingredient Image Viewer</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 1100px; margin: 40px auto; padding: 0 20px; }
    form { display: flex; gap: 10px; margin-bottom: 30px; }
    input { flex: 1; padding: 12px; font-size: 16px; }
    button { padding: 12px 20px; cursor: pointer; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }
    .card { border: 1px solid #ddd; border-radius: 10px; padding: 12px; }
    img { width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 8px; background: #f3f3f3; }
    .missing { aspect-ratio: 1; display: grid; place-items: center; background: #f3f3f3; border-radius: 8px; color: #777; }
    .id { color: #777; font-size: 13px; }
  </style>
</head>
<body>
  <h1>Ingredient Image Viewer</h1>
  <form method="get">
    <input name="q" value="{{ q }}" placeholder="Search by ingredient name or ID">
    <button type="submit">Search</button>
  </form>
  <p>{{ results|length }} result(s)</p>
  <div class="grid">
    {% for item in results %}
      <div class="card">
        {% if item.image_exists %}
          <img src="/images/{{ item.id }}.jpg" alt="{{ item.name }}">
        {% else %}
          <div class="missing">Image not downloaded</div>
        {% endif %}
        <h3>{{ item.name }}</h3>
        <div class="id">ID: {{ item.id }}</div>
      </div>
    {% endfor %}
  </div>
</body>
</html>
'''


@app.route("/")
def index():
    query = request.args.get("q", "").strip().lower()
    ingredients = get_ingredients()

    if query:
        results = [
            item for item in ingredients
            if query in str(item["id"]).lower()
            or query in str(item["name"]).lower()
        ]
    else:
        results = ingredients

    for item in results:
        item["image_exists"] = (
            Path(IMAGE_DIR) / f"{item['id']}.jpg"
        ).exists()

    return render_template_string(HTML, results=results, q=query)


@app.route("/images/<path:filename>")
def images(filename):
    return send_from_directory(IMAGE_DIR, filename)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
