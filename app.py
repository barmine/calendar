from datetime import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///calendar.db"
db = SQLAlchemy(app)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "description": self.description,
        }


@app.route("/")
def home():
    return "Calendar is alive!"


@app.route("/events", methods=["GET"])
def list_events():
    return jsonify([e.to_dict() for e in Event.query.all()])


@app.route("/events", methods=["POST"])
def create_event():
    data = request.get_json()
    event = Event(
        title=data["title"],
        start=datetime.fromisoformat(data["start"]),
        end=datetime.fromisoformat(data["end"]),
        description=data.get("description"),
    )
    db.session.add(event)
    db.session.commit()
    return jsonify(event.to_dict()), 201


@app.route("/events/<int:event_id>", methods=["PATCH"])
def update_event(event_id):
    event = db.get_or_404(Event, event_id)
    data = request.get_json()
    if "title" in data:
        event.title = data["title"]
    if "start" in data:
        event.start = datetime.fromisoformat(data["start"])
    if "end" in data:
        event.end = datetime.fromisoformat(data["end"])
    if "description" in data:
        event.description = data["description"]
    db.session.commit()
    return jsonify(event.to_dict())


@app.route("/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    event = db.get_or_404(Event, event_id)
    db.session.delete(event)
    db.session.commit()
    return "", 204


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
