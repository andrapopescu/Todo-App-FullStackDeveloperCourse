import sys

from flask import Flask, abort, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:postgres@localhost:5432/todoapp'
db = SQLAlchemy(app)


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'


db.create_all()


@app.route('/')
def index():
    data = Todo.query.all()
    return render_template('index.html', data=data)


@app.route('/todos/create/', methods=['POST'])
def create_todo_item():
    error = False
    body = {}
    try:
        description = request.get_json().get('description', '')
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exec_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify(body)
