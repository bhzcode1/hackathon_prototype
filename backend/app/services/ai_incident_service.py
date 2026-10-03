"""
AI Incident Intelligence Service.

Provides analysis of incidents using a configurable LLM provider or a rule-based fallback.
"""
import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

# Define the structure of the AI analysis
class IncidentAIAnalysis:
    def __init__(self, summary: str, risk_explanation: str, key_factors: List[str],
                 recommended_actions: List[str], limitations: str, provider: str):
        self.summary = summary
        self.risk_explanation = risk_explanation
        self.key_factors = key_factors
        self.recommended_actions = recommended_actions
        self.limitations = limitations
        self.provider = provider

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "risk_explanation": self.risk_explanation,
            "key_factors": self.key_factors,
            "recommended_actions": self.recommended_actions,
            "limitations": self.limitations,
            "provider": self.provider
        }

class AIIncidentService:
    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "rule-based").lower()
        self.model = os.getenv("AI_MODEL", "")
        self.api_key = os.getenv("AI_API_KEY", "")
        # For now, we only implement rule-based. LLM integration can be added later.
        # We'll check if the API key is set for LLM providers, but we won't actually call without a key.
        if self.provider not in ["rule-based", "openai", "anthropic", "google"]:
            # Default to rule-based if an unknown provider is specified
            self.provider = "rule-based"

    def analyze_incident(self, incident: Dict[str, Any], risk_data: Optional[Dict[str, Any]] = None,
                         hotspot_data: Optional[Dict[str, Any]] = None,
                         environmental_data: Optional[Dict[str, Any]] = None) -> IncidentAIAnalysis:
        """
        Generate an analysis for the given incident.

        Args:
            incident: The incident dictionary from the store.
            risk_data: Optional risk zone data (from the risk zone service) for the incident location.
            hotspot_data: Optional hotspot data (from NASA FIRMS) that triggered the incident.
            environmental_data: Optional environmental data (temperature, humidity, etc.) for the incident.

        Returns:
            IncidentAIAnalysis object.
        """
        if self.provider == "rule-based":
            return self._rule_based_analysis(incident, risk_data, hotspot_data, environmental_data)
        else:
            # Attempt to use LLM if configured and API key is present
            try:
                if self.provider == "openai" and self.api_key:
                    return self._openai_analysis(incident, risk_data, hotspot_data, environmental_data)
                elif self.provider == "anthropic" and self.api_key:
                    return self._anthropic_analysis(incident, risk_data, hotspot_data, environmental_data)
                elif self.provider == "google" and self.api_key:
                    return self._google_analysis(incident, risk_data, hotspot_data, environmental_data)
            except Exception as e:
                # Fallback to rule-based on any error
                print(f"LLM analysis failed ({e}), falling back to rule-based.")
                return self._rule_based_analysis(incident, risk_data, hotspot_data, environmental_data)
            # If we get here, the provider was set but no API key or we didn't match above
            return self._rule_based_analysis(incident, risk_data, hotspot_data, environmental_data)

    def _rule_based_analysis(self, incident: Dict[str, Any], risk_data: Optional[Dict[str, Any]],
                             hotspot_data: Optional[Dict[str, Any]],
                             environmental_data: Optional[Dict[str, Any]]) -> IncidentAIAnalysis:
        """
        Generate a rule-based analysis when no LLM is available or configured.
        """
        summary = self._generate_summary(incident, risk_data, hotspot_data, environmental_data)
        risk_explanation = self._generate_risk_explanation(incident, risk_data, environmental_data)
        key_factors = self._generate_key_factors(incident, risk_data, hotspot_data, environmental_data)
        recommended_actions = self._generate_recommended_actions(incident, risk_data, hotspot_data)
        limitations = self._generate_limitations(incident, risk_data, hotspot_data, environmental_data)

        return IncidentAIAnalysis(
            summary=summary,
            risk_explanation=risk_explanation,
            key_factors=key_factors,
            recommended_actions=recommended_actions,
            limitations=limitations,
            provider="rule-based"
        )

    def _generate_summary(self, incident: Dict[str, Any], risk_data: Optional[Dict[str, Any]],
                          hotspot_data: Optional[Dict[str, Any]],
                          environmental_data: Optional[Dict[str, Any]]) -> str:
        severity = incident.get("severity", "UNKNOWN")
        region = incident.get("region", "Unknown region")
        source = incident.get("source", "Unknown source")
        risk_score = incident.get("risk_score", 0)

        if source == "NASA FIRMS":
            base = f"A {severity} fire hotspot was detected via satellite in the {region}."
        else:
            base = f"A {severity} fire risk was predicted by the FireSight ML model in the {region}."

        if risk_score is not None:
            base += f" The predicted risk score is {risk_score}/100."
        else:
            base += " Risk score data is not available."

        return base

    def _generate_risk_explanation(self, incident: Dict[str, Any], risk_data: Optional[Dict[str, Any]],
                                   environmental_data: Optional[Dict[str, Any]]) -> str:
        explanation_parts = []

        if environmental_data:
            temp = environmental_data.get("temperature")
            hum = environmental_data.get("humidity")
            wind = environmental_data.get("wind_speed")
            rain = environmental_data.get("rainfall")

            if temp is not None:
                explanation_parts.append(f"temperature of {temp}°C")
            if hum is not None:
                explanation_parts.append(f"humidity of {hum}%")
            if wind is not None:
                explanation_parts.append(f"wind speed of {wind} km/h")
            if rain is not None:
                explanation_parts.append(f"rainfall of {rain} mm")

        if explanation_parts:
            env_str = ", ".join(explanation_parts)
            explanation = f"Environmental conditions contributing to the risk include {env_str}."
        else:
            explanation = "Detailed environmental data is not available for this incident."

        # Add risk score context
        risk_score = incident.get("risk_score")
        if risk_score is not None:
            if risk_score >= 80:
                explanation += " The risk score is in the critical range (80-100)."
            elif risk_score >= 60:
                explanation += " The risk score is in the high range (60-79)."
            elif risk_score >= 30:
                explanation += " The risk score is in the medium range (30-59)."
            else:
                explanation += " The risk score is in the low range (0-29)."

        return explanation

    def _generate_key_factors(self, incident: Dict[str, Any], risk_data: Optional[Dict[str, Any]],
                              hotspot_data: Optional[Dict[str, Any]],
                              environmental_data: Optional[Dict[str, Any]]) -> List[str]:
        factors = []

        # From incident
        severity = incident.get("severity")
        if severity:
            factors.append(f"Incident severity: {severity}")

        risk_score = incident.get("risk_score")
        if risk_score is not None:
            factors.append(f"Fire risk score: {risk_score}/100")

        # From environmental data
        if environmental_data:
            for label, key, unit in [("temperature", "temperature", "°C"),
                                     ("humidity", "humidity", "%"),
                                     ("wind_speed", "wind_speed", "km/h"),
                                     ("rainfall", "rainfall", "mm")]:
                val = environmental_data.get(key)
                if val is not None:
                    factors.append(f"{label.capitalize()}: {val}{unit}")

        # From hotspot data (if available)
        if hotspot_data:
            confidence = hotspot_data.get("confidence")
            if confidence is not None:
                factors.append(f"Satellite hotspot confidence: {confidence}%")
            frp = hotspot_data.get("frp")
            if frp is not None:
                factors.append(f"Fire Radiative Power (FRP): {frp} MW")

        # From risk data (if available)
        if risk_data:
            # We already have risk_score from incident, but we can add vegetation index, etc. if present
            veg = risk_data.get("vegetation_index")
            if veg is not None:
                factors.append(f"Vegetation index: {veg}")
            fuel = risk_data.get("fuel_moisture")
            if fuel is not None:
                factors.append(f"Fuel moisture: {fuel}")

        # If we have no factors, add a placeholder
        if not factors:
            factors.append("Limited data available for detailed factor analysis.")

        return factors

    def _generate_recommended_actions(self, incident: Dict[str, Any],
                                      risk_data: Optional[Dict[str, Any]],
                                      hotspot_data: Optional[Dict[str, Any]]) -> List[str]:
        actions = []
        severity = incident.get("severity", "").upper()
        source = incident.get("source", "")

        # Base actions based on severity
        if severity == "CRITICAL":
            actions.append("Immediately verify the hotspot or prediction with field teams or additional satellite passes.")
            actions.append("Consider deploying firefighting resources to the area if safe to do so.")
            actions.append("Issue alerts to nearby communities and emergency services.")
        elif severity == "HIGH":
            actions.append("Prioritize field verification of the hotspot or prediction.")
            actions.append("Monitor the area closely for changes in risk level.")
            actions.append("Prepare firefighting resources for potential deployment.")
        elif severity == "MEDIUM":
            actions.append("Schedule a field assessment within the next 24 hours.")
            actions.append("Continue monitoring via satellite and ground observers.")
        else:  # LOW or unknown
            actions.append("Continue routine monitoring.")
            actions.append("No immediate action required based on current data.")

        # Add source-specific actions
        if source == "NASA FIRMS":
            actions.append("Cross-reference with other satellite sources (e.g., MODIS) for confirmation.")
        else:
            actions.append("Validate the ML prediction with recent weather and vegetation data.")

        # If we have hotspot data, suggest checking FRP trend
        if hotspot_data:
            frp = hotspot_data.get("frp")
            if frp is not None and frp > 100:  # arbitrary threshold for high FRP
                actions.append("The high FRP suggests significant heat output; consider aerial reconnaissance.")

        return actions

    def _generate_limitations(self, incident: Dict[str, Any], risk_data: Optional[Dict[str, Any]],
                              hotspot_data: Optional[Dict[str, Any]],
                              environmental_data: Optional[Dict[str, Any]]) -> str:
        limitations = []

        if not environmental_data:
            limitations.append("Real-time environmental data (temperature, humidity, wind, rainfall) is not available for this analysis.")
        else:
            missing = []
            for label in ["temperature", "humidity", "wind_speed", "rainfall"]:
                if environmental_data.get(label) is None:
                    missing.append(label)
            if missing:
                limitations.append(f"Missing environmental data: {', '.join(missing)}.")

        if not hotspot_data and incident.get("source") == "NASA FIRMS":
            limitations.append("Associated NASA FIRMS hotspot data could not be retrieved for detailed analysis.")
        elif hotspot_data:
            if hotspot_data.get("confidence") is None:
                limitations.append("Hotspot confidence value is not available.")
            if hotspot_data.get("frp") is None:
                limitations.append("Fire Radiative Power (FRP) is not available.")

        if not risk_data:
            limitations.append("Risk zone environmental data (vegetation index, fuel moisture, etc.) is not available.")
        else:
            if risk_data.get("vegetation_index") is None:
                limitations.append("Vegetation index data is not available.")
            if risk_data.get("fuel_moisture") is None:
                limitations.append("Fuel moisture data is not available.")

        limitations.append("This analysis is decision-support only and does not replace professional judgment or official emergency assessments.")
        limitations.append("The AI model does not predict fire spread, intensity, or impact on structures or ecosystems.")

        if not limitations:
            limitations = ["No specific limitations identified based on available data."]

        return " ".join(limitations)

    # Stub methods for LLM providers - to be implemented if API keys are present
    def _openai_analysis(self, incident: Dict[str, Any], risk_data: Optional[Dict[str, Any]],
                         hotspot_data: Optional[Dict[str, Any]],
                         environmental_data: Optional[Dict[str, Any]]) -> IncidentAIAnalysis:
        # Placeholder: In a real implementation, we would call the OpenAI API.
        # For now, we fall back to rule-based to avoid making actual calls without a key.
        # But if we have a key, we could attempt a call. We'll simulate by falling back for safety.
        # In a production setting, we would implement the call here.
        print("OpenAI API key detected but LLM call not implemented; using rule-based fallback.")
        return self._rule_based_analysis(incident, risk_data, hotspot_data, environmental_data)

    def _anthropic_analysis(self, incident: Dict[str, Any], risk_data: Optional[Dict[str, Any]],
                            hotspot_data: Optional[Dict[str, Any]],
                            environmental_data: Optional[Dict[str, Any]]) -> IncidentAIAnalysis:
        print("Anthropic API key detected but LLM call not implemented; using rule-based fallback.")
        return self._rule_based_analysis(incident, risk_data, hotspot_data, environmental_data)

    def _google_analysis(self, incident: Dict[str, Any], risk_data: Optional[Dict[str, Any]],
                         hotspot_data: Optional[Dict[str, Any]],
                         environmental_data: Optional[Dict[str, Any]]) -> IncidentAIAnalysis:
        print("Google API key detected but LLM call not implemented; using rule-based fallback.")
        return self._rule_based_analysis(incident, risk_data, hotspot_data, environmental_data)