
from flask import Flask, request, redirect
import sqlite3

app = Flask(__name__)
DB_NAME = "students.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll TEXT NOT NULL UNIQUE,
            course TEXT NOT NULL,
            email TEXT DEFAULT ''
        )
    """)

    # Add email column to an older database if it is missing.
    columns = [
        row["name"]
        for row in conn.execute("PRAGMA table_info(students)").fetchall()
    ]

    if "email" not in columns:
        conn.execute("ALTER TABLE students ADD COLUMN email TEXT DEFAULT ''")

    conn.commit()
    conn.close()


@app.route("/")
def home():
    conn = get_db()
    students = conn.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()
    conn.close()

    rows = ""
    for student in students:
        rows += f"""
        <tr>
            <td>{student['id']}</td>
            <td>{student['name']}</td>
            <td>{student['roll']}</td>
            <td>{student['course']}</td>
            <td>{student['email'] or ''}</td>
            <td>
                <form action="/delete/{student['id']}" method="post"
                      onsubmit="return confirm('Delete this student?')">
                    <button class="delete" type="submit">Delete</button>
                </form>
            </td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student Management System</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial; background: #f2f5fa; margin: 0; padding: 30px; }}
            .container {{ max-width: 1000px; margin: auto; }}
            h1 {{ color: #23395d; }}
            .card {{ background: white; padding: 22px; margin: 20px 0;
                     border-radius: 12px; box-shadow: 0 3px 12px #0001; }}
            input {{ padding: 10px; margin: 5px; border: 1px solid #ccc;
                     border-radius: 6px; }}
            button {{ padding: 10px 16px; border: 0; border-radius: 6px;
                      background: #246bfd; color: white; cursor: pointer; }}
            .delete {{ background: #d93025; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #eee; }}
            th {{ background: #edf2ff; }}
            .table-wrap {{ overflow-x: auto; }}
        </style>
    </head>
    <body>
    <div class="container">
        <h1>Student Management System</h1>

        <div class="card">
            <h2>Add New Student</h2>
            <form action="/add" method="post">
                <input name="name" placeholder="Student Name" required>
                <input name="roll" placeholder="Roll Number" required>
                <input name="course" placeholder="Course" required>
                <input name="email" type="email" placeholder="Email">
                <button type="submit">Add Student</button>
            </form>
        </div>

        <div class="card">
            <h2>Student Records</h2>
            <div class="table-wrap">
            <table>
                <tr>
                    <th>ID</th><th>Name</th><th>Roll No.</th>
                    <th>Course</th><th>Email</th><th>Action</th>
                </tr>
                {rows if rows else '<tr><td colspan="6">No students added yet.</td></tr>'}
            </table>
            </div>
        </div>
    </div>
    </body>
    </html>
    """


@app.route("/add", methods=["POST"])
def add_student():
    name = request.form["name"].strip()
    roll = request.form["roll"].strip()
    course = request.form["course"].strip()
    email = request.form.get("email", "").strip()

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO students (name, roll, course, email) VALUES (?, ?, ?, ?)",
            (name, roll, course, email)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return "That roll number already exists. Go back and use a unique roll number."
    finally:
        if conn:
            conn.close()

    return redirect("/")


@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
    return redirect("/")


if __name__ == "__main__":
    initialize_db()
    app.run(debug=True)
