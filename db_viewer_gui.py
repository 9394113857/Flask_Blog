import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import os

# -------------------------------------------------
# DB PATH (Flask-Migrate authoritative DB)
# -------------------------------------------------
DB_PATH = os.path.join("instance", "site.db")

if not os.path.exists(DB_PATH):
    messagebox.showerror(
        "Database Not Found",
        f"Database not found at:\n{DB_PATH}\n\n"
        "Run `flask db upgrade` first."
    )
    raise SystemExit


# -------------------------------------------------
# DATABASE HELPERS (READ-ONLY)
# -------------------------------------------------
def get_tables():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        ORDER BY name;
    """)
    tables = [r[0] for r in cur.fetchall()]
    conn.close()
    return tables


def get_table_data(table):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(f"PRAGMA table_info({table});")
    columns = [c[1] for c in cur.fetchall()]

    cur.execute(f"SELECT * FROM {table};")
    rows = cur.fetchall()

    conn.close()
    return columns, rows


def get_alembic_version():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("SELECT version_num FROM alembic_version;")
        row = cur.fetchone()
        return row[0] if row else "Unknown"
    except:
        return "Not migrated"
    finally:
        conn.close()


# -------------------------------------------------
# GUI ACTIONS
# -------------------------------------------------
def load_table():
    table = table_listbox.get(tk.ACTIVE)
    if not table:
        return

    tree.delete(*tree.get_children())

    columns, rows = get_table_data(table)
    tree["columns"] = columns
    tree["show"] = "headings"

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor="center")

    for row in rows:
        tree.insert("", tk.END, values=row)


# -------------------------------------------------
# MAIN WINDOW
# -------------------------------------------------
root = tk.Tk()
alembic_ver = get_alembic_version()
root.title(f"Flask DB Viewer | Migration: {alembic_ver}")
root.geometry("1000x550")
root.configure(bg="#1e1e1e")

# -------------------------------------------------
# STYLES
# -------------------------------------------------
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

# -------------------------------------------------
# LEFT PANEL
# -------------------------------------------------
left = tk.Frame(root, bg="#252526", width=240)
left.pack(side=tk.LEFT, fill=tk.Y)

tk.Label(
    left,
    text="Tables (Alembic)",
    bg="#252526",
    fg="white",
    font=("Segoe UI", 12, "bold"),
).pack(pady=10)

table_listbox = tk.Listbox(
    left,
    bg="#1e1e1e",
    fg="white",
    selectbackground="#007acc",
    font=("Segoe UI", 10),
)
table_listbox.pack(fill=tk.BOTH, expand=True, padx=10)

for t in get_tables():
    table_listbox.insert(tk.END, t)

tk.Button(
    left,
    text="Load Table",
    command=load_table,
    bg="#007acc",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    relief=tk.FLAT,
).pack(pady=12)

# -------------------------------------------------
# RIGHT PANEL
# -------------------------------------------------
right = tk.Frame(root, bg="#1e1e1e")
right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

tree = ttk.Treeview(right)
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

scroll = ttk.Scrollbar(right, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scroll.set)
scroll.pack(side=tk.RIGHT, fill=tk.Y)

# -------------------------------------------------
# RUN
# -------------------------------------------------
root.mainloop()
