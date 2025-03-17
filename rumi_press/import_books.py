import os
import django
import pandas as pd
from datetime import datetime

# ✅ Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rumi_press.settings')
django.setup()

from books.models import Book, Category

# ✅ Load the spreadsheet
file_path = r"C:\Users\gurug\Documents\Python Projects\Expense Tracker\Books Distribution Expenses.xlsx"
df = pd.read_excel(file_path, sheet_name="Books")

# ✅ Iterate over each row and insert into database
for index, row in df.iterrows():
    # Get or create category
    category_name = row['category']
    category, _ = Category.objects.get_or_create(name=category_name)

    # ✅ Convert 'published_date' to datetime safely
    if pd.isnull(row['published_date']) or row['published_date'] == "":
        pub_date = None  # Handle missing dates
    else:
        try:
            pub_date = pd.to_datetime(row['published_date']).date()
        except Exception as e:
            print(f"⚠️ Skipping invalid date: {row['published_date']} (Error: {e})")
            pub_date = None  # Skip invalid dates

    # ✅ Create book entry
    Book.objects.create(
        title=row['title'],
        author=row['authors'],
        publishing_date=pub_date,
        category=category,
        distribution_expense=row['distribution_expense']
    )

print("✅ Data import complete!")
