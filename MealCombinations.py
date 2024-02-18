import pandas as pd
import itertools
def filter_meals(meals_df, target_calories_per_day, target_protein_per_day,exclude_ingredients=None):
    # Filter meals based on calorie count
    meals_filtered = meals_df[meals_df['Calories'] <= target_calories_per_day]

    # Apply optional ingredient filters
    if exclude_ingredients and any(exclude_ingredients):
        for ingredient in exclude_ingredients:
            if ingredient:
                meals_filtered = meals_filtered[
                    ~meals_filtered['Ingredients'].str.contains(ingredient.strip(), case=False)]

    # Generate all possible combinations of meals
    valid_combinations = []
    for combo in itertools.combinations(meals_filtered.to_dict('records'), meals_per_day):
        total_calories = sum(meal['Calories'] for meal in combo)
        total_protein = sum(meal['Protein'] for meal in combo)
        if total_calories == target_calories_per_day and total_protein >= target_protein_per_day:
            valid_combinations.append((combo, total_calories, total_protein))

    return valid_combinations


# Read specific columns from the CSV file
meals_df = pd.read_csv('C:\\Users\\ADMIN\\Documents\\dummy_meals.csv',
                       usecols=['Name', 'Calories', 'Protein', 'Ingredients'])

# Get user input for meals per day, target calorie intake, target protein intake per day,
# and optional ingredient filters
while True:
    try:
        meals_per_day = int(input("Enter the number of meals per day (e.g., 3 or 4): "))
        target_calories_per_day = int(input("Enter the target total calorie intake per day: "))
        target_protein_per_day = float(input("Enter the target protein intake per day: "))
        exclude_ingredients = input("Enter ingredients to exclude (comma-separated, leave blank for none): ").split(',')
        break
    except ValueError:
        print("Invalid input. Please enter valid integers.")

# Filter meals and generate valid combinations
valid_combinations = filter_meals(meals_df, target_calories_per_day, target_protein_per_day,
                                  exclude_ingredients=exclude_ingredients)

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
