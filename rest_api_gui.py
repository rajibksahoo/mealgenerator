import tkinter as tk
import requests


def call_api():
    meals_per_day = meals_per_day_entry.get()
    target_calories_per_day = target_calories_entry.get()
    target_protein_per_day = target_protein_entry.get()
    exclude_ingredients = exclude_ingredients_entry.get()
    meal_ids = meal_ids_entry.get()
    calories_variation = calories_variation_entry.get()

    # Check if any required field is empty
    if not (meals_per_day and target_calories_per_day and target_protein_per_day and meal_ids and calories_variation):
        response_text.delete(1.0, tk.END)
        response_text.insert(tk.END, "Please fill out all required fields.")
        return

    # Convert to int
    meals_per_day = int(meals_per_day)
    target_calories_per_day = int(target_calories_per_day)
    target_protein_per_day = int(target_protein_per_day)
    calories_variation = int(calories_variation)

    url = "http://127.0.0.1:5000/meal_plans"
    payload = {
        "meals_per_day": meals_per_day,
        "target_calories_per_day": target_calories_per_day,
        "target_protein_per_day": target_protein_per_day,
        "exclude_ingredients": exclude_ingredients,
        "meal_ids": meal_ids.split(','),
        "calories_variation": calories_variation
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        response_text.delete(1.0, tk.END)
        response_text.insert(tk.END, response.json())
    else:
        response_text.delete(1.0, tk.END)
        response_text.insert(tk.END, "Error: " + response.text)



root = tk.Tk()
root.title("REST API UI")

meals_per_day_label = tk.Label(root, text="Meals Per Day:")
meals_per_day_label.grid(row=0, column=0)
meals_per_day_entry = tk.Entry(root)
meals_per_day_entry.grid(row=0, column=1)

target_calories_label = tk.Label(root, text="Target Calories Per Day:")
target_calories_label.grid(row=1, column=0)
target_calories_entry = tk.Entry(root)
target_calories_entry.grid(row=1, column=1)

target_protein_label = tk.Label(root, text="Target Protein Per Day:")
target_protein_label.grid(row=2, column=0)
target_protein_entry = tk.Entry(root)
target_protein_entry.grid(row=2, column=1)

exclude_ingredients_label = tk.Label(root, text="Exclude Ingredients:")
exclude_ingredients_label.grid(row=3, column=0)
exclude_ingredients_entry = tk.Entry(root)
exclude_ingredients_entry.grid(row=3, column=1)

meal_ids_label = tk.Label(root, text="Meal IDs (comma-separated):")
meal_ids_label.grid(row=4, column=0)
meal_ids_entry = tk.Entry(root)
meal_ids_entry.grid(row=4, column=1)

calories_variation_label = tk.Label(root, text="Calories Variation:")
calories_variation_label.grid(row=5, column=0)
calories_variation_entry = tk.Entry(root)
calories_variation_entry.grid(row=5, column=1)

call_button = tk.Button(root, text="Call API", command=call_api)
call_button.grid(row=6, columnspan=2)

response_text = tk.Text(root, height=10, width=50)
response_text.grid(row=7, columnspan=2)

root.mainloop()
