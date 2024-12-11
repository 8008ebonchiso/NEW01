from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3

app = FastAPI()


# データベース初期化
def init_db():
    with sqlite3.connect('todos.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed BOOLEAN DEFAULT FALSE
            )
        ''')


init_db()


class Todo(BaseModel):
    title: str
    completed: Optional[bool] = False


class TodoResponse(Todo):
    id: int


# 新規TODO作成
@app.post("/todos", response_model=TodoResponse)
def create_todo(todo: Todo):
    with sqlite3.connect('todos.db') as conn:
        cursor = conn.execute(
            'INSERT INTO todos (title, completed) VALUES (?, ?)',
            (todo.title, todo.completed)
        )
        todo_id = cursor.lastrowid
        return {"id": todo_id, "title": todo.title, "completed": todo.completed}


# 全TODO取得
@app.get("/todos")
def get_todos():
    with sqlite3.connect('todos.db') as conn:
        todos = conn.execute('SELECT * FROM todos').fetchall()
        return [
            {"id": t[0], "title": t[1], "completed": bool(t[2])}
            for t in todos
        ]


# 個別TODO取得
@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    with sqlite3.connect('todos.db') as conn:
        todo = conn.execute(
            'SELECT * FROM todos WHERE id = ?', (todo_id,)).fetchone()
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        return {"id": todo[0], "title": todo[1], "completed": bool(todo[2])}


# TODO更新
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: Todo):
    with sqlite3.connect('todos.db') as conn:
        cursor = conn.execute(
            'UPDATE todos SET title = ?, completed = ? WHERE id = ?',
            (todo.title, todo.completed, todo_id)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Todo not found")
        return {"id": todo_id, "title": todo.title, "completed": todo.completed}


# TODO削除
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    with sqlite3.connect('todos.db') as conn:
        cursor = conn.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Todo not found")
        return {"message": "Todo deleted"}
