from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import sqlite3
from datetime import datetime
import bcrypt

# ------------------ FLASK APP SETUP ------------------
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ------------------ MYSQL CONFIG (MAIN DATABASE) ------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Akshaya@7777", 
    database="patientdb"
)
cursor = db.cursor(dictionary=True)

# =====================================================
#                ADMIN LOGIN & DASHBOARD
# =====================================================

@app.route('/', methods=['GET', 'POST'])
def login():
    """Admin login page"""
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


@app.route('/dashboard')
def dashboard():
    """Admin dashboard showing today's appointments"""
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

# =====================================================
#                ADD / VIEW PATIENTS
# =====================================================

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    """Add a patient (MySQL version for hospital)"""
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
        cursor.execute("""
            INSERT INTO patients (name, age, gender, phone, email, address, medical_history, 
                                  last_appointment, next_appointment, doctor_id, has_history)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, data)
        db.commit()
        flash("Patient added successfully!", "success")
        return redirect(url_for('add_patient'))

    return render_template('add_patient.html')


@app.route('/view_patients')
def view_patients():
    """View all patients"""
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    cursor.execute("SELECT * FROM patients ORDER BY name")
    patients = cursor.fetchall()
    return render_template('view_patients.html', patients=patients)

# =====================================================
#                BILL GENERATION
# =====================================================

@app.route('/generate_bill', methods=['GET', 'POST'])
def generate_bill():
    """Generate bill for patient"""
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

# =====================================================
#                SIMPLE SQLITE FORM (DEMO)
# =====================================================

@app.route('/sqlite_form')
def sqlite_form():
    """Show form.html for SQLite-based demo"""
    return render_template('form.html', message=None)


@app.route('/insert_sqlite', methods=['POST'])
def insert_patient_sqlite():
    """Insert into SQLite patient table (form.html)"""
    patient_id = request.form['patient_id']
    name = request.form['name']
    age = request.form['age']
    email = request.form['email']
    doctor_id = request.form['doctor_id']

    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO patients (patient_id, name, age, email, doctor_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (patient_id, name, age, email, doctor_id))
        conn.commit()
        conn.close()
        return render_template('form.html', message="✅ Patient record added successfully!")

    except sqlite3.IntegrityError as e:
        error_message = str(e)
        if "UNIQUE constraint failed: patients.patient_id" in error_message:
            msg = "❌ Clash: Duplicate Patient ID!"
        elif "UNIQUE constraint failed: patients.email" in error_message:
            msg = "❌ Clash: Duplicate Email ID!"
        elif "NOT NULL constraint failed" in error_message:
            msg = "❌ Clash: Required field missing!"
        elif "CHECK constraint failed" in error_message:
            msg = "❌ Clash: Invalid data (e.g., negative age)!"
        else:
            msg = f"⚠ Database Error: {error_message}"
        return render_template('form.html', message=msg)

    except Exception as e:
        return render_template('form.html', message=f"⚠ Unexpected Error: {str(e)}")

# =====================================================
#                LOGOUT
# =====================================================

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# =====================================================
#                MAIN ENTRY POINT
# =====================================================

if __name__ == '__main__':
    app.run(debug=True)
