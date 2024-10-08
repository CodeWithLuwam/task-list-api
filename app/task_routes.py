import os, requests
from flask import Blueprint, jsonify, make_response, request
from app import db
from app.models.task import Task
from app.helper import validate_task

#CREATE BP/ENDPOINT
tasks_bp = Blueprint("tasks", __name__, url_prefix= "/tasks") 

# GET all tasks - /tasks [READ] 
@tasks_bp.route("", methods =["GET"])
def get_all_tasks():
    if request.args.get("sort") == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    elif request.args.get("sort") == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else:
        tasks = Task.query.all()
    tasks_response = []
    for task in tasks:
        tasks_response.append(task.to_json())

    return jsonify(tasks_response), 200

# GET one task - /tasks/<id>  [READ]
@tasks_bp.route("/<id>", methods=["GET"])
def get_one_task(id):
    task = validate_task(id)
    return jsonify({"task":task.to_json()}), 200

#POST  - /tasks [CREATE]
@tasks_bp.route("", methods= ["POST"])
def create_task():
    request_body = request.get_json()
    new_task = Task.create_dict(request_body)
    
    db.session.add(new_task)
    db.session.commit()
    
    return make_response({"task":new_task.to_json()}), 201

#PUT one task - /tasks/<id>  [UPDATE]
@tasks_bp.route("/<id>",methods=["PUT"])
def update_task(id):
    task = validate_task(id)
    request_body = request.get_json()
    task.update_dict(request_body)
    
    db.session.commit()

    return jsonify({"task":task.to_json()}), 200

#DELETE one task - /tasks/<id> [DELETE]
@tasks_bp.route("/<id>", methods=["DELETE"])
def delete_task(id):
    task_to_delete = validate_task(id)

    db.session.delete(task_to_delete)
    db.session.commit()

    message = {"details": f'Task 1 "{task_to_delete.title}" successfully deleted'}
    return make_response(message, 200)

#PATCH /tasks/1/mark_incomplete [UPDATE]
@tasks_bp.route("/<id>/mark_incomplete", methods = ["PATCH"])
def mark_incompleted(id):
    task_to_incomplete = validate_task(id)
    request_body = request.get_json()
    task_to_incomplete.patch_incomplete(request_body)
    
    db.session.commit()

    return jsonify({"task":task_to_incomplete.to_json()}), 200

# PATCH tasks/<id>/mark_complete [UPDATE]
@tasks_bp.route("/<id>/mark_complete", methods=["PATCH"])
def mark_completed(id):
    task_to_complete = validate_task(id)
    request_body = request.get_json()
    task_to_complete.patch_complete(request_body)

    db.session.commit()

    PATH = "https://slack.com/api/chat.postMessage"

    query_params = {
        "channel": "api-test-channel",
        "text": f'Task {task_to_complete.title} has been completed!'
    }

    the_headers = {"Authorization": os.environ.get("SLACK_API_KEY")}
    
    requests.post(PATH, params=query_params, headers=the_headers)

    return jsonify({"task":task_to_complete.to_json()}), 200