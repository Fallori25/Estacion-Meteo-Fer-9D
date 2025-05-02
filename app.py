from flask import Flask, request, render_template_string, jsonify
from datetime import datetime, timedelta
import pytz
import pandas as pd
import os
import csv

app = Flask(__name__)
CSV_FILE = "datos.csv"

html_template = """
<html>
<head>
<title>Estación Meteo Fer</title>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<style>
body { font-family: Arial; background-color: #FFB6C1; text-align: center; padding: 20px; }
.card { background: #c7ecee; padding: 15px; margin: 10px auto; border-radius: 20px; max-width: 400px; }
canvas { max-width: 100%; margin-top: 20px; }
</style>
</head>
<body>
<h1>Monitor Climático de Fer</h1>
<div class='card'>Temperatura: {{ temperatura }} °C</div>
<div class='card'>Humedad: {{ humedad }} %</div>
<div class='card'>Presión: {{ presion }} hPa</div>
<div class='card'>Altitud: {{ altitud }} m</div>
<div class='card'>Última actualización: {{ fecha }}</div>

<h2>Gráfico de Temperatura</h2>
<canvas id="graficoTemp"></canvas>
<h2>Gráfico de Humedad</h2>
<canvas id="graficoHum"></canvas>
<h2>Gráfico de Presión</h2>
<canvas id="graficoPres"></canvas>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
let gTemp, gHum, gPres;

function cargar() {
  fetch('/api/datos')
    .then(r => r.json())
    .then(data => {
      const opts = { responsive: true, scales: { y: { beginAtZero: false } } };
      if (!gTemp) {
        gTemp = new Chart(document.getElementById('graficoTemp').getContext('2d'), {
          type: 'line', data: { labels: data.labels, datasets: [{
            label: '°C', data: data.temperaturas, borderColor: 'red', fill: false }] }, options: opts });
        gHum = new Chart(document.getElementById('graficoHum').getContext('2d'), {
          type: 'line', data: { labels: data.labels, datasets: [{
            label: '% Humedad', data: data.humedades, borderColor: 'blue', fill: false }] }, options: opts });
        gPres = new Chart(document.getElementById('graficoPres').getContext('2d'), {
          type: 'line', data: { labels: data.labels, datasets: [{
            label: 'hPa', data: data.presiones, borderColor: 'green', fill: false }] }, options: opts });
      } else {
        gTemp.data.labels = data.labels; gTemp.data.datasets[0].data = data.temperaturas; gTemp.update();
        gHum.data.labels = data.labels; gHum.data.datasets[0].data = data.humedades; gHum.update();
        gPres.data.labels = data.labels; gPres.data.datasets[0].data = data.presiones; gPres.update();
      }
    });
}

cargar();
setInterval(cargar, 60000);
</script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    ultima = leer_ultimo_valor()
    return render_template_string(html_template, **ultima)

@app.route("/update", methods=["POST"])
def update():
    argentina = pytz.timezone('America/Argentina/Buenos_Aires')
    ahora = datetime.now(argentina)
    fila = {
        "fecha": ahora.strftime("%d/%m/%Y"),
        "hora": ahora.strftime("%H:%M"),
        "temperatura": float(request.form.get("temperatura", 0)),
        "humedad": float(request.form.get("humedad", 0)),
        "presion": float(request.form.get("presion", 0)),  # YA NO se suma 60
        "altitud": float(request.form.get("altitud", 0))
    }

    archivo_nuevo = not os.path.exists(CSV_FILE)
    with open(CSV_FILE, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fila.keys())
        if archivo_nuevo:
            writer.writeheader()
        writer.writerow(fila)

    return "OK"

@app.route("/api/datos", methods=["GET"])
def api_datos():
    df = cargar_csv()
    if df.empty:
        return jsonify({"labels": [], "temperaturas": [], "humedades": [], "presiones": []})

    ultimas_48h = df[df["datetime"] > datetime.now() - timedelta(hours=48)]

    # Forzar conversión a numérico
    for col in ["temperatura", "humedad", "presion"]:
        ultimas_48h[col] = pd.to_numeric(ultimas_48h[col], errors="coerce")

    # Agrupar cada 10 minutos
    cada_10min = ultimas_48h.resample("10min", on="datetime").mean().dropna()

    etiquetas = cada_10min.index.strftime("%d %H:%M").tolist()
    return jsonify({
        "labels": etiquetas,
        "temperaturas": cada_10min["temperatura"].tolist(),
        "humedades": cada_10min["humedad"].tolist(),
        "presiones": cada_10min["presion"].tolist()
    })

def leer_ultimo_valor():
    df = cargar_csv()
    if df.empty:
        return {"temperatura": "-", "humedad": "-", "presion": "-", "altitud": "-", "fecha": "-"}
    ultimo = df.iloc[-1]
    return {
        "temperatura": round(ultimo["temperatura"], 1),
        "humedad": round(ultimo["humedad"], 1),
        "presion": round(ultimo["presion"], 1),
        "altitud": round(ultimo["altitud"], 1),
        "fecha": f'{ultimo["fecha"]} {ultimo["hora"]}'
    }

def cargar_csv():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame()
    df = pd.read_csv(CSV_FILE)
    try:
        df["datetime"] = pd.to_datetime(df["fecha"] + " " + df["hora"], format="%d/%m/%Y %H:%M")
        return df
    except:
        return pd.DataFrame()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)



