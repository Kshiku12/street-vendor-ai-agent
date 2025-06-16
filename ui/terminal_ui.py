#!/usr/bin/env python3
"""
Terminal UI for Street Vendor Demand Predictor (SVDP)
Author: Kumar Kshitij
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent import SVDPAgent, WeatherCondition, LocationType
from agent import VendorProfile, DayContext
from datetime import datetime
import sys

# Initialize agent
agent = SVDPAgent()

# Welcome banner
print("\n" + "=" * 70)
print("🍛 STREET VENDOR DEMAND PREDICTOR (SVDP)")
print("AI for India's Informal Economy")
print("Thinks in Rupees, Not Just Data Points")
print("=" * 70 + "\n")

# Step 1: Vendor selection
print("👤 Select Vendor")
vendors = list(agent.memory['vendors'].keys())
for i, key in enumerate(vendors, 1):
    print(f"{i}. {key.replace('_', ' ')}")

try:
    choice = int(input("\nEnter vendor number: ")) - 1
    vendor_id = vendors[choice]
    profile_data = agent.memory['vendors'][vendor_id]['profile']
    vendor = VendorProfile(
        name=profile_data['name'],
        location=profile_data['location'],
        location_type=LocationType(profile_data['location_type']),
        items_sold=profile_data['items_sold'],
        avg_daily_revenue=profile_data['avg_daily_revenue'],
        peak_hours=profile_data['peak_hours']
    )
except (ValueError, IndexError, KeyError) as e:
    print("❌ Invalid selection.")
    sys.exit(1)

# Step 2: Day context
print("\n📅 Enter Day Context")
date_str = input("Date (YYYY-MM-DD) [leave blank for today]: ").strip()
if not date_str:
    date_str = datetime.now().strftime("%Y-%m-%d")
day_of_week = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")

print("\nWeather:")
for i, condition in enumerate(WeatherCondition, 1):
    print(f"{i}. {condition.value.title()}")
try:
    weather_choice = int(input("Choose weather (1-4): "))
    weather = list(WeatherCondition)[weather_choice - 1]
except:
    weather = WeatherCondition.SUNNY

temp = int(input("Temperature (°C): ") or "32")
is_festival = input("Is today a festival? (y/n): ").lower() == 'y'
is_payday = input("Is it payday week? (y/n): ").lower() == 'y'

context = DayContext(
    date=date_str,
    day_of_week=day_of_week,
    weather=weather,
    is_festival=is_festival,
    is_payday=is_payday,
    temperature=temp
)

# Step 3: Predict
print("\n🔮 Generating prediction...")
pred = agent.predict(vendor, context)

# Step 4: Output
print("\n" + "=" * 70)
print(f"Prediction for {vendor.name.upper()} ({vendor.location})")
print("=" * 70)
print(f"📅 Date: {context.date} ({context.day_of_week})")
print(f"🌤️  Weather: {context.weather.value.title()} | Temp: {context.temperature}°C")
print(f"💰 Expected Revenue: ₹{pred.expected_revenue[0]} – ₹{pred.expected_revenue[1]}")
print(f"📈 Confidence: {pred.confidence_level:.1%}")
print("\n📦 Inventory Recommendation:")
for item, qty in pred.recommended_items.items():
    print(f" - {item}: {qty} units")

print("\n⏰ Peak Hours:", ", ".join(map(str, pred.peak_hours)))

if pred.special_notes:
    print("\n📝 Notes:")
    for note in pred.special_notes:
        print(" -", note)

print("\n✅ Prediction complete. Memory updated.")
