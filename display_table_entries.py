from flaskblog import app, db  # Replace 'flaskblog' with your Flask application name
from flaskblog.models import User, Post, PasswordHistory  # Import your models
from tabulate import tabulate  # For displaying data in table format
from sqlalchemy.orm import class_mapper
import sys

# Function to fetch entries from a table
def fetch_table_entries(model):
    entries = model.query.all()
    if entries:
        # Get table headers dynamically
        headers = [column.key for column in class_mapper(model).columns]
        # Convert entries to list of lists for tabulate
        data = [[getattr(entry, column) for column in headers] for entry in entries]
        # Display data using tabulate
        print(tabulate(data, headers=headers, tablefmt="grid"))
        print("\n")
    else:
        print(f"No entries found in {model.__tablename__}.\n")

# Context manager to ensure proper application context
with app.app_context():
    print("Available tables:")
    print("1. User")
    print("2. Post")
    print("3. PasswordHistory")
    print("")

    table_names = {
        '1': User,
        '2': Post,
        '3': PasswordHistory,
    }

    tables_to_display = input("Enter the table numbers to display their entries (e.g., 1 2 3): ").strip().split()

    for table_number in tables_to_display:
        if table_number in table_names:
            fetch_table_entries(table_names[table_number])
        else:
            print(f"Invalid table number: {table_number}")
            sys.exit(1)
