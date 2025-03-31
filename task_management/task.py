from flask import Flask, render_template, request, redirect, url_for
import csv
import os

app = Flask(__name__)

CSV_FILE = "tasks.csv"
PRIORITY_ORDER = {"High": 1, "Medium": 2, "Low": 3}

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Description", "Priority", "Status"])

class Task:
    def __init__(self, title, description, priority, status="Pending"):
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status

    def mark_completed(self):
        self.status = "Completed"

    def update_priority(self, new_priority):
        self.priority = new_priority

    def to_dict(self):
        return {
            "Title": self.title,
            "Description": self.description,
            "Priority": self.priority,
            "Status": self.status
        }

def read_tasks():
    tasks = []
    with open(CSV_FILE, mode="r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            tasks.append(Task(row["Title"], row["Description"], row["Priority"], row["Status"]))
    return tasks

def write_tasks(tasks):
    with open(CSV_FILE, mode="w", newline="") as file:
        fieldnames = ["Title", "Description", "Priority", "Status"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for task in tasks:
            writer.writerow(task.to_dict())

@app.route("/")
def index():
    tasks = read_tasks()
    # sort tasks by priority 
    tasks.sort(key=lambda task: PRIORITY_ORDER.get(task.priority, 4))
    return render_template("index.html", tasks=tasks)

@app.route("/add_task", methods=["POST"])
def add_task():
    title = request.form.get("title")
    description = request.form.get("description")
    priority = request.form.get("priority")

    new_task = Task(title, description, priority)
    tasks = read_tasks()
    tasks.append(new_task)
    write_tasks(tasks)

    return redirect(url_for("index"))

@app.route("/mark_completed/<int:task_id>")
def mark_completed(task_id):
    tasks = read_tasks()
    if 0 <= task_id < len(tasks):
        tasks[task_id].mark_completed()
        write_tasks(tasks)
    return redirect(url_for("index"))

@app.route("/delete_task/<int:task_id>")
def delete_task(task_id):
    tasks = read_tasks()
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        write_tasks(tasks)
    return redirect(url_for("index"))

@app.route("/update_priority/<int:task_id>", methods=["POST"])
def update_priority(task_id):
    tasks = read_tasks()
    if 0 <= task_id < len(tasks):
        new_priority = request.form.get("new_priority")
        tasks[task_id].update_priority(new_priority)
        write_tasks(tasks)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)