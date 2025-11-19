
from flask import Blueprint, Response, abort, make_response, request, Request
import requests
from .route_utilities import validate_model, create_model, get_models_with_filters
from app.models.goal import Goal
from app.models.task import Task 
from ..db import db
import os


bp = Blueprint("goals_bp", __name__, url_prefix="/goals")


@bp.post("")
def create_goal():
    request_body = request.get_json()
 
    return create_model(Goal, request_body)   
   

@bp.get("")
def get_all_goals():
    return get_models_with_filters(Goal, request.args), 200
    

@bp.get("/<goal_id>")
def get_one_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    return goal.to_dict(), 200

@bp.put("/<goal_id>")
def update_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()
    goal.title=request_body["title"]
    db.session.commit()

    return Response(status = 204, mimetype="application/json")

@bp.delete("/<goal_id>")
def delete_one_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    db.session.delete(goal)
    db.session.commit()

    return Response(status=204, mimetype="application/json")
    


@bp.get("/<goal_id>/tasks")
def get_tasks_by_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    return goal.to_dict(has_tasks=True), 200
    # response = {
    #     "id": goal.id,
    #     "title": goal.title,
    #     "tasks": [task.to_dict() for task in goal.tasks]
    # }
    # return response, 200

   
@bp.post("/<goal_id>/tasks")
def post_task_to_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()
    task_ids = request_body.get("task_ids", [])
    goal.tasks.clear()

    for task_id in task_ids:
        task = validate_model(Task, task_id)
        # task = db.session.scalar(db.select(Task).where(Task.id == task_id))
        if task:
            # task.goal_id = goal.id  
            goal.tasks.append(task)

    db.session.commit()

    return {"id": goal.id, "task_ids": [task.id for task in goal.tasks]}, 200


