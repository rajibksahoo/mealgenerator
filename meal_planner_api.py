import logging
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import itertools
import configparser

app = Flask(__name__)

# Enable CORS for all origins (adjust for specific origins in production)
CORS(app)

# Read configuration from config.properties
config = configparser.ConfigParser()
config.read('config.properties')

# Read meals data from CSV
meals_df = pd.read_csv(config['paths']['meals_data_file_path'])

# Configure logging
logging.basicConfig(filename=config['logging']['filename'], level=int(config['logging']['level']),
                    format=config['logging']['format'])

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(config['logging']['format'])
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)


def log_input(data):
    for key, value in data.items():
        logging.info(f"Input {key}: {value} (Type: {type(value).__name__})")


def filter_meals(meals_df, target_calories_per_day, target_protein_per_day, meals_per_day, meal_ids=None,
                 exclude_ingredients=None, x=0):
    meal_ids_count = len(meal_ids) if meal_ids else 0
    meals_filtered = meals_df[meals_df['Calories'] <= target_calories_per_day]

    if exclude_ingredients and any(exclude_ingredients):
        for ingredient in exclude_ingredients:
            if ingredient:
                meals_filtered = meals_filtered[
                    ~meals_filtered['Ingredients'].str.contains(ingredient.strip(), case=False)]

    if meal_ids:
        remaining_meals_filtered = meals_filtered[~meals_filtered['Meal Id'].isin(meal_ids)]
    else:
        remaining_meals_filtered = meals_filtered.copy()

    valid_combinations = []

    combinations_remaining_meals = itertools.combinations(remaining_meals_filtered.to_dict('records'),
                                                          meals_per_day - meal_ids_count)

    for combo in combinations_remaining_meals:
        combo = list(combo) + [meal for meal in meals_df.to_dict('records') if meal['Meal Id'] in meal_ids]

        total_calories = sum(meal['Calories'] for meal in combo)
        total_protein = sum(meal['Protein'] for meal in combo)

        if (1 - x / 100) * target_calories_per_day <= total_calories <= (
                1 + x / 100) * target_calories_per_day and total_protein >= target_protein_per_day:
            valid_combinations.append((combo, total_calories, total_protein))

    return valid_combinations


@app.route('/meal_plans', methods=['POST'])
def get_meal_plans():
    data = request.json

    # Log input values and their types
    log_input(data)

    meals_per_day = data['meals_per_day']
    target_calories_per_day = data['target_calories_per_day']
    target_protein_per_day = data['target_protein_per_day']
    exclude_ingredients = data.get('exclude_ingredients', [])
    meal_ids = data.get('meal_ids', [])
    x = data.get('calories_variation', 0)

    valid_combinations = filter_meals(meals_df, target_calories_per_day, target_protein_per_day,
                                      meals_per_day, meal_ids=meal_ids, exclude_ingredients=exclude_ingredients, x=x)

    if valid_combinations:
        response = {
            "message": f"Valid meal plans for {meals_per_day} meals per day with at least {target_protein_per_day} grams of protein:",
            "meal_plans": []
        }
        for idx, (combo, total_calories, total_protein) in enumerate(valid_combinations, start=1):
            meal_plan = {
                "id": idx,
                "total_calories": total_calories,
                "total_protein": total_protein,
                "meals": [{
                    "Meal Id": meal['Meal Id'],
                    "Name": meal['Name'],
                    "Ingredients": meal['Ingredients'],
                    "Directions": meal['Directions'],
                    "Protein": meal['Protein'],
                    "Carbs": meal['Carbs'],
                    "Fat": meal['Fat'],
                    "Calories": meal['Calories'],
                    "Type": meal['Type']
                } for meal in combo]
            }
            response["meal_plans"].append(meal_plan)
        return jsonify(response), 200
    else:
        return jsonify({
            "message": f"No valid meal plans found for {meals_per_day} meals per day with at least {target_protein_per_day} grams of protein."}), 200


if __name__ == '__main__':
    app.run(debug=True)
