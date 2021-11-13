from flask import Flask, request, jsonify
import sqlite3
import json
import uuid

def create_app():
    app = Flask(__name__)
    
    def get_db():
        return sqlite3.connect("polls.db")
    
    @app.after_request
    def apply_cors(response):
        response.headers["Access-Control-Allow-Origin"] = '*'
        return response
    
    """
    This just shoves a new poll in the database with 0 yes's and 0 no's.
    Feed it JSON, and you'll get the same json back at any other endpoint.
    Recommended schema:
    {
        "title": "Title of poll",
        "description": "optional description of poll"
    }
    returns:
    {
        "uuid": "UUID-3059..."
    }
    """
    @app.route("/polls/new", methods = ["POST"])
    def new_poll():
        # make sure it's valid json
        j = request.get_json(force=True)
        assert j is not None
        db = get_db()
        u = str(uuid.uuid4())
        db.execute("insert into polls values (?,?,0,0)", (u, json.dumps(j)))
        db.commit()
        return jsonify({"uuid": u})
    
    """
    gets a poll by UUID (see next endpoint)
    {
        "header": {
            <json you made earlier>
        },
        "votes": {
            "yes": 2,
            "no": 3
        }
    }
    """
    @app.route("/polls/get/<uuid>")
    def get_poll(uuid):
        c = get_db().cursor()
        c.execute("SELECT * from polls where uuid = ?", (uuid,))
        (_, js, yes, no) = c.fetchone()
        d = {
            "header": json.loads(js),
            "votes": {
                "yes": yes,
                "no": no 
            }
        }
        return jsonify(d)
    
    """
    Schema:
    [
        "UUID-30924-3454",
        ...
    ]
    """
    @app.route("/polls/list")
    def list_polls():
        c = get_db().cursor()
        c.execute("SELECT uuid from polls")
        return jsonify([x for (x,) in c.fetchall()])
    
    """
    /polls/vote/<uuid>/yes or /polls/vote/<uuid>/no
    """
    @app.route("/polls/vote/<uuid>/<option>", methods = ["POST"])
    def vote(uuid, option):
        assert option in ["yes", "no"]
        db = get_db()
        db.execute(f"UPDATE polls SET {option} = {option} + 1 WHERE uuid = ?", (uuid,))
        db.commit()
        return jsonify({"status": "ok"})

    return app

app = create_app()
app.run('127.0.0.1', 8081)