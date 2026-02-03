"""
WHO & EU Air Quality Guidelines Knowledge Base for RAG
"""

KNOWLEDGE_BASE = {
    "pm10_guidelines": {
        "who_annual": "15 µg/m³ annual mean",
        "who_24h": "45 µg/m³ 24-hour mean",
        "eu_annual": "40 µg/m³ annual limit",
        "eu_24h": "50 µg/m³ not to exceed 35 times/year"
    },
    
    "health_categories": {
        "0-20": {
            "level": "Good",
            "color": "green",
            "advice": "Air quality is excellent. Perfect for all outdoor activities.",
            "activities": ["Running", "Cycling", "Hiking", "Outdoor sports", "Open windows"],
            "sensitive_groups": "No restrictions for anyone"
        },
        "20-40": {
            "level": "Moderate",
            "color": "yellow",
            "advice": "Air quality is acceptable for most. Unusually sensitive people should limit prolonged exposure.",
            "activities": ["Most outdoor activities OK", "Light exercise safe", "Moderate intensity OK"],
            "sensitive_groups": "Asthmatics: Keep rescue inhaler handy. Elderly: Monitor symptoms."
        },
        "40-50": {
            "level": "Moderate-Unhealthy",
            "color": "orange",
            "advice": "Sensitive groups may experience health effects. General public less likely to be affected.",
            "activities": ["Reduce prolonged outdoor exertion", "Short walks OK", "Indoor exercise preferred"],
            "sensitive_groups": "Children, elderly, asthmatics: Limit outdoor time to <2 hours"
        },
        "50-100": {
            "level": "Unhealthy",
            "color": "red",
            "advice": "Everyone may begin to experience health effects. Sensitive groups at greater risk.",
            "activities": ["Avoid prolonged outdoor exercise", "Essential trips only", "Keep windows closed"],
            "sensitive_groups": "Children, elderly, respiratory/heart conditions: Stay indoors. Use air purifiers."
        },
        "100+": {
            "level": "Very Unhealthy",
            "color": "purple",
            "advice": "Health alert: everyone may experience serious effects.",
            "activities": ["Stay indoors", "Avoid all outdoor activity", "Use air purifiers", "Wear N95 masks if must go out"],
            "sensitive_groups": "High-risk groups: Medical consultation advised. Monitor symptoms closely."
        }
    },
    
    "health_effects": {
        "short_term": [
            "Respiratory irritation",
            "Coughing and throat irritation",
            "Worsening of asthma symptoms",
            "Decreased lung function"
        ],
        "long_term": [
            "Chronic bronchitis",
            "Reduced lung growth in children",
            "Cardiovascular disease progression",
            "Premature mortality in vulnerable groups"
        ]
    },
    
    "vulnerable_groups": {
        "children": {
            "why_vulnerable": "Developing lungs, higher breathing rate, more outdoor time",
            "precautions": "Limit outdoor play when PM10 >40, indoor activities during high pollution"
        },
        "elderly": {
            "why_vulnerable": "Weakened immune system, pre-existing cardiovascular/respiratory conditions",
            "precautions": "Avoid outdoor exertion when PM10 >40, monitor symptoms closely"
        },
        "asthma": {
            "why_vulnerable": "Airways already inflamed, immediate trigger for attacks",
            "precautions": "Always carry rescue inhaler, use preventive medication, stay indoors when PM10 >50"
        },
        "heart_disease": {
            "why_vulnerable": "PM10 increases cardiovascular stress, blood pressure, clotting risk",
            "precautions": "Avoid all strenuous activity when PM10 >50, consult doctor if symptoms worsen"
        },
        "pregnant": {
            "why_vulnerable": "Fetal development risk, increased respiratory stress",
            "precautions": "Minimize exposure when PM10 >40, ensure adequate indoor air quality"
        }
    },
    
    "mitigation_strategies": {
        "indoor": [
            "Use HEPA air purifiers",
            "Keep windows closed during high pollution",
            "Avoid indoor smoking and strong chemicals",
            "Use exhaust fans while cooking",
            "Monitor indoor air quality"
        ],
        "outdoor": [
            "Check forecast before outdoor activities",
            "Schedule exercise during low-pollution hours (early morning/evening)",
            "Wear N95 masks if PM10 >50",
            "Avoid busy roads and traffic areas",
            "Stay hydrated to help body cope"
        ],
        "general": [
            "Install air quality monitoring apps",
            "Create a home air quality action plan",
            "Know your local air quality station",
            "Advocate for cleaner air policies",
            "Reduce personal pollution contributions (public transit, energy efficiency)"
        ]
    }
}


def get_health_category(pm10_value):
    """Get health category based on PM10 level"""
    if pm10_value < 20:
        return KNOWLEDGE_BASE["health_categories"]["0-20"]
    elif pm10_value < 40:
        return KNOWLEDGE_BASE["health_categories"]["20-40"]
    elif pm10_value < 50:
        return KNOWLEDGE_BASE["health_categories"]["40-50"]
    elif pm10_value < 100:
        return KNOWLEDGE_BASE["health_categories"]["50-100"]
    else:
        return KNOWLEDGE_BASE["health_categories"]["100+"]


def get_personalized_advice(pm10_forecast, user_profile="general"):
    """
    Generate personalized health advice based on PM10 forecast and user profile
    
    Args:
        pm10_forecast: Predicted PM10 level (µg/m³)
        user_profile: One of: general, children, elderly, asthma, heart_disease, pregnant
    
    Returns:
        Comprehensive health advice dictionary
    """
    category = get_health_category(pm10_forecast)
    
    advice = {
        "pm10_level": round(pm10_forecast, 1),
        "category": category["level"],
        "color": category["color"],
        "general_advice": category["advice"],
        "recommended_activities": category["activities"],
        "sensitive_groups_advice": category["sensitive_groups"]
    }
    
    # Add profile-specific guidance
    if user_profile in KNOWLEDGE_BASE["vulnerable_groups"]:
        profile_info = KNOWLEDGE_BASE["vulnerable_groups"][user_profile]
        advice["profile_specific"] = {
            "why_vulnerable": profile_info["why_vulnerable"],
            "precautions": profile_info["precautions"]
        }
    
    # Add mitigation strategies based on level
    if pm10_forecast >= 40:
        advice["mitigation"] = {
            "indoor": KNOWLEDGE_BASE["mitigation_strategies"]["indoor"][:3],
            "outdoor": KNOWLEDGE_BASE["mitigation_strategies"]["outdoor"][:3]
        }
    
    return advice
