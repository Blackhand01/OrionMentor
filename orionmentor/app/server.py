from pathlib import Path
from flask import Flask, render_template, request, jsonify, Response
from orionmentor.core.chains import build_chain, build_chain_router
from orionmentor.core.telemetry.store import STORE

BASE_DIR = Path(__file__).resolve().parents[1]
TEMPLATES = str(BASE_DIR / "ui" / "templates")
STATIC = str(BASE_DIR / "ui" / "static")

app = Flask(__name__, template_folder=TEMPLATES, static_folder=STATIC, static_url_path="/static")
chain = build_chain_router()

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/mentor")
def mentor():
    data = request.get_json() or {}
    topic = data.get("topic","Spiega agentic RAG con schema e mini-esercizio")
    try:
        result = chain(topic)
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# --- Dashboard & Metrics API ---
@app.get("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.get("/api/metrics/summary")
def metrics_summary():
    return jsonify(STORE.summary())

@app.get("/api/metrics/timeseries")
def metrics_timeseries():
    return jsonify({
        "latency": STORE.timeseries_latency(),
        "tokens": STORE.tokens_timeseries(),
    })

@app.get("/api/metrics/fail_reasons")
def metrics_fail_reasons():
    return jsonify(STORE.distribution_fail_reasons())

@app.get("/api/metrics/export")
def metrics_export():
    csv_str = STORE.export_csv()
    return Response(
        csv_str,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=orionmentor_metrics.csv"},
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
