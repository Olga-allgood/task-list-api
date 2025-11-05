from flask import Blueprint
from .route_utilities import *
from flask import Blueprint, Response, abort, make_response, request, Request
import requests
from app.models.task import Task
from ..db import db
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")


# QUESTION: why the request_body line cannot be moved into route_utilities?

@bp.post("")
def create_task():
    request_body = request.get_json()

    return create_model(Task, request_body), '201 CREATED'

    # try:
    #     new_task = Task.from_dict(request_body)
    # except KeyError as error:
    #     response = {"details": "Invalid data"}  
    #     abort(make_response(response, 400))  

    # db.session.add(new_task)
    # db.session.commit()
    
    # # return new_task.to_dict()
    # return new_task.to_dict(), '201 CREATED'

# @bp.get("")
# def get_all_tasks():
#     query = db.select(Task)

#     title_param = request.args.get("title")
#     if title_param == "/tasks?sort=desc":
#         query = query.order_by(Task.title.desc())

#     if title_param == "/tasks?sort=asc":
#         query = query.order_by(Task.title.asc())
            
#     # tasks = db.session.scalars(query.order_by(Task.title))
#     tasks = db.session.execute(query).scalars()

#     task_response = []

#     for task in tasks:
#         task_response.append(task.to_dict())

#     return task_response, 200
@bp.get("")
def get_all_tasks():
    # query = db.select(Task)

    # sort_param = request.args.get("sort")

    # if sort_param == "desc":
    #     query = query.order_by(Task.title.desc())
    # elif sort_param == "asc":
    #     query = query.order_by(Task.title.asc())

    # tasks = db.session.execute(query).scalars()

    # task_response = [task.to_dict() for task in tasks]

    return get_models_with_filters(Task, request.args), 200

@bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_model(Task, task_id)

    return task.to_dict(), 200

@bp.put("/<task_id>")
def update_task(task_id):
    task = validate_model(Task, task_id)
    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]
    # task.completed_at = request_body.get("completed_at", None)
    db.session.commit()

    return Response(status = 204, mimetype = "application/json")

@bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_model(Task, task_id)
    db.session.delete(task)
    db.session.commit()
    
    return Response(status = 204, mimetype = "application/json")

# def validate_task(task_id):
#     try:
#         task_id = int(task_id)
#     except:
#         response = {"message": f"task {task_id} invalid"} 
#         abort(make_response(response, 400))   

#     query = db.select(Task).where(Task.id == task_id)  
#     task = db.session.scalar(query)

#     if not task:
#         not_found = {"message": f"task {task_id} not found"}
#         abort(make_response(not_found, 404))

#     return task  


@bp.patch("/<task_id>/mark_complete")
def mark_task_complete(task_id):
    task = task = validate_model(Task, task_id)
    task.completed_at = datetime.now()

    db.session.commit()

    slack_url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": "slack-api-testing",
        "text": f"Here is your completed task: {task.title}"
    }
    response = requests.post(slack_url, headers=headers, json=payload)
    return Response(status=204, mimetype = "application/json")

@bp.patch("/<task_id>/mark_incomplete")
def mark_test_incomplete(task_id):
    task = task = validate_model(Task, task_id)
    task.completed_at = None 

    db.session.commit()

    return Response(status=204, mimetype="application/json")

    

 