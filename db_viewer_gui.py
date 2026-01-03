import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import os

# ----------------------------------
# Correct DB path (Flask instance DB)
# ----------------------------------
DB_PATH = os.path.join("instance", "site.db")

if not os.path.exists(DB_PATH):
    messagebox.showerror(
        "Database Not Found",
        f"Database not found at:\n{DB_PATH}"
    )
    raise SystemExit


# ----------------------------------
# Database helpers
# ----------------------------------
def get_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables


def get_table_data(table_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [col[1] for col in cursor.fetchall()]

    cursor.execute(f"SELECT * FROM {table_name};")
    rows = cursor.fetchall()

    conn.close()
    return columns, rows


# ----------------------------------
# GUI actions
# ----------------------------------
def load_table():
    selected = table_listbox.get(tk.ACTIVE)
    if not selected:
        messagebox.showwarning("No Selection", "Please select a table")
        return

    tree.delete(*tree.get_children())

    columns, rows = get_table_data(selected)

    tree["columns"] = columns
    tree["show"] = "headings"

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor="center")

    for row in rows:
        tree.insert("", tk.END, values=row)


# ----------------------------------
# Main window
# ----------------------------------
root = tk.Tk()
root.title("Flask SQLite DB Viewer")
root.geometry("950x520")
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use("default")

style.configure(
    "Treeview",
    background="#2b2b2b",
    foreground="white",
    rowheight=28,
    fieldbackground="#2b2b2b",
)
style.map("Treeview", background=[("selected", "#007acc")])

style.configure(
    "Treeview.Heading",
    background="#3c3f41",
    foreground="white",
    font=("Segoe UI", 10, "bold"),
)

# ----------------------------------
# Left panel (Tables)
# ----------------------------------
left_frame = tk.Frame(root, bg="#252526", width=220)
left_frame.pack(side=tk.LEFT, fill=tk.Y)

tk.Label(
    left_frame,
    text="Tables",
    bg="#252526",
    fg="white",
    font=("Segoe UI", 12, "bold"),
).pack(pady=10)

table_listbox = tk.Listbox(
    left_frame,
    bg="#1e1e1e",
    fg="white",
    selectbackground="#007acc",
    font=("Segoe UI", 10),
)
table_listbox.pack(fill=tk.BOTH, expand=True, padx=10)

tables = get_tables()
if not tables:
    table_listbox.insert(tk.END, "No tables found")
else:
    for table in tables:
        table_listbox.insert(tk.END, table)

tk.Button(
    left_frame,
    text="Load Table",
    command=load_table,
    bg="#007acc",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    relief=tk.FLAT,
).pack(pady=12)

# ----------------------------------
# Right panel (Data)
# ----------------------------------
right_frame = tk.Frame(root, bg="#1e1e1e")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

tree = ttk.Treeview(right_frame)
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# ----------------------------------
# Run app
# ----------------------------------
root.mainloop()
