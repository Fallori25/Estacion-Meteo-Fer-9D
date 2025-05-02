from flask import Flask, request, render_template_string, jsonify
from datetime import datetime
import pytz

app = Flask(__name__)

# Variables para guardar los datos actuales
datos = {
    "temperatura": "-",
    "humedad": "-",
    "presion": "-",
    "altitud": "-",
    "fecha": "-"
}

# Historial de las últimas 10 temperaturas
historial = []

# HTML de la página con gráfico que se actualiza automáticamente
html_template = """
<html>
<head>
<title>Monitor Climatico de Fer 9D</title>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<meta http-equiv='refresh' content='60'>
<style>
body { font-family: Arial, sans-serif; background-color: #FFB6C1; text-align: center; padding: 20px; margin: 0; }
.header { display: flex; justify-content: center; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 30px; }
.mini-card { background-color: red; color: white; padding: 10px 15px; border-radius: 10px; font-size: 1em; font-weight: bold; }
h1 { color: #2c3e50; font-size: 2em; margin: 0; }
.card { background: linear-gradient(135deg, #00CED1, #c7ecee); padding: 15px; margin: 15px auto; border-radius: 20px; max-width: 400px; box-shadow: 0px 4px 20px rgba(0,0,0,0.1); }
.dato { font-size: 2em; font-weight: bold; }
</style>
</head>
<body>
  <div class='header'>
    <div class='mini-card'>San Miguel de Tucumán</div>
    <div class='mini-card'>{{ fecha }}</div>
  </div>

  <h1>Monitor Climatico de Fer 9D</h1>

  <div class='card'><div class='dato'>Temperatura: {{ temperatura }} &#8451;</div></div>
  <div class='card'><div class='dato'>Humedad: {{ humedad }} %</div></div>
  <div class='card'><div class='dato'>Presión: {{ presion }} hPa</div></div>
  <div class='card'><div class='dato'>Altitud: {{ altitud }} m</div></div>

  <h2>Gráfico de Temperatura</h2>
  <canvas id="graficoTemp" width="400" height="200"></canvas>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script>
    let grafico;

    function cargarDatos() {
      fetch('/api/datos')
        .then(response => response.json())
        .then(data => {
          if (!grafico) {
            const ctx = document.getElementById('graficoTemp').getContext('2d');
            grafico = new Chart(ctx, {
              type: 'line',
              data: {
                labels: data.labels,
                datasets: [{
                  label: 'Temperatura (°C)',
                  data: data.values,
                  borderWidth: 2,
                  borderColor: 'red',
                  fill: false
                }]
              },
              options: {
                scales: {
                  y: {
                    beginAtZero: false
                  }
                }
              }
            });
          } else {
            grafico.data.labels = data.labels;
            grafico.data.datasets[0].data = data.values;
            grafico.update();
          }
        });
    }

    cargarDatos();
    setInterval(cargarDatos, 60000); // actualizar cada 60 segundos
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
                                  altitud=datos["altitud"],
                                  fecha=datos["fecha"])

@app.route("/update", methods=["POST"])
def update():
    argentina = pytz.timezone('America/Argentina/Buenos_Aires')

    datos["temperatura"] = request.form.get("temperatura", "-")
    datos["humedad"] = request.form.get("humedad", "-")
    datos["presion"] = request.form.get("presion", "-")
    datos["altitud"] = request.form.get("altitud", "-")
    datos["fecha"] = datetime.now(argentina).strftime("%d/%m/%Y %H:%M")

    # Guardar en historial
    try:
        registro = {
            "hora": datetime.now(argentina).strftime("%H:%M"),
            "temperatura": float(datos["temperatura"])
        }
        historial.append(registro)
        if len(historial) > 10:
            historial.pop(0)
    except:
        pass

    return "OK"

@app.route("/api/datos", methods=["GET"])
def api_datos():
    etiquetas = [r["hora"] for r in historial]
    valores = [r["temperatura"] for r in historial]
    return jsonify({"labels": etiquetas, "values": valores})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
