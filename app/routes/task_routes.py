from flask import Blueprint

from flask import Blueprint, Response, abort, make_response, request
from app.models.task import Task
from ..db import db

bp = Blueprint("bp", __name__, url_prefix="/tasks")

@bp.post("")
def create_task():
    request_body = request.get_json()

    title = request_body["title"]
    description = request_body["description"]
    completed_at = request_body.get("completed_at", False)
    # completed_at = request_body.get("completed_at", None)

    if "title" not in request_body:
        return {"message": "Invalid data"}, 400
    if "description" not in request_body:
        return {"message": "Invalid data"}, 400
    

    new_task = Task(
        title=title,
        description=description,
        completed_at=completed_at
    )

    db.session.add(new_task)
    db.session.commit()

    task_response = {
        "id": new_task.id,
        "title": new_task.title,
        "description": new_task.description,
        "completed_at": None,
    }
    
    return task_response, 201

@bp.get("")
def get_all_tasks():
    query = db.select(Task).order_by(Task.id)
    tasks = db.session.scalars(query)

    result_list = []

    for task in tasks:
        result_list.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed_at": None
        })

    return result_list, 200

@bp.get("/<task_id>")
def get_one_planet(task_id):
    task = validate_task(task_id)
    result = {"id": task.id,
            "title": task.title,
            "description": task.description,
            "completed_at": None}
    return result, 200

def validate_task(task_id):
    try:
        task_id = int(task_id)
    except ValueError:
        response = {"message": f"task {task_id} invalid"} 
        abort(make_response(response, 400))   

    query = db.select(Task).where(Task.id == task_id)  
    task = db.session.scalar(query)

    if not task:
        not_found = {"message": f"task {task_id} not found"}
        abort(make_response(not_found, 404))

    return task  

@bp.put("/<task_id>")
def update_task(task_id):
    task = validate_task(task_id)
    request_body = request.get_json()
    task.title = request_body["title"]
    task.description = request_body["description"]
    task.completed_at = request_body.get("completed_at", None)
    db.session.commit()

    return Response(status = 204, mimetype = "application/json")

@bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_task(task_id)
    db.session.delete(task)
    db.session.commit()

    return Response(status = 204, mimetype = "application/json")