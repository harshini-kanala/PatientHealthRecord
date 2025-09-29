from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",          # your MySQL username
    password="kamakshi@1806",  # your MySQL password
    database="PatientHealthDB"
)
cursor = db.cursor(dictionary=True)
@app.route('/')
def home():
    return "Welcome to Patient Health Record System API! Try /patients, /doctors, /appointments"

# ---------- PATIENT CRUD ----------
@app.route("/patients", methods=["GET"])
def get_patients():
    cursor.execute("SELECT * FROM Patient")
    return jsonify(cursor.fetchall())

@app.route("/patients/<int:id>", methods=["GET"])
def get_patient(id):
    cursor.execute("SELECT * FROM Patient WHERE PatientID=%s", (id,))
    return jsonify(cursor.fetchone())

@app.route("/patients", methods=["POST"])
def add_patient():
    data = request.json
    sql = "INSERT INTO Patient (Name, DOB, Gender, Phone, Address, BloodGroup) VALUES (%s,%s,%s,%s,%s,%s)"
    val = (data["Name"], data["DOB"], data["Gender"], data["Phone"], data["Address"], data["BloodGroup"])
    cursor.execute(sql, val)
    db.commit()
    return jsonify({"message": "Patient added successfully"}), 201

@app.route("/patients/<int:id>", methods=["PUT"])
def update_patient(id):
    data = request.json
    sql = "UPDATE Patient SET Name=%s, DOB=%s, Gender=%s, Phone=%s, Address=%s, BloodGroup=%s WHERE PatientID=%s"
    val = (data["Name"], data["DOB"], data["Gender"], data["Phone"], data["Address"], data["BloodGroup"], id)
    cursor.execute(sql, val)
    db.commit()
    return jsonify({"message": "Patient updated successfully"})

@app.route("/patients/<int:id>", methods=["DELETE"])
def delete_patient(id):
    cursor.execute("DELETE FROM Patient WHERE PatientID=%s", (id,))
    db.commit()
    return jsonify({"message": "Patient deleted successfully"})

# ---------- APPOINTMENTS ----------
@app.route("/appointments", methods=["GET"])
def get_appointments():
    cursor.execute("SELECT * FROM Appointment")
    return jsonify(cursor.fetchall())

@app.route("/appointments", methods=["POST"])
def add_appointment():
    data = request.json
    sql = """INSERT INTO Appointment (PatientID, DoctorID, AppointmentDate, AppointmentTime, Status) 
             VALUES (%s,%s,%s,%s,%s)"""
    val = (data["PatientID"], data["DoctorID"], data["AppointmentDate"], data["AppointmentTime"], data["Status"])
    try:
        cursor.execute(sql, val)
        db.commit()
        return jsonify({"message": "Appointment added successfully"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400

# ---------- BILLING ----------
@app.route("/billing/<int:pid>", methods=["GET"])
def get_bills(pid):
    cursor.execute("SELECT * FROM Billing WHERE PatientID=%s", (pid,))
    return jsonify(cursor.fetchall())

if __name__ == "__main__":
    app.run(debug=True)
