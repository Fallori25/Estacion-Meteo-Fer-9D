from flask import Flask, request, render_template_string
from datetime import datetime

app = Flask(__name__)

# Variables para guardar los datos
datos = {
    "temperatura": "-",
    "humedad": "-",
    "presion": "-",
    "altitud": "-",
    "fecha": "-"
}

# HTML base (igual al de tu ESP32)
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
    datos["temperatura"] = request.form.get("temperatura", "-")
    datos["humedad"] = request.form.get("humedad", "-")
    datos["presion"] = request.form.get("presion", "-")
    datos["altitud"] = request.form.get("altitud", "-")
    datos["fecha"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
