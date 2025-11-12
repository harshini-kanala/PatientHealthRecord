from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import datetime
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ------------------ DATABASE CONFIG ------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Akshaya@7777",
    database="patientdb"
)
cursor = db.cursor(dictionary=True)

# ------------------ LOGIN PAGE ------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM admin_users WHERE username = %s", (username,))
        admin = cursor.fetchone()

        if admin and bcrypt.checkpw(password.encode('utf-8'), admin['password_hash'].encode('utf-8')):
            session['admin_id'] = admin['admin_id']
            session['username'] = admin['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')


# ------------------ DASHBOARD ------------------
@app.route('/dashboard')
def dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    today = datetime.now().date()
    cursor.execute("""
        SELECT a.appointment_id, p.name, a.doctor_name, a.department, a.appointment_date, a.status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        WHERE DATE(a.appointment_date) = %s
        ORDER BY a.appointment_date
    """, (today,))
    appointments = cursor.fetchall()

    return render_template('dashboard.html', appointments=appointments, today=today)


# ------------------ ADD PATIENT ------------------
@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = (
            request.form['name'],
            request.form['age'],
            request.form['gender'],
            request.form['phone'],
            request.form['email'],
            request.form['address'],
            request.form['medical_history'],
            request.form['last_appointment'],
            request.form['next_appointment'],
            request.form['doctor_assigned'],
            request.form['has_history']
        )

        # Updated: using doctor_assigned (string)
        cursor.execute("""
            INSERT INTO patients (name, age, gender, phone, email, address, medical_history, 
                                  last_appointment, next_appointment, doctor_assigned, has_history)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, data)

        db.commit()
        flash("✅ Patient added successfully!", "success")
        return redirect(url_for('add_patient'))

    return render_template('add_patient.html')


# ------------------ GENERATE BILL ------------------
@app.route('/generate_bill', methods=['GET', 'POST'])
def generate_bill():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        patient_id = request.form['patient_id']
        appointment_id = request.form['appointment_id']
        consultation_fee = float(request.form['consultation_fee'])
        medicine_charges = float(request.form['medicine_charges'])
        lab_test_charges = float(request.form['lab_test_charges'])

        cursor.execute("""
            INSERT INTO bills (patient_id, appointment_id, consultation_fee, medicine_charges, 
                               lab_test_charges, payment_status)
            VALUES (%s,%s,%s,%s,%s,'Pending')
        """, (patient_id, appointment_id, consultation_fee, medicine_charges, lab_test_charges))
        db.commit()
        flash("Bill generated successfully!", "success")

    cursor.execute("SELECT patient_id, name FROM patients")
    patients = cursor.fetchall()
    return render_template('generate_bill.html', patients=patients)


# ------------------ VIEW ALL PATIENTS ------------------
@app.route('/view_patients')
def view_patients():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    cursor.execute("SELECT * FROM patients ORDER BY name")
    patients = cursor.fetchall()
    return render_template('view_patients.html', patients=patients)


# ------------------ LOGOUT ------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ------------------ MAIN ------------------
if __name__ == '__main__':
    app.run(debug=True)
