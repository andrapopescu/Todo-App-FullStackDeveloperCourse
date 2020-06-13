import functools
import sys

from flask import Flask, abort, jsonify, redirect, render_template, request, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:postgres@localhost:5432/todoapp'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description} (completed: {self.completed})>'


class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='list', cascade='all, delete-orphan', lazy=True)

    @property
    def completed(self):
        return all(todo.completed for todo in self.todos)


@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))


@app.route('/lists/<list_id>/')
def get_list_todos(list_id):
    return render_template(
        'index.html',
        lists=TodoList.query.all(),
        active_list=TodoList.query.get(list_id),
        todos=Todo.query.filter_by(list_id=list_id).order_by('id').all(),
    )


def error_handling_decorator(**kwargs):
    def error_handling(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            error = False
            body = {}
            try:
                body = f(**kwargs)
            except:
                error = True
                db.session.rollback()
                print(sys.exc_info())
            finally:
                db.session.close()
            return error, body
        return wrapper
    return error_handling


@app.route('/lists/create/', methods=['POST'])
def create_todo_list():
    @error_handling_decorator(body={})
    def try_block_code(body):
        name = request.get_json().get('name', '')
        todo_list = TodoList(name=name)
        db.session.add(todo_list)
        db.session.commit()
        body['id'] = todo_list.id
        body['name'] = todo_list.name
        body['completed'] = todo_list.completed
        return body
    error, body = try_block_code(body={})
    if error:
        abort(500)
    else:
        return jsonify(body)


@app.route('/lists/<list_id>/set-completed/', methods=['POST'])
def set_completed_list(list_id):
    @error_handling_decorator(body={}, list_id=list_id)
    def try_block_code(body, list_id):
        completed = request.get_json().get('completed')
        todo_list = TodoList.query.get(list_id)
        for todo in todo_list.todos:
            todo.completed = completed
        db.session.commit()
        return body
    error, body = try_block_code(body={}, list_id=list_id)
    if error:
        abort(500)
    else:
        return redirect(url_for('index'))


@app.route('/lists/<list_id>/delete/', methods=['DELETE'])
def delete_list(list_id):
    @error_handling_decorator(body={}, list_id=list_id)
    def try_block_code(body, list_id):
        todo_list = TodoList.query.get(list_id)
        for todo in todo_list.todos:
            db.session.delete(todo)
        db.session.delete(todo_list)
        db.session.commit()
        return body
    error, body = try_block_code(body={}, list_id=list_id)
    if error:
        abort(500)
    else:
        return jsonify({'success': True})


@app.route('/todos/create/', methods=['POST'])
def create_todo_item():
    @error_handling_decorator(body={})
    def try_block_code(body):
        description = request.get_json().get('description', '')
        list_id = request.get_json().get('list_id', '')
        todo = Todo(description=description)
        todo.list = TodoList.query.get(list_id)
        db.session.add(todo)
        db.session.commit()
        body['id'] = todo.id
        body['completed'] = todo.completed
        body['description'] = todo.description
        return body
    error, body = try_block_code(body={})
    if error:
        abort(500)
    else:
        return jsonify(body)


@app.route('/todos/<todo_id>/set-completed/', methods=['POST'])
def set_completed_todo(todo_id):
    @error_handling_decorator(body={}, todo_id=todo_id)
    def try_block_code(body, todo_id):
        completed = request.get_json().get('completed')
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
        return body
    error, body = try_block_code(body={}, todo_id=todo_id)
    if error:
        abort(500)
    else:
        return redirect(url_for('index'))


@app.route('/todos/<todo_id>/delete/', methods=['DELETE'])
def delete_todo(todo_id):
    @error_handling_decorator(body={}, todo_id=todo_id)
    def try_block_code(body, todo_id):
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
        return body
    error, body = try_block_code(body={}, todo_id=todo_id)
    if error:
        abort(500)
    else:
        return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True)
