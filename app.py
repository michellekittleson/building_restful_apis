# Task 1: Setting Up the Flask Environment and Database Connection
    # Create virtual environment: python3 -m venv fitness_center_venv
    # Activate virtual environment: source fitness_center_venv/bin/activate
    # Install Packages: pip3 install flask flask-marshmallow mysql-connector-python

from flask import Flask, app, jsonify, request
from flask_marshmallow import Marshmallow
import mysql.connector
from mysql.connector import Error
from marshmallow import Schema, fields, ValidationError

app = Flask(__name__)
ma = Marshmallow(app)

def get_db_connection():
    db_name = "fitness_center_db"
    user = "root"
    password = "Lynn060386!"
    host = "localhost"

    try:
        conn = mysql.connector.connect(
            database = db_name,
            user = user,
            password = password,
            host = host
        )
        print("Connected to MySQL database successfully")
        return conn
    
    except Error as e:
        print(f"Error: {e}")
        return None

class MemberSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    age = fields.Date(required=True)

class WorkoutSessionSchema(ma.Schema):
    session_id = fields.Int(required=True)
    member_id = fields.Str(required=True)
    session_date = fields.Date(required=True)
    session_time = fields.Time(required=True)
    activity = fields.Str(required=True)


member_schema = MemberSchema()
members_schema = MemberSchema(many=True)
workoutsesion_schema = WorkoutSessionSchema()
workoutsessions_schema = WorkoutSessionSchema(many=True)

# Task 2: Implementing CRUD Operations for Members
# Route to add member to Members table
@app.route('/members', methods=["POST"])
def add_member():
    try:
        member = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        query = "INSERT INTO Members (name, birthdate) VALUES (%s, %s, %s)"
        cursor.execute(query, (member['name'], member['age']))

        conn.commit()
        return jsonify({"message": "Member added successfully"}), 201
    
    except Error as e:
        return jsonify({"error": str(e)}), 500


# Route to retrieve members from Members table
@app.route('/members', methods=["GET"])
def get_members():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT m.id, m.name, m.age FROM Members m, WorkoutSessions w WHERE m.id = w.member_id")
        members = cursor.fetchall()

        return members_schema.jsonify(members)
    
    except Error as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()

# Route to update member from Members table
@app.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        updated_member = (member_data['name'], member_data['age'], id)

        query = "UPDATE Members SET name = %s, age = %s WHERE id = %s"

        cursor.execute(query, updated_member)
        conn.commit()

        return jsonify({"message": "Member data updated successfully"}), 201
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Route to delete member from Members table
@app.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        member_to_remove = (id,)
        cursor.execute("SELECT * FROM Members WHERE id = %s", member_to_remove)
        member = cursor.fetchone()
        if not member:
            return jsonify({"error": "Member not found"}), 404
        
        query = "DELETE FROM Members WHERE id = %s"
        cursor.execute(query, member_to_remove)
        conn.commit()

        return jsonify({"message": "Member removed successfully"}), 200
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected:
            cursor.close()
            conn.close()


# Task 3: Managing Workout Sessions
# Route to schedule a workout session
@app.route('/workoutsessions', methods=["POST"])
def add_workoutsession():
    try:
        workoutsession = workoutsesion_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        query = "INSERT INTO WorkoutSessions (member_id, session_date, session_time, activity) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (workoutsession['member_id'], workoutsession['session_date'], workoutsession['session_time'], workoutsession['activity']))

        conn.commit()
        return jsonify({"message": "Workout Session added successfully"}), 201
    
    except Error as e:
        return jsonify({"error": str(e)}), 500

# Route to update a workout session
@app.route("/workoutsessions/<int:id>", methods=["PUT"])
def update_workoutsession(id):
    try:
        workoutsession_data = workoutsesion_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        updated_workoutsession = (workoutsession_data['member_id'], workoutsession_data['session_date'], workoutsession_data['session_time'], workoutsession_data['activity'], id)

        query = "UPDATE WorkoutSessions SET member_id = %s, session_date = %s, sesion_time = %s, activity = %s WHERE id = %s"

        cursor.execute(query, updated_workoutsession)
        conn.commit()

        return jsonify({"message": "Member data updated successfully"}), 201
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Route to view all workout sessions for a specific member
@app.route('/members/<int:id>/workoutsessions', methods=["GET"])
def workoutsessions_by_member(id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT w.session_id, w.session_date, w.session_time, w.activitu FROM Members m, WorkoutSessions w WHERE m.id = w.member_id")
        workout_sessions = cursor.fetchall()

        return workoutsessions_schema.jsonify(workout_sessions)
    
    except Error as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()