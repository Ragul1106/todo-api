from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {"id": self.id, "title": self.title, "status": self.status}

class TaskListAPI(Resource):
    def get(self):
        """Get all tasks"""
        tasks = Task.query.all()
        return [task.to_dict() for task in tasks]

    def post(self):
        """Add a new task (title required)"""
        data = request.get_json(silent=True) or {}
        title = data.get("title")

        if not title:
            return {"error": "Task title is required"}, 400

        task = Task(title=title, status=False)
        db.session.add(task)
        db.session.commit()
        return task.to_dict(), 201


class TaskAPI(Resource):
    def put(self, task_id):
        """Update or toggle task status"""
        task = Task.query.get_or_404(task_id)
        data = request.get_json(silent=True) or {}

        if "title" in data:
            task.title = data["title"]

        if "status" in data:
            task.status = bool(data["status"])
        elif "toggle" in data:  
            task.status = not task.status

        db.session.commit()
        return task.to_dict(), 200

    def delete(self, task_id):
        """Delete a task"""
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return {"message": f"Task {task_id} deleted"}, 200


api.add_resource(TaskListAPI, "/tasks")
api.add_resource(TaskAPI, "/tasks/<int:task_id>")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
