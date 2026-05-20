import os, sqlite3, io, json
from datetime import datetime
from flask import Flask, jsonify, request, render_template, send_file
from reportlab.pdfgen import canvas

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'steel_prices.db')

def get_steel_types():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT type, price FROM steel_prices ORDER BY type").fetchall()
    conn.close()
    return [{"type": r[0], "price": r[1]} for r in rows]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/steel-types")
def api_steel_types():
    return jsonify(get_steel_types())

@app.route("/api/export/pdf", methods=["POST"])
def api_export_pdf():
    data = request.get_json() or {}
    result = data.get("result", {})
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 780, "Steel Price Calculator - Report")
    c.setFont("Helvetica", 10)
    c.drawString(50, 760, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.line(50, 750, 550, 750)
    y = 730
    for k, v in result.items():
        c.setFont("Helvetica-Bold" if k == "Total Price" else "Helvetica", 11)
        txt = f"{k}: {v}".replace("\u00b3", "3").replace("\u00b0", "deg").replace("\u00b7", "-")
        c.drawString(60, y, txt)
        y -= 22
    c.save()
    buf.seek(0)
    return send_file(buf, mimetype="application/pdf", as_attachment=True,
                     download_name="steel_calc_report.pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
