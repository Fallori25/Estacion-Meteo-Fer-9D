from flask import Flask, request, render_template_string, jsonify
from datetime import datetime
import pytz

app = Flask(__name__)

datos = {
    "temperatura": "-",
    "humedad": "-",
    "presion": "-",
    "altitud": "-",
    "fecha": "-"
}

historial = []

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
    return render_template_string(html_template, **datos)

@app.route("/update", methods=["POST"])
def update():
    argentina = pytz.timezone('America/Argentina/Buenos_Aires')
    ahora = datetime.now(argentina)

    datos["temperatura"] = request.form.get("temperatura", "-")
    datos["humedad"] = request.form.get("humedad", "-")
    datos["presion"] = request.form.get("presion", "-")
    datos["altitud"] = request.form.get("altitud", "-")
    datos["fecha"] = ahora.strftime("%d/%m/%Y %H:%M")

    try:
        historial.append({
            "hora": ahora.strftime("%H:%M"),
            "temperatura": float(datos["temperatura"]),
            "humedad": float(datos["humedad"]),
            "presion": float(datos["presion"])
        })
        if len(historial) > 10:
            historial.pop(0)
    except:
        pass

    return "OK"

@app.route("/api/datos", methods=["GET"])
def api_datos():
    etiquetas = [r["hora"] for r in historial]
    temperaturas = [r["temperatura"] for r in historial]
    humedades = [r["humedad"] for r in historial]
    presiones = [r["presion"] for r in historial]
    return jsonify({
        "labels": etiquetas,
        "temperaturas": temperaturas,
        "humedades": humedades,
        "presiones": presiones
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)




