#!/usr/bin/env python3
"""
Street Vendor Demand Predictor (SVDP) Agent
Main logic implementing the 4-layer architecture: Input → State → Task → Output

Author: Kumar Kshitij
Purpose: AI for India's informal economy - thinks in rupees, not just data points
"""

import json
import datetime
from typing import Dict, List, Optional, Tuple
import os
import csv
from dataclasses import dataclass
from enum import Enum

class WeatherCondition(Enum):
    SUNNY = "sunny"
    RAINY = "rainy"
    CLOUDY = "cloudy"
    HOT = "hot"

class LocationType(Enum):
    OFFICE_AREA = "office_area"
    RESIDENTIAL = "residential"
    MARKET = "market"
    TRANSPORT_HUB = "transport_hub"
    COLLEGE = "college"

@dataclass
class VendorProfile:
    name: str
    location: str
    location_type: LocationType
    items_sold: List[str]
    avg_daily_revenue: float
    peak_hours: List[int]

@dataclass
class DayContext:
    date: str
    day_of_week: str
    weather: WeatherCondition
    is_festival: bool
    is_payday: bool
    temperature: int

@dataclass
class PredictionOutput:
    recommended_items: Dict[str, int]
    expected_revenue: Tuple[int, int]
    peak_hours: List[int]
    special_notes: List[str]
    confidence_level: float

class SVDPAgent:
    def __init__(self, memory_file: str = "memory.json", prompts_file: str = "prompts/prompt_templates.txt"):
        self.memory_file = memory_file
        self.prompts_file = prompts_file
        self.memory = self._load_memory()
        self.prompt_templates = self._load_prompts()

    def _load_memory(self) -> Dict:
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"vendors": {}, "patterns": {}, "last_updated": ""}

    def _save_memory(self):
        def convert(obj):
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert(i) for i in obj]
            return obj

        self.memory["last_updated"] = datetime.datetime.now().isoformat()
        serializable_memory = convert(self.memory)
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_memory, f, indent=2, ensure_ascii=False)

    def _load_prompts(self) -> Dict[str, str]:
        try:
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                content = f.read()
                return {
                    "demand_analysis": content,
                    "inventory_optimization": "Optimize inventory based on Indian street vendor context",
                    "revenue_prediction": "Predict revenue in rupees and paise"
                }
        except FileNotFoundError:
            return self._get_default_prompts()

    def _get_default_prompts(self) -> Dict[str, str]:
        return {
            "demand_analysis": """
            Analyze demand for street vendor in India considering:
            - Local festivals and holidays
            - Weather patterns (monsoon, summer heat)
            - Payday cycles (salary days)
            - Regional food preferences
            - Price sensitivity (₹5-50 range typical)
            """,
            "inventory_optimization": """
            Suggest inventory in Indian context:
            - Think in small quantities (50-200 pieces)
            - Consider perishability in Indian climate
            - Account for ₹500-2000 daily investment capacity
            - Factor in local supplier availability
            """,
            "revenue_prediction": """
            Predict revenue in Indian rupees:
            - Daily range: ₹300-1500 typical for street vendors
            - Peak hours: 12-2pm (lunch), 6-9pm (evening snacks)
            - Weather impact: Rain reduces footfall by 60-80%
            - Festival days can boost sales by 200-400%
            """
        }

    
    # LAYER 1: INPUT PROCESSING
    def process_input(self, vendor_profile: VendorProfile, day_context: DayContext) -> Dict:
        """
        Layer 1: Process and normalize input data
        Converts real-world vendor context into structured data
        """
        processed_input = {
            "vendor_id": f"{vendor_profile.name}_{vendor_profile.location}".replace(" ", "_"),
            "location_factors": self._analyze_location_factors(vendor_profile.location_type),
            "weather_impact": self._calculate_weather_impact(day_context.weather, day_context.temperature),
            "time_factors": self._get_time_factors(day_context),
            "item_categories": self._categorize_items(vendor_profile.items_sold),
            "historical_context": self._get_historical_patterns(vendor_profile.name)
        }
        
        self._log_input_processing(processed_input)
        return processed_input
    
    def _analyze_location_factors(self, location_type: LocationType) -> Dict:
        """Analyze location-specific demand factors"""
        location_multipliers = {
            LocationType.OFFICE_AREA: {
                "lunch_demand": 1.5,
                "evening_snacks": 1.2,
                "price_tolerance": 1.3,
                "payday_boost": 1.8
            },
            LocationType.RESIDENTIAL: {
                "lunch_demand": 0.8,
                "evening_snacks": 1.4,
                "price_tolerance": 0.9,
                "weekend_boost": 1.6
            },
            LocationType.COLLEGE: {
                "lunch_demand": 1.8,
                "evening_snacks": 1.6,
                "price_tolerance": 0.7,
                "exam_period_drop": 0.4
            },
            LocationType.TRANSPORT_HUB: {
                "morning_rush": 1.9,
                "evening_rush": 1.7,
                "price_tolerance": 1.1,
                "weather_sensitivity": 1.4
            },
            LocationType.MARKET: {
                "all_day_steady": 1.2,
                "festival_boost": 2.5,
                "price_tolerance": 0.8,
                "competition_factor": 0.9
            }
        }
        return location_multipliers.get(location_type, {"default": 1.0})
    
    def _calculate_weather_impact(self, weather: WeatherCondition, temperature: int) -> Dict:
        """Calculate weather impact on sales"""
        base_impact = {
            WeatherCondition.SUNNY: 1.0,
            WeatherCondition.CLOUDY: 0.9,
            WeatherCondition.RAINY: 0.3,
            WeatherCondition.HOT: 0.7 if temperature > 35 else 0.8
        }
        
        # Temperature adjustments
        temp_factor = 1.0
        if temperature > 40:
            temp_factor = 0.5  # Extreme heat
        elif temperature > 35:
            temp_factor = 0.7  # Very hot
        elif temperature < 10:
            temp_factor = 0.6  # Too cold for street food
            
        return {
            "weather_multiplier": base_impact.get(weather, 1.0),
            "temperature_factor": temp_factor,
            "combined_impact": base_impact.get(weather, 1.0) * temp_factor
        }
    
    # LAYER 2: STATE MANAGEMENT  
    def update_state(self, processed_input: Dict, vendor_profile: VendorProfile) -> Dict:
        """
        Layer 2: Update agent state with new information
        Maintains context and learning from patterns
        """
        vendor_id = processed_input["vendor_id"]
        
        # Initialize vendor memory if new
        if vendor_id not in self.memory["vendors"]:
            self.memory["vendors"][vendor_id] = {
                "profile": vendor_profile.__dict__,
                "sales_history": [],
                "learned_patterns": {},
                "performance_metrics": {}
            }
        
        # Update state with current context
        current_state = {
            "vendor_memory": self.memory["vendors"][vendor_id],
            "processed_input": processed_input,
            "confidence_factors": self._calculate_confidence_factors(vendor_id, processed_input),
            "pattern_matches": self._find_pattern_matches(vendor_id, processed_input)
        }
        
        self._log_state_update(current_state)
        return current_state
    
    def _calculate_confidence_factors(self, vendor_id: str, processed_input: Dict) -> Dict:
        """Calculate prediction confidence based on available data"""
        vendor_data = self.memory["vendors"].get(vendor_id, {})
        history_length = len(vendor_data.get("sales_history", []))
        
        confidence_factors = {
            "historical_data": min(history_length / 30, 1.0),  # 30 days for full confidence
            "weather_data": 0.8,  # Assume good weather data
            "location_knowledge": 0.9,  # Good location understanding
            "seasonal_patterns": 0.6 if history_length < 90 else 0.9
        }
        
        return confidence_factors
    
    # LAYER 3: TASK EXECUTION
    def execute_prediction_task(self, current_state: Dict, day_context: DayContext) -> Dict:
        """
        Layer 3: Execute the core prediction task
        This is where the AI reasoning happens
        """
        # Extract relevant data
        vendor_memory = current_state["vendor_memory"]
        processed_input = current_state["processed_input"]
        
        # Core prediction logic
        demand_prediction = self._predict_item_demand(vendor_memory, processed_input, day_context)
        revenue_prediction = self._predict_revenue(vendor_memory, processed_input, day_context)
        timing_prediction = self._predict_optimal_timing(vendor_memory, processed_input, day_context)
        
        # Combine predictions
        task_result = {
            "item_demand": demand_prediction,
            "revenue_forecast": revenue_prediction,
            "timing_optimization": timing_prediction,
            "risk_factors": self._identify_risk_factors(processed_input, day_context),
            "opportunities": self._identify_opportunities(processed_input, day_context)
        }
        
        self._log_task_execution(task_result)
        return task_result
    
    def _predict_item_demand(self, vendor_memory: Dict, processed_input: Dict, day_context: DayContext) -> Dict:
        """Predict demand for specific items"""
        # Simplified demand prediction logic
        base_items = vendor_memory.get("profile", {}).get("items_sold", [])
        location_factors = processed_input["location_factors"]
        weather_impact = processed_input["weather_impact"]["combined_impact"]
        
        item_predictions = {}
        for item in base_items:
            # Base demand calculation
            base_demand = 50  # Base quantity
            
            # Apply location multipliers
            if "lunch_demand" in location_factors and "rice" in item.lower():
                base_demand *= location_factors["lunch_demand"]
            if "evening_snacks" in location_factors and any(snack in item.lower() for snack in ["samosa", "pakora", "chai"]):
                base_demand *= location_factors["evening_snacks"]
                
            # Apply weather impact
            base_demand *= weather_impact
            
            # Festival boost
            if day_context.is_festival:
                base_demand *= 1.5
                
            item_predictions[item] = max(int(base_demand), 10)  # Minimum 10 items
            
        return item_predictions
    
    def _predict_revenue(self, vendor_memory: Dict, processed_input: Dict, day_context: DayContext) -> Tuple[int, int]:
        """Predict revenue range in rupees"""
        profile = vendor_memory.get("profile", {})
        base_revenue = profile.get("avg_daily_revenue", 800)
        
        # Apply various factors
        location_impact = sum(processed_input["location_factors"].values()) / len(processed_input["location_factors"])
        weather_impact = processed_input["weather_impact"]["combined_impact"]
        
        adjusted_revenue = base_revenue * location_impact * weather_impact
        
        if day_context.is_festival:
            adjusted_revenue *= 1.8
        if day_context.is_payday:
            adjusted_revenue *= 1.3
            
        # Return range (min 80%, max 120% of prediction)
        min_revenue = int(adjusted_revenue * 0.8)
        max_revenue = int(adjusted_revenue * 1.2)
        
        return (min_revenue, max_revenue)
    
    # LAYER 4: OUTPUT GENERATION
    def generate_output(self, task_result: Dict, current_state: Dict) -> PredictionOutput:
        """
        Layer 4: Generate human-readable output
        Convert AI predictions into actionable vendor advice
        """
        confidence_factors = current_state["confidence_factors"]
        overall_confidence = sum(confidence_factors.values()) / len(confidence_factors)
        
        # Generate special notes
        special_notes = []
        if task_result["revenue_forecast"][0] < 300:
            special_notes.append("Low revenue day predicted - consider reducing inventory by 30%")
        if any("rain" in str(risk) for risk in task_result.get("risk_factors", [])):
            special_notes.append("Carry plastic covers for rain protection")
        if overall_confidence < 0.6:
            special_notes.append("Prediction confidence low - start with smaller inventory")
            
        # Create structured output
        output = PredictionOutput(
            recommended_items=task_result["item_demand"],
            expected_revenue=task_result["revenue_forecast"],
            peak_hours=task_result["timing_optimization"].get("peak_hours", [12, 13, 18, 19]),
            special_notes=special_notes,
            confidence_level=overall_confidence
        )
        
        self._log_output_generation(output)
        return output
    
    # HELPER METHODS
    def _get_time_factors(self, day_context: DayContext) -> Dict:
        """Extract time-based factors"""
        return {
            "day_of_week": day_context.day_of_week,
            "is_weekend": day_context.day_of_week in ["Saturday", "Sunday"],
            "is_festival": day_context.is_festival,
            "is_payday": day_context.is_payday
        }
    
    def _categorize_items(self, items: List[str]) -> Dict:
        """Categorize food items"""
        categories = {"main": [], "snacks": [], "beverages": []}
        for item in items:
            if any(main in item.lower() for main in ["rice", "roti", "dal", "curry"]):
                categories["main"].append(item)
            elif any(snack in item.lower() for snack in ["samosa", "pakora", "vada", "bhel"]):
                categories["snacks"].append(item)
            elif any(bev in item.lower() for bev in ["chai", "coffee", "lassi", "juice"]):
                categories["beverages"].append(item)
            else:
                categories["snacks"].append(item)  # Default to snacks
        return categories
    
    def _get_historical_patterns(self, vendor_name: str) -> Dict:
        """Get historical patterns for vendor"""
        # Simplified - in real implementation, this would analyze past data
        return {"patterns_found": 0, "confidence": 0.5}
    
    def _find_pattern_matches(self, vendor_id: str, processed_input: Dict) -> List:
        """Find matching patterns from historical data"""
        return []  # Simplified for prototype
    
    def _predict_optimal_timing(self, vendor_memory: Dict, processed_input: Dict, day_context: DayContext) -> Dict:
        """Predict optimal operating hours"""
        profile = vendor_memory.get("profile", {})
        base_peak_hours = profile.get("peak_hours", [12, 13, 18, 19])
        
        # Adjust based on location
        location_type = processed_input.get("location_factors", {})
        if "morning_rush" in location_type:
            base_peak_hours = [8, 9] + base_peak_hours
        if "evening_rush" in location_type:
            base_peak_hours = base_peak_hours + [20, 21]
            
        return {"peak_hours": base_peak_hours}
    
    def _identify_risk_factors(self, processed_input: Dict, day_context: DayContext) -> List[str]:
        """Identify potential risks"""
        risks = []
        if day_context.weather == WeatherCondition.RAINY:
            risks.append("Heavy rain may reduce customer footfall")
        if day_context.temperature > 40:
            risks.append("Extreme heat may affect food quality")
        return risks
    
    def _identify_opportunities(self, processed_input: Dict, day_context: DayContext) -> List[str]:
        """Identify potential opportunities"""
        opportunities = []
        if day_context.is_festival:
            opportunities.append("Festival day - consider special items and decorations")
        if day_context.is_payday:
            opportunities.append("Payday period - customers may spend more")
        return opportunities
    
    # LOGGING METHODS
    def _log_input_processing(self, processed_input: Dict):
        """Log input processing for debugging"""
        pass  # Implement logging as needed
    
    def _log_state_update(self, current_state: Dict):
        """Log state updates"""
        pass
    
    def _log_task_execution(self, task_result: Dict):
        """Log task execution"""
        pass
    
    def _log_output_generation(self, output: PredictionOutput):
        """Log output generation"""
        pass
    
    
    def _log_to_csv(self, vendor_profile: VendorProfile, day_context: DayContext, output: PredictionOutput):
        os.makedirs("logs", exist_ok=True)
        csv_file = os.path.join("logs", "predictions.csv")
        is_new_file = not os.path.exists(csv_file)
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if is_new_file:
                writer.writerow(["Date", "Vendor", "Location", "Items", "RevenueMin", "RevenueMax", "PeakHours", "Confidence"])
            items_str = "; ".join([f"{item}: {qty}" for item, qty in output.recommended_items.items()])
            writer.writerow([
                day_context.date,
                vendor_profile.name,
                vendor_profile.location,
                items_str,
                output.expected_revenue[0],
                output.expected_revenue[1],
                ", ".join(map(str, output.peak_hours)),
                f"{output.confidence_level:.2f}"
            ])


# MAIN PREDICTION METHOD
    def predict(self, vendor_profile: VendorProfile, day_context: DayContext) -> PredictionOutput:
        """
        Main prediction method - orchestrates all 4 layers
        """
        # Layer 1: Process Input
        processed_input = self.process_input(vendor_profile, day_context)
        
        # Layer 2: Update State
        current_state = self.update_state(processed_input, vendor_profile)
        
        # Layer 3: Execute Task
        task_result = self.execute_prediction_task(current_state, day_context)
        
        # Layer 4: Generate Output
        output = self.generate_output(task_result, current_state)
        
        # Save updated memory
        self._save_memory()
        
        return output

# Example usage
if __name__ == "__main__":
    # Create agent
    agent = SVDPAgent()
    
    # Example vendor profile
    vendor = VendorProfile(
        name="Raman Chai Wala",
        location="Connaught Place",
        location_type=LocationType.OFFICE_AREA,
        items_sold=["Chai", "Samosa", "Bread Pakora", "Biscuit"],
        avg_daily_revenue=650,
        peak_hours=[9, 12, 16, 18]
    )
    
    # Example day context
    today = DayContext(
        date="2025-06-17",
        day_of_week="Tuesday",
        weather=WeatherCondition.SUNNY,
        is_festival=False,
        is_payday=False,
        temperature=32
    )
    
    # Get prediction
    prediction = agent.predict(vendor, today)
    
    print(f"Prediction for {vendor.name}:")
    print(f"Recommended items: {prediction.recommended_items}")
    print(f"Expected revenue: ₹{prediction.expected_revenue[0]}-₹{prediction.expected_revenue[1]}")
    print(f"Peak hours: {prediction.peak_hours}")
    print(f"Confidence: {prediction.confidence_level:.2f}")
    print(f"Special notes: {prediction.special_notes}")
