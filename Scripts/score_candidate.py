"""ApplyPilot candidate scoring.

Reads one JSON object from  describing a candidate, prints one JSON
object to stdout with the score and priority. No external libraries and
no extra console output, so UiPath can call this and read stdout directly.

Run it by hand for testing, for example:
    echo {"skills": "Python, SQL", "education": "Diploma", "experienceYears": 2} | python score_candidate.py
"""
import sys
import json

MAX_SCORE = 100

# Points awarded per skill if it appears anywhere in the detected skills text.
PYTHON_POINTS = 25
JAVA_POINTS = 20
SQL_POINTS = 20

# A degree and a diploma are never both counted - a degree is the higher
# qualification, so it takes priority when both words appear.
DEGREE_POINTS = 20
DIPLOMA_POINTS = 10
DEGREE_KEYWORDS = ["bachelor", "degree", "bsc", "b.sc", "master"]
DIPLOMA_KEYWORDS = ["diploma"]

# Experience adds 3 points per year, capped so it cannot dominate the score.
POINTS_PER_YEAR = 3
MAX_EXPERIENCE_POINTS = 15

# Used only when the caller does not supply its own thresholds, so this
# script can still be tested on its own without UiPath.
DEFAULT_HIGH_THRESHOLD = 70
DEFAULT_MEDIUM_THRESHOLD = 40


def score_candidate(skills_text, education_text, experience_years):
    """Returns (score, breakdown_dict) for one candidate."""
    skills_text = (skills_text or "").lower()
    education_text = (education_text or "").lower()

    try:
        experience_years = int(experience_years)
    except (TypeError, ValueError):
        experience_years = 0
    if experience_years < 0:
        experience_years = 0

    python_score = PYTHON_POINTS if "python" in skills_text else 0
    java_score = JAVA_POINTS if "java" in skills_text else 0
    sql_score = SQL_POINTS if "sql" in skills_text else 0

    if any(word in education_text for word in DEGREE_KEYWORDS):
        education_score = DEGREE_POINTS
    elif any(word in education_text for word in DIPLOMA_KEYWORDS):
        education_score = DIPLOMA_POINTS
    else:
        education_score = 0

    experience_score = min(experience_years * POINTS_PER_YEAR, MAX_EXPERIENCE_POINTS)

    total = python_score + java_score + sql_score + education_score + experience_score
    total = min(total, MAX_SCORE)

    breakdown = {
        "python": python_score,
        "java": java_score,
        "sql": sql_score,
        "education": education_score,
        "experience": experience_score,
    }
    return total, breakdown


def priority_for_score(score, high_threshold, medium_threshold):
    if score >= high_threshold:
        return "High"
    if score >= medium_threshold:
        return "Medium"
    return "Low"


def main():
    raw_input_text = sys.stdin.read()
    try:
        data = json.loads(raw_input_text) if raw_input_text.strip() else {}
    except json.JSONDecodeError:
        # Malformed input should not crash the script - UiPath will see a
        # valid, safe result and can flag it based on scoreError instead.
        print(json.dumps({"score": 0, "priority": "Low", "breakdown": {}, "scoreError": "Invalid JSON input"}))
        return

    skills_text = data.get("skills", "")
    education_text = data.get("education", "")
    experience_years = data.get("experienceYears", 0)
    high_threshold = data.get("highThreshold", DEFAULT_HIGH_THRESHOLD)
    medium_threshold = data.get("mediumThreshold", DEFAULT_MEDIUM_THRESHOLD)

    score, breakdown = score_candidate(skills_text, education_text, experience_years)
    priority = priority_for_score(score, high_threshold, medium_threshold)

    print(json.dumps({"score": score, "priority": priority, "breakdown": breakdown, "scoreError": ""}))


if __name__ == "__main__":
    main()
