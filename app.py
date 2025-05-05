from flask import Flask, request, render_template_string, jsonify
from datetime import datetime
import pytz
import requests

app = Flask(__name__)

# Variables actuales
datos = {
    "temperatura": "-",
    "humedad": "-",
    "presion": "-",
    "fecha": "-"
}

# Historial para 3 horas con 10 minutos entre puntos: 18 registros
historial = []

# API clima externo

def obtener_clima():
    try:
        api_key = "TU_API_KEY"  # ← Reemplazar por tu API key real
        ciudad = "San Miguel de Tucuman,AR"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&units=metric&lang=es&appid={api_key}"
        r = requests.get(url)
        data = r.json()

        descripcion = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        humedad = data["main"]["humidity"]
        presion = data["main"]["pressure"]
        viento = data["wind"]["speed"]

        resumen = f"{descripcion} – {temp:.1f} °C – Humedad {humedad}% – Viento {viento} m/s – Presión {presion} hPa"
        return resumen
    except Exception:
        return "No se pudo obtener el clima externo"

# HTML
html_template = """
<html>
<head>
<title>Monitor Climatico de Fer 9D</title>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<meta http-equiv='refresh' content='600'>
<style>
body { font-family: Arial, sans-serif; background-color: #FFB6C1; text-align: center; padding: 20px; margin: 0; }
.header { display: flex; justify-content: center; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 30px; }
.mini-card { background-color: red; color: white; padding: 10px 15px; border-radius: 10px; font-size: 1em; font-weight: bold; }
h1 { color: #2c3e50; font-size: 2em; margin: 0; }
.card { background: linear-gradient(135deg, #00CED1, #c7ecee); padding: 15px; margin: 15px auto; border-radius: 20px; max-width: 500px; box-shadow: 0px 4px 20px rgba(0,0,0,0.1); }
.dato { font-size: 1.5em; font-weight: bold; }
canvas { max-width: 100%; margin: 20px auto; }
</style>
</head>
<body>
  <div class='header'>
    <div class='mini-card'>San Miguel de Tucumán</div>
    <div class='mini-card'><span id="reloj">--:--:--</span></div>
  </div>

  <h1>Monitor Climatico de Fer 9D</h1>

  <div class='card'><div class='dato'>Temperatura: {{ temperatura }} &#8451;</div></div>
  <div class='card'><div class='dato'>Humedad: {{ humedad }} %</div></div>
  <div class='card'><div class='dato'>Presión: {{ presion }} hPa</div></div>
  <div class='card'><div class='dato'>Clima externo: {{ clima_ext }}</div></div>

  <h2>Gráfico de Temperatura</h2>
  <canvas id="graficoTemp"></canvas>

  <h2>Gráfico de Humedad</h2>
  <canvas id="graficoHum"></canvas>

  <h2>Gráfico de Presión</h2>
  <canvas id="graficoPres"></canvas>

  <script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script>
  <script>
    function actualizarReloj() {
      const ahora = new Date();
      const hora = ahora.toLocaleTimeString('es-AR', { hour12: false });
      document.getElementById('reloj').textContent = hora;
    }
    setInterval(actualizarReloj, 1000);
    actualizarReloj();

    let gTemp, gHum, gPres;
    function cargarGraficos() {
      fetch('/api/datos')
        .then(r => r.json())
        .then(data => {
          if (!gTemp) {
            gTemp = new Chart(document.getElementById('graficoTemp').getContext('2d'), {
              type: 'line',
              data: {
                labels: data.labels,
                datasets: [{
                  label: 'Temperatura (°C)',
                  data: data.temperaturas,
                  borderColor: 'red',
                  backgroundColor: 'transparent',
                  tension: 0.4,
                  pointRadius: 2
                }]
              },
              options: { responsive: true }
            });
          } else {
            gTemp.data.labels = data.labels;
            gTemp.data.datasets[0].data = data.temperaturas;
            gTemp.update();
          }

          if (!gHum) {
            gHum = new Chart(document.getElementById('graficoHum').getContext('2d'), {
              type: 'line',
              data: {
                labels: data.labels,
                datasets: [{
                  label: 'Humedad (%)',
                  data: data.humedades,
                  borderColor: 'blue',
                  backgroundColor: 'transparent',
                  tension: 0.4,
                  pointRadius: 2
                }]
              },
              options: { responsive: true }
            });
          } else {
            gHum.data.labels = data.labels;
            gHum.data.datasets[0].data = data.humedades;
            gHum.update();
          }

          if (!gPres) {
            gPres = new Chart(document.getElementById('graficoPres').getContext('2d'), {
              type: 'line',
              data: {
                labels: data.labels,
                datasets: [{
                  label: 'Presión (hPa)',
                  data: data.presiones,
                  borderColor: 'green',
                  backgroundColor: 'transparent',
                  tension: 0.4,
                  pointRadius: 2
                }]
              },
              options: { responsive: true }
            });
          } else {
            gPres.data.labels = data.labels;
            gPres.data.datasets[0].data = data.presiones;
            gPres.update();
          }
        });
    }
    cargarGraficos();
    setInterval(cargarGraficos, 600000);
  </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(html_template,
                                  temperatura=datos["temperatura"],
                                  humedad=datos["humedad"],
                                  presion=datos["presion"],
                                  fecha=datos["fecha"],
                                  clima_ext=obtener_clima())

@app.route("/update", methods=["POST"])
def update():
    argentina = pytz.timezone('America/Argentina/Buenos_Aires')
    datos["fecha"] = datetime.now(argentina).strftime("%d/%m/%Y %H:%M")
    try:
        temperatura = float(request.form.get("temperatura", "-"))
        humedad = float(request.form.get("humedad", "-"))
        presion = float(request.form.get("presion", "-"))

        datos["temperatura"] = f"{temperatura:.1f}"
        datos["humedad"] = f"{humedad:.1f}"
        datos["presion"] = f"{presion:.1f}"

        registro = {
            "hora": datetime.now(argentina).strftime("%H:%M"),
            "temperatura": temperatura,
            "humedad": humedad,
            "presion": presion
        }
        historial.append(registro)
        if len(historial) > 18:
            historial.pop(0)

    except:
        datos["temperatura"] = datos["humedad"] = datos["presion"] = "-"

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

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
