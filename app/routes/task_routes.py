from flask import Blueprint
from .route_utilities import validate_model, create_model, get_models_with_filters
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


@bp.post("")
def create_task():
    request_body = request.get_json()

    return create_model(Task, request_body)

# @bp.get("")
# def get_all_tasks():
#     query = db.select(Task)

#     sort_param = request.args.get("sort")

#     if sort_param == "desc":
#         query = query.order_by(Task.title.desc())
#     elif sort_param == "asc":
#         query = query.order_by(Task.title.asc())

#     tasks = db.session.execute(query).scalars()

#     task_response = [task.to_dict() for task in tasks]
#     return task_response, 200

@bp.get("")
def get_all_tasks():
    # tasks_response = get_models_with_filters(Task, filters=request.args)
    # return tasks_response, 200
    filters = dict(request.args)
    tasks_response = get_models_with_filters(Task, filters=filters)
    return tasks_response, 200
  

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
    db.session.commit()

    return Response(status = 204, mimetype = "application/json")

@bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_model(Task, task_id)
    db.session.delete(task)
    db.session.commit()
    
    return Response(status = 204, mimetype = "application/json")


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

    

 