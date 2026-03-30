
from flask import Flask, render_template, request 
import os 
import re

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_ai_meal(diet, age, height, weight, goal):
    prompt = f"""
    Create a 7-day {diet} Indian meal plan.

    User details:
    - Age: {age}
    - Weight: {weight}
    - Height: {height}
    - Goal: {goal}

    For EACH meal include:
    - Dish name
    - Short description
    - Estimated calories (in kcal)

    Format EXACTLY like:

    ### Day 1
    Breakfast: Oats Upma (250 kcal)
    Lunch: Dal Rice (400 kcal)
    Dinner: Paneer Sabzi (450 kcal)
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user","content": prompt}]
    )
    return response.choices[0].message.content

def get_calories(text):
    match = re.search(r'(\d+)', text)
    return int(match.group(1)) if match else 0
app= Flask(__name__, template_folder='templates')

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    diet = request.form['diet']
    age = request.form.get('age')
    weight = request.form.get('weight')
    height = request.form.get('height')
    goal = request.form.get('goal')

    ai_text = generate_ai_meal(diet, age, height, weight, goal)

    formatted_plan = format_meal_plan(ai_text)

    print("FORMATTED:", formatted_plan)  # debug

    return render_template("result.html", plan=formatted_plan)

def format_meal_plan(text):
    structured = []

    # Split using regex (safer)
    days = re.split(r"### Day \d+", text)[1:]

    day_numbers = re.findall(r"### Day (\d+)", text)

    for i, day in enumerate(days):
        lines = day.strip().split("\n")

        meals = {
            "breakfast": "",
            "lunch": "",
            "dinner": "",
            "total": 0
        }

        for line in lines:
            line = line.strip()

            if "Breakfast" in line:
                meals["breakfast"] = line.split(":",1)[-1].strip()
                meals["total"] += get_calories(line)

            elif "Lunch" in line:
                meals["lunch"] = line.split(":",1)[-1].strip()
                meals["total"] += get_calories(line)

            elif "Dinner" in line:
                meals["dinner"] = line.split(":",1)[-1].strip()
                meals["total"] += get_calories(line)

        structured.append({
            "day": day_numbers[i] if i < len(day_numbers) else i+1,
            "meals": meals
        })

    return structured

if __name__ == "__main__":
    app.run(debug=True)
    