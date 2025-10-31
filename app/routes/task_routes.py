from flask import Blueprint

from flask import Blueprint, Response, abort, make_response, request
from app.models.task import Task
from ..db import db

bp = Blueprint("bp", __name__, url_prefix="/tasks")

@bp.post("")
def create_task():
    request_body = request.get_json()

    try:
        new_task = Task.from_dict(request_body)
    except KeyError as error:
        response = {"message": "Invalid data"}  
        abort(make_response(response, 400))  

    db.session.add(new_task)
    db.session.commit()
    
    return new_task.to_dict(), 201

@bp.get("")
def get_all_tasks():
    query = db.select(Task)
    tasks = db.session.scalars(query.order_by(Task.id))

    task_response = []

    for task in tasks:
        task_response.append(task.to_dict())

    return task_response, 200

@bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_task(task_id)

    return task.to_dict(), 200



@bp.put("/<task_id>")
def update_task(task_id):
    task = validate_task(task_id)
    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]
    # task.completed_at = request_body.get("completed_at", None)
    db.session.commit()

    return Response(status = 204, mimetype = "application/json")

@bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_task(task_id)
    db.session.delete(task)
    db.session.commit()

    return Response(status = 204, mimetype = "application/json")

def validate_task(task_id):
    try:
        task_id = int(task_id)
    except:
        response = {"message": f"task {task_id} invalid"} 
        abort(make_response(response, 400))   

    query = db.select(Task).where(Task.id == task_id)  
    task = db.session.scalar(query)

    if not task:
        not_found = {"message": f"task {task_id} not found"}
        abort(make_response(not_found, 404))

    return task  