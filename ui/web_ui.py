
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template_string, request
from agent import SVDPAgent, VendorProfile, DayContext, WeatherCondition, LocationType

app = Flask(__name__)
agent = SVDPAgent()

TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Street Vendor Demand Predictor</title>
<style>
  * {
    box-sizing: border-box;
  }

  body {
    font-family: 'Segoe UI', sans-serif;
    background: linear-gradient(to right, #f5f7fa, #c3cfe2);
    padding: 40px;
    margin: 0;
    color: #333;
  }

  h2 {
    text-align: center;
    color: #2c3e50;
    margin-bottom: 30px;
  }

  form {
    background: #ffffff;
    padding: 25px 30px;
    border-radius: 12px;
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    max-width: 640px;
    margin: auto;
  }

  label {
    margin-top: 10px;
    font-weight: 600;
    display: block;
  }

  input[type="text"],
  input[type="date"],
  input[type="number"],
  select {
    width: 100%;
    padding: 10px;
    border-radius: 6px;
    border: 1px solid #ccc;
    margin-top: 5px;
    margin-bottom: 15px;
    font-size: 1rem;
  }

  input[type="submit"] {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 12px 20px;
    font-size: 1rem;
    font-weight: bold;
    border-radius: 6px;
    cursor: pointer;
    width: 100%;
  }

  input[type="submit"]:hover {
    background-color: #2980b9;
  }

  .result {
    margin-top: 40px;
    max-width: 720px;
    margin-left: auto;
    margin-right: auto;
    background: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 12px 20px rgba(0,0,0,0.1);
    border-left: 6px solid #2ecc71;
  }

  .note {
    background: #fff8e1;
    border-left: 4px solid #f1c40f;
    padding: 10px 15px;
    margin-top: 10px;
    font-size: 0.95rem;
    border-radius: 6px;
  }

  ul {
    padding-left: 20px;
  }

  .section-title {
    margin-top: 25px;
    margin-bottom: 10px;
    color: #2c3e50;
    font-weight: 600;
    font-size: 1.1rem;
  }

  .confidence-bar {
    height: 12px;
    background: #eee;
    border-radius: 6px;
    margin-top: 5px;
    overflow: hidden;
  }

  .confidence-fill {
    height: 100%;
    background: #2ecc71;
  }
</style>
</head>
<body>
  <h2>🍛 Street Vendor Demand Predictor</h2>
  <form method="POST">
    <label for="vendor_id">Select Vendor:</label>
    <select name="vendor_id" id="vendor_id">
      {% for vid, v in vendors.items() %}
      <option value="{{ vid }}">{{ v['profile']['name'] }} ({{ v['profile']['location'] }})</option>
      {% endfor %}
    </select>

    <label for="date">Date:</label>
    <input type="date" name="date">

    <label for="weather">Weather:</label>
    <select name="weather">
      {% for w in weather_options %}
      <option value="{{ w }}">{{ w }}</option>
      {% endfor %}
    </select>

    <label for="temperature">Temperature (°C):</label>
    <input type="number" name="temperature" value="32">

    <label><input type="checkbox" name="is_festival"> Festival Day</label>
    <label><input type="checkbox" name="is_payday"> Payday Week</label>

    <input type="submit" value="Predict Demand">
  </form>

  {% if result %}
  <div class="result">
    <h3>Prediction for {{ result['vendor'] }}</h3>
    <p><strong>Date:</strong> {{ result['date'] }}</p>
    <p><strong>Weather:</strong> {{ result['weather'] }}, {{ result['temperature'] }}°C</p>
    <p><strong>Expected Revenue:</strong> ₹{{ result['revenue'][0] }} - ₹{{ result['revenue'][1] }}</p>
    <p><strong>Peak Hours:</strong> {{ result['peak_hours'] }}</p>
    <p class="section-title">🔍 Confidence: {{ result['confidence'] }}</p>
<div class="confidence-bar">
  <div class="confidence-fill" style="width: {{ result['confidence']|float * 100 }}%"></div>
</div>

    <h4>📦 Inventory Recommendation:</h4>
    <ul>
      {% for item, qty in result['inventory'].items() %}
      <li>{{ item }}: {{ qty }} units</li>
      {% endfor %}
    </ul>

    <h4>📝 Notes:</h4>
    {% if result['notes'] %}
      {% for note in result['notes'] %}
      <div class="note">{{ note }}</div>
      {% endfor %}
    {% else %}
      <div class="note">All set! No critical issues predicted for the day.</div>
    {% endif %}
  </div>
  {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    vendors = agent.memory["vendors"]
    weather_options = [w.value for w in WeatherCondition]

    if request.method == "POST":
        vendor_id = request.form["vendor_id"]
        v = vendors[vendor_id]["profile"]
        vendor = VendorProfile(
            name=v["name"],
            location=v["location"],
            location_type=LocationType(v["location_type"]),
            items_sold=v["items_sold"],
            avg_daily_revenue=v["avg_daily_revenue"],
            peak_hours=v["peak_hours"]
        )
        date = request.form.get("date") or "2025-06-17"
        day_of_week = "Tuesday"  # fallback default, can add logic if needed
        context = DayContext(
            date=date,
            day_of_week=day_of_week,
            weather=WeatherCondition(request.form["weather"]),
            is_festival=bool(request.form.get("is_festival")),
            is_payday=bool(request.form.get("is_payday")),
            temperature=int(request.form["temperature"])
        )
        pred = agent.predict(vendor, context)
        result = {
            "vendor": vendor.name,
            "date": date,
            "weather": context.weather.value,
            "temperature": context.temperature,
            "revenue": pred.expected_revenue,
            "peak_hours": pred.peak_hours,
            "confidence": f"{pred.confidence_level:.2f}",
            "inventory": pred.recommended_items,
            "notes": pred.special_notes
        }

    return render_template_string(TEMPLATE, vendors=vendors, result=result, weather_options=weather_options)

if __name__ == "__main__":
    app.run(debug=True)
