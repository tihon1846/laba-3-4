from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import logging
import time
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.json.ensure_ascii = False
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
file_handler = RotatingFileHandler(filename="app.log", maxBytes=1024*1024, backupCount=3)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

def get_db_connection():
    conn = sqlite3.connect("poliklinika.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Doctors (
    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(100) NOT NULL,
    specialisation_id INTEGER NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(12),
    adress VARCHAR(150) NOT NULL,
    birthday_date DATE NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Medicines (
    med_id INTEGER PRIMARY KEY AUTOINCREMENT,
    med_name VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_date DATE NOT NULL,
    diagnosis TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Specialisations (
    specialisation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    specialisation_name VARCHAR(50) NOT NULL UNIQUE)''')

def insert_test_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM patients")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany("""
            INSERT INTO Specialisations (specialisation_name)
            VALUES (?)
        """, [
            ('Терапевт',),
            ('Кардиолог',),
            ('Невролог',)
        ])

        cursor.executemany("""
            INSERT INTO Doctors (full_name, specialisation_id)
            VALUES (?, ?)
        """, [
            ('Иванов Иван Иванович', 1),
            ('Петров Петр Петрович', 2),
            ('Сидоров Сергей Сергеевич', 3)
        ])

        cursor.executemany("""
            INSERT INTO Patients (full_name, phone, adress, birthday_date)
            VALUES (?, ?, ?, ?)
        """, [
            ('Смирнов Алексей Андреевич', '+79990001122', 'Москва', '2001-05-10'),
            ('Кузнецова Мария Игоревна', '+79993334455', 'Химки', '1999-11-21'),
            ('Орлов Дмитрий Павлович', '+79996667788', 'Мытищи', '2003-02-15')
        ])

        cursor.executemany("""
            INSERT INTO Appointments (patient_id, doctor_id, appointment_date, diagnosis)
            VALUES (?, ?, ?, ?)
        """, [
            (1, 1, '2026-05-10', 'ОРВИ'),
            (2, 2, '2026-05-11', 'Аритмия'),
            (3, 3, '2026-05-12', 'Мигрень')
        ])

        cursor.executemany("""
            INSERT INTO Medicines (med_name, manufacturer, price)
            VALUES (?, ?, ?)
        """, [
            ('Парацетамол', 'ФармСтандарт', 120.50),
            ('Но-шпа', 'Sanofi', 210.00),
            ('Анальгин', 'Renewal', 95.30)
        ])

    conn.commit()
    conn.close()

@app.route("/")
def home():
    return jsonify(
        {"message": "API поликлиники работает", 
         "routes": ["api/patients", "api/patients/<id>", "api/doctors", "api/appointments", "api/medicines"]}
    )

#############################################################################################

@app.route("/api/patients", methods=["GET"])
def get_patient():
    start_time = time.time()
    conn = get_db_connection()

    logger.info(f"GET /api/patients from {request.remote_addr}")

    try:
        patients = conn.execute("SELECT * FROM patients").fetchall()
        result = [dict(row) for row in patients]
        duration = time.time() - start_time
        logger.info(f"Request completed in {duration:.4f} sec")
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Ошибка сервера"}), 500
    
    finally:
        conn.close()


@app.route("/api/patients", methods=["POST"])
def add_patient():
    start_time = time.time()
    logger.info(f"POST /api/patients from {request.remote_addr}")
    data = request.get_json()
    
    if not data:
        logger.warning("Пустой JSON")
        return jsonify({"error": "Нет данных"}), 400
    
    if not data.get("full_name"):
        return jsonify({'error': "обязательное поле ввода"}), 406
    
    conn = get_db_connection()

    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Patients
                    (full_name, phone, adress, birthday_date)
                    VALUES (?, ?, ?, ?)''',
                    (data.get("full_name"), data.get("phone"), data.get("adress"), data.get("birthday_date")))

        conn.commit()

        duration = time.time() - start_time
        logger.info(f"Patient added: {data.get('full_name')}")
        logger.info(f"Request completed in {duration:.4f} sec")
        
        return jsonify({"message": "Пациент добавлен", "patient_id": cursor.lastrowid}), 201
    
    except Exception as e:
        conn.rollback()

        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Ошибка базы данных"}), 500
    
    finally:
        conn.close()

@app.route("/api/patients/<int:patient_id>", methods=["GET"])
def get_patient_by_id(patient_id):
    start_time = time.time()
    conn = get_db_connection()

    logger.info(f"GET /api/patients/<int:patient_id> from {request.remote_addr}")

    try:
        patients = conn.execute("SELECT * FROM Patients WHERE patient_id = ?", (patient_id,)).fetchone()
        if patients is None:
            return jsonify({'error': "пациент не найден"}), 404
        duration = time.time() - start_time
        logger.info(f"Request completed in {duration:.4f} sec")
        return jsonify(dict(patients))

    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
    finally:
        conn.close()

###########################################################################################

@app.route("/api/doctors", methods=["GET"])
def get_doctors():
    start_time = time.time()
    conn = get_db_connection()

    logger.info(f"GET /api/doctors from {request.remote_addr}")

    try:
        doctors = conn.execute('''
                               SELECT d.doctor_id, d.full_name, s.specialisation_name
                               FROM Doctors d
                               JOIN Specialisations s ON d.specialisation_id = s.specialisation_id''').fetchall()

        result = [dict(row) for row in doctors]
        duration = time.time() - start_time
        logger.info(f"Request completed in {duration:.4f} sec")
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({'error': str(e)}), 501
    
    finally:
        conn.close()

@app.route("/api/appointments", methods=["GET"])
def get_appointment():
    start_time = time.time()
    conn = get_db_connection()

    logger.info(f"GET /api/appointments from {request.remote_addr}")
    
    try:
        appointments = conn.execute('''
                                    SELECT a.appointment_id, p.full_name AS patient_name, d.full_name AS doctor_name, s.specialisation_name, a.appointment_date, a.diagnosis
                                    FROM Appointments a
                                    JOIN Patients p ON a.patient_id = p.patient_id
                                    JOIN Doctors d ON a.doctor_id = d.doctor_id
                                    JOIN Specialisations s ON d.specialisation_id = s.specialisation_id''').fetchall()
        
        result = [dict(row) for row in appointments]
        duration = time.time() - start_time
        logger.info(f"Request completed in {duration:.4f} sec")
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({'error': str(e)}), 502
    
    finally:
        conn.close()

@app.route("/api/medicines", methods=["GET"])
def get_medicines():
    start_time = time.time()
    conn = get_db_connection()

    logger.info(f"GET /api/medicines from {request.remote_addr}")

    try:
        medicines = conn.execute('''
                                SELECT * FROM Medicines''').fetchall()
        
        result = [dict(row) for row in medicines]
        duration = time.time() - start_time
        logger.info(f"Request completed in {duration:.4f} sec")
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({'error': str(e)}), 503
    
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    insert_test_data()
    app.run(debug=True)
