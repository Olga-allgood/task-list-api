
from flask import Blueprint, Response, abort, make_response, request, Request
import requests
from app.models.goal import Goal
from ..db import db
# from datetime import datetime
import os
# from dotenv import load_dotenv

# load_dotenv()

bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

@bp.post("")
def create_goal():
    request_body = request.get_json()

    try:
        new_goal = Goal.from_dict(request_body)
    except KeyError as error:
        response = {"details": "Invalid data"}  
        abort(make_response(response, 400))  

    db.session.add(new_goal)
    db.session.commit()
    
    return new_goal.to_dict(), 201

@bp.get("")
def get_all_goals():
    query = db.select(Goal).order_by(Goal.id)
    goals = db.session.scalars(query).all()

    if not goals:
        return [], 200
    
    goal_response = [goal.to_dict() for goal in goals]
    return goal_response, 200 

@bp.get("/<goal_id>")
def get_one_goal(goal_id):
    goal_response = validate_goal(goal_id)

    return goal_response.to_dict(), 200

@bp.put("/<goal_id>")
def update_goal(goal_id):
    goal = validate_goal(goal_id)
    request_body = request.get_json()
    goal.title=request_body["title"]
    db.session.commit()

    return Response(status = 204, mimetype="application/json")

@bp.delete("/<goal_id>")
def delete_one_goal(goal_id):
    goal = validate_goal(goal_id)
    db.session.delete(goal)
    db.session.commit()

    return Response(status=204, mimetype="application/json")
    

def validate_goal(goal_id):
    try:
        goal_id = int(goal_id)
    except:
        response = {"message": f"goal {goal_id} invalid"} 
        abort(make_response(response, 400))   

    query = db.select(Goal).where(Goal.id == goal_id)  
    goal = db.session.scalar(query)

    if not goal:
        not_found = {"message": f"goal {goal_id} not found"}
        abort(make_response(not_found, 404))

    return goal 