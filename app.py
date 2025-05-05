def obtener_clima():
    try:
        api_key = "TU_API_KEY"  # ← reemplazá esto por tu clave real
        ciudad = "San Miguel de Tucuman,AR"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&units=metric&lang=es&appid={api_key}"
        r = requests.get(url)
        data = r.json()

        descripcion = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        humedad = data["main"]["humidity"]
        presion = data["main"]["pressure"]
        viento = data["wind"]["speed"] * 3.6  # Convertir de m/s a km/h

        resumen = f"{descripcion} – {temp:.1f} °C – Humedad {humedad}% – Viento {viento:.1f} km/h – Presión {presion} hPa"
        return resumen
    except Exception:
        return "No se pudo obtener el clima externo"

