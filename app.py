from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# Create a connection to the SQLite database
conn = sqlite3.connect('tasks.db', check_same_thread=False)
cur = conn.cursor()

# Create tasks table if not exists
cur.execute('''CREATE TABLE IF NOT EXISTS tasks (
               id INTEGER PRIMARY KEY,
               name TEXT NOT NULL,
               description TEXT NOT NULL,
               status TEXT NOT NULL,
               category_id INTEGER NOT NULL,
               colleague_id INTEGER,
               FOREIGN KEY (category_id) REFERENCES categories(id),
               FOREIGN KEY (colleague_id) REFERENCES colleagues(id)
               )''')

# Create categories table if not exists
cur.execute('''CREATE TABLE IF NOT EXISTS categories (
               id INTEGER PRIMARY KEY,
               name TEXT NOT NULL
               )''')

# Create colleagues table if not exists
cur.execute('''CREATE TABLE IF NOT EXISTS colleagues (
               id INTEGER PRIMARY KEY,
               name TEXT NOT NULL
               )''')

# Populate categories table if it's empty
cur.execute("SELECT * FROM categories")
if not cur.fetchall():
    cur.execute("INSERT INTO categories (name) VALUES ('Project 1'), ('Project 2'), ('Project 3')")
    conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to add a new task
@app.route('/add_task', methods=['POST'])
def add_task():
    name = request.form['name']
    description = request.form['description']
    category_name = request.form['category_id']
    colleague_id = request.form.get('colleague_id')
    cur.execute("SELECT id FROM categories WHERE name=?", (category_name,))
    category_id = cur.fetchone()[0]
    cur.execute("INSERT INTO tasks (name, description, status, category_id, colleague_id) VALUES (?, ?, 'to-do', ?, ?)", (name, description, category_id, colleague_id))
    conn.commit()
    return jsonify({'message': 'Task added successfully'})

# Endpoint to retrieve all tasks with colleague names
@app.route('/get_tasks')
def get_tasks():
    cur.execute("SELECT tasks.id, tasks.name, tasks.description, tasks.status, categories.name, colleagues.name FROM tasks INNER JOIN categories ON tasks.category_id = categories.id LEFT JOIN colleagues ON tasks.colleague_id = colleagues.id")
    tasks = cur.fetchall()
    tasks_list = [{'id': task[0], 'name': task[1], 'description': task[2], 'status': task[3], 'category': task[4], 'with': task[5]} for task in tasks]
    return jsonify(tasks_list)

# Endpoint to delete a task
@app.route('/delete_task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    cur.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    return jsonify({'message': 'Task deleted successfully'})

# Endpoint to change task status
@app.route('/change_status/<int:task_id>/<status>', methods=['PUT'])
def change_status(task_id, status):
    cur.execute("UPDATE tasks SET status=? WHERE id=?", (status, task_id))
    conn.commit()
    return jsonify({'message': 'Task status changed successfully'})

# Endpoint to fetch categories from the database
@app.route('/get_categories', methods=['GET'])
def get_categories():
    cur.execute("SELECT id, name FROM categories")
    categories = cur.fetchall()
    categories = [{'id': row[0], 'name': row[1]} for row in categories]
    return jsonify(categories)

# Endpoint to fetch colleagues from the database
@app.route('/get_colleagues', methods=['GET'])
def get_colleagues():
    cur.execute("SELECT id, name FROM colleagues")
    colleagues = cur.fetchall()
    colleagues = [{'id': row[0], 'name': row[1]} for row in colleagues]
    return jsonify(colleagues)

# Endpoint to add a new colleague
@app.route('/add_colleague', methods=['POST'])
def add_colleague():
    name = request.form['name']
    cur.execute("INSERT INTO colleagues (name) VALUES (?)", (name,))
    conn.commit()
    return jsonify({'message': 'Colleague added successfully'})

# Endpoint to assign a task to a colleague
@app.route('/assign_employee/<int:task_id>/<int:colleague_id>', methods=['PUT'])
def assign_employee(task_id, colleague_id):
    cur.execute("UPDATE tasks SET colleague_id=? WHERE id=?", (colleague_id, task_id))
    conn.commit()
    return jsonify({'message': 'Employee assigned successfully'})

# Endpoint to add a new project
@app.route('/add_project', methods=['POST'])
def add_project():
    project_name = request.form['name']
    cur.execute("INSERT INTO categories (name) VALUES (?)", (project_name,))
    conn.commit()
    
    # Fetch updated categories data
    cur.execute("SELECT id, name FROM categories")
    categories = cur.fetchall()
    categories = [{'id': row[0], 'name': row[1]} for row in categories]
    
    return jsonify({'message': 'Project added successfully', 'categories': categories})

# Endpoint to rename a project
@app.route('/rename_project', methods=['POST'])
def rename_project():
    old_name = request.form['old_name']
    new_name = request.form['newName']
    cur.execute("UPDATE categories SET name=? WHERE name=?", (new_name, old_name))
    conn.commit()
    
    # Fetch updated categories data
    cur.execute("SELECT id, name FROM categories")
    categories = cur.fetchall()
    categories = [{'id': row[0], 'name': row[1]} for row in categories]
    
    return jsonify({'message': 'Project renamed successfully', 'categories': categories})

if __name__ == '__main__':
    app.run(debug=True)
