import pandas as pd
import itertools


def filter_meals(meals_df, target_calories_per_day, target_protein_per_day, meal_ids=None, exclude_ingredients=None,
                 x=0):
    # count of meals to be included in our final output
    meal_ids_count = len(meal_ids) if meal_ids else 0

    # Filter meals based on calorie count
    meals_filtered = meals_df[meals_df['Calories'] <= target_calories_per_day]

    # Apply optional ingredient filters
    if exclude_ingredients and any(exclude_ingredients):
        for ingredient in exclude_ingredients:
            if ingredient:
                meals_filtered = meals_filtered[
                    ~meals_filtered['Ingredients'].str.contains(ingredient.strip(), case=False)]

    # remaining meals from filtered meals
    if meal_ids:
        remaining_meals_filtered = meals_filtered[~meals_filtered['Meal Id'].isin(meal_ids)]
    else:
        remaining_meals_filtered = meals_filtered.copy()

    valid_combinations = []

    # Generate all possible combinations of meals
    combinations_remaining_meals = itertools.combinations(remaining_meals_filtered.to_dict('records'),
                                                          meals_per_day - meal_ids_count)

    for combo in combinations_remaining_meals:
        # Ensure that all meals from meal_ids are included in the combination
        combo = list(combo) + [meal for meal in meals_df.to_dict('records') if meal['Meal Id'] in meal_ids]

        total_calories = sum(meal['Calories'] for meal in combo)
        total_protein = sum(meal['Protein'] for meal in combo)

        # Check if total calories fall within the range of ±x%
        if (1 - x / 100) * target_calories_per_day <= total_calories <= (
                1 + x / 100) * target_calories_per_day and total_protein >= target_protein_per_day:
            valid_combinations.append((combo, total_calories, total_protein))

    return valid_combinations


# Read specific columns from the CSV file
meals_df = pd.read_csv('C:\\Users\\ADMIN\\Documents\\dummy_meals.csv',
                       usecols=['Meal Id', 'Name', 'Calories', 'Protein', 'Ingredients'])

# Get user input for meals per day, target calorie intake, target protein intake per day,
# optional ingredient filters, and specific meal IDs
while True:
    try:
        meals_per_day = int(input("Enter the number of meals per day (e.g., 3 or 4): "))
        target_calories_per_day = int(input("Enter the target total calorie intake per day: "))
        calories_variation_input = input("Enter the % variation allowed for total calories :  ")
        x = int(calories_variation_input) if calories_variation_input.strip() else 0
        target_protein_input = input("Enter the target protein intake per day (leave blank for 0): ")
        target_protein_per_day = float(target_protein_input) if target_protein_input.strip() else 0.0
        exclude_ingredients = input("Enter ingredients to exclude (comma-separated, leave blank for none): ").split(',')
        meal_ids = input("Enter list of meal IDs to include (comma-separated, leave blank for none): ").split(',')
        meal_ids = [(meal_id.strip()) for meal_id in meal_ids if meal_id.strip()]
        break
    except ValueError:
        print("Invalid input. Please enter valid integers or floats.")

# Filter meals and generate valid combinations
valid_combinations = filter_meals(meals_df, target_calories_per_day, target_protein_per_day,
                                  meal_ids=meal_ids, exclude_ingredients=exclude_ingredients, x=x)

# Print the valid meal plans
if valid_combinations:
    print(
        f"Valid meal plans for {meals_per_day} meals per day with at least {target_protein_per_day} grams of protein:")
    for idx, (combo, total_calories, total_protein) in enumerate(valid_combinations, start=1):
        print(f"Meal Plan {idx}:")
        print(f"Total Calories: {total_calories}, Total Protein: {total_protein}")
        for meal in combo:
            print(f"- {meal['Name']} ({meal['Calories']} calories, {meal['Protein']} grams of protein)")
        print()
else:
    print(
        f"No valid meal plans found for {meals_per_day} meals per day with at least {target_protein_per_day} grams of protein.")
