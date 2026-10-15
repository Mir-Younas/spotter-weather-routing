RISK_SCORES = {
    "LOW": 0,
    "MODERATE": 25,
    "HIGH": 50,
    "SEVERE": 75,
    "NO_TRAVEL": 100,
}

RISK_PRIORITY = {
    "UNKNOWN": -1,
    "LOW": 0,
    "MODERATE": 1,
    "HIGH": 2,
    "SEVERE": 3,
    "NO_TRAVEL": 4,
}

MM_PER_INCH = 25.4
CM_PER_INCH = 2.54


def classify_wind(wind_mph):
    if wind_mph >= 55:
        return "NO_TRAVEL"
    if wind_mph >= 45:
        return "SEVERE"
    if wind_mph >= 35:
        return "HIGH"
    if wind_mph >= 25:
        return "MODERATE"
    return "LOW"


def classify_rain(rain_inches):
    if rain_inches > 1.0:
        return "NO_TRAVEL"
    if rain_inches >= 0.5:
        return "SEVERE"
    if rain_inches >= 0.25:
        return "HIGH"
    if rain_inches >= 0.10:
        return "MODERATE"
    return "LOW"


def classify_snow(snow_inches):
    if snow_inches > 3.0:
        return "NO_TRAVEL"
    if snow_inches >= 2.0:
        return "SEVERE"
    if snow_inches >= 1.0:
        return "HIGH"
    if snow_inches >= 0.5:
        return "MODERATE"
    return "LOW"


def calculate_weather_risk(weather, load_weight):
    if weather is None:
        return {
            "score": None,
            "level": "UNKNOWN",
            "hazards": ["Weather forecast unavailable"],
        }

    required_fields = [
        "wind_speed_mph",
        "wind_gusts_mph",
        "precipitation_mm",
        "snowfall_cm",
    ]

    if any(
        not isinstance(weather.get(field), (int, float))
        or isinstance(weather.get(field), bool)
        for field in required_fields
    ):
        return {
            "score": None,
            "level": "UNKNOWN",
            "hazards": ["Incomplete weather forecast"],
        }

    wind_speed = max(0, weather["wind_speed_mph"])
    wind_gusts = max(0, weather["wind_gusts_mph"])
    precipitation_mm = max(0, weather["precipitation_mm"])
    snowfall_cm = max(0, weather["snowfall_cm"])

    # Use the stronger of sustained wind and gusts.
    wind_mph = max(wind_speed, wind_gusts)

    # Open-Meteo provides precipitation in mm
    # and snowfall in cm. The assessment uses inches.
    rain_inches = precipitation_mm / MM_PER_INCH
    snow_inches = snowfall_cm / CM_PER_INCH

    wind_level = classify_wind(wind_mph)
    rain_level = classify_rain(rain_inches)
    snow_level = classify_snow(snow_inches)

    hazards = []

    if wind_level != "LOW":
        hazards.append(f"Wind: {wind_level} ({wind_mph:.1f} mph)")

    if rain_level != "LOW":
        hazards.append(f"Rain: {rain_level} ({rain_inches:.2f} in/hr)")

    if snow_level != "LOW":
        hazards.append(f"Snow: {snow_level} ({snow_inches:.2f} in/hr)")

    # Assessment-specific load rules.
    if wind_mph >= 55:
        wind_level = "NO_TRAVEL"
        hazards.append("No travel: wind is at least 55 mph")

    elif wind_mph >= 45 and load_weight > 30000:
        wind_level = "NO_TRAVEL"
        hazards.append("No travel: wind is at least 45 mph with load over 30,000 lb")

    elif wind_mph >= 35 and load_weight > 40000:
        if RISK_PRIORITY[wind_level] < RISK_PRIORITY["SEVERE"]:
            wind_level = "SEVERE"

        hazards.append(
            "Severe load risk: wind is at least 35 mph with load over 40,000 lb"
        )

    # The highest risk condition determines
    # the checkpoint classification.
    level = max(
        [wind_level, rain_level, snow_level],
        key=lambda value: RISK_PRIORITY[value],
    )

    return {
        "score": RISK_SCORES[level],
        "level": level,
        "hazards": hazards,
    }


def score_route_checkpoints(checkpoints, load_weight):
    valid_scores = []

    severe_miles = 0.0
    high_miles = 0.0
    no_travel_miles = 0.0
    unavailable_miles = 0.0

    for checkpoint in checkpoints:
        risk = calculate_weather_risk(
            checkpoint.get("weather"),
            load_weight,
        )

        checkpoint["risk_score"] = risk["score"]
        checkpoint["risk_level"] = risk["level"]
        checkpoint["hazards"] = risk["hazards"]

        if risk["score"] is not None:
            valid_scores.append(risk["score"])

    # Each checkpoint represents the road distance
    # halfway toward its neighboring checkpoints.
    for index, checkpoint in enumerate(checkpoints):
        current_mile = checkpoint["mile_marker"]

        previous_mile = (
            checkpoints[index - 1]["mile_marker"] if index > 0 else current_mile
        )

        next_mile = (
            checkpoints[index + 1]["mile_marker"]
            if index < len(checkpoints) - 1
            else current_mile
        )

        represented_miles = (current_mile - previous_mile) / 2 + (
            next_mile - current_mile
        ) / 2

        level = checkpoint["risk_level"]

        if level == "NO_TRAVEL":
            no_travel_miles += represented_miles
        elif level == "SEVERE":
            severe_miles += represented_miles
        elif level == "HIGH":
            high_miles += represented_miles
        elif level == "UNKNOWN":
            unavailable_miles += represented_miles

    total_checkpoints = len(checkpoints)
    evaluated_checkpoints = len(valid_scores)
    unavailable_checkpoints = total_checkpoints - evaluated_checkpoints

    if not valid_scores:
        return {
            "average_risk_score": None,
            "maximum_risk_score": None,
            "overall_risk_score": None,
            "overall_risk_level": "UNKNOWN",
            "severe_miles": round(severe_miles, 2),
            "high_miles": round(high_miles, 2),
            "no_travel_miles": round(no_travel_miles, 2),
            "unavailable_miles": round(unavailable_miles, 2),
            "total_checkpoints": total_checkpoints,
            "evaluated_checkpoints": evaluated_checkpoints,
            "unavailable_checkpoints": unavailable_checkpoints,
        }

    average_score = round(
        sum(valid_scores) / evaluated_checkpoints,
        2,
    )

    maximum_score = max(valid_scores)

    overall_score = round(
        average_score * 0.7 + maximum_score * 0.3,
        2,
    )

    levels = [
        checkpoint["risk_level"]
        for checkpoint in checkpoints
        if checkpoint["risk_level"] != "UNKNOWN"
    ]

    overall_level = max(
        levels,
        key=lambda value: RISK_PRIORITY[value],
    )

    if unavailable_checkpoints > 0:
        overall_level = "UNKNOWN"

    return {
        "average_risk_score": average_score,
        "maximum_risk_score": maximum_score,
        "overall_risk_score": overall_score,
        "overall_risk_level": overall_level,
        "severe_miles": round(severe_miles, 2),
        "high_miles": round(high_miles, 2),
        "no_travel_miles": round(no_travel_miles, 2),
        "unavailable_miles": round(unavailable_miles, 2),
        "total_checkpoints": total_checkpoints,
        "evaluated_checkpoints": evaluated_checkpoints,
        "unavailable_checkpoints": unavailable_checkpoints,
    }
