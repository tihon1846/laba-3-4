-- Доктора
CREATE TABLE Doctors (
    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(100) NOT NULL,
    specialisation_id INTEGER NOT NULL,

    FOREIGN KEY (specialisation_id) REFERENCES Specialisations(specialisation_id)
);

-- Пациенты
CREATE TABLE Patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(12),
    adress VARCHAR(150) NOT NULL,
    birthday_date DATE NOT NULL
);

-- Лекарства
CREATE TABLE Medicines (
    med_id INTEGER PRIMARY KEY AUTOINCREMENT,
    med_name VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

-- Записи на приём
CREATE TABLE Appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_date DATE NOT NULL,
    diagnosis TEXT NOT NULL,

    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id)
);

-- Специализации
CREATE TABLE Specialisations (
    specialisation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    specialisation_name VARCHAR(50) NOT NULL UNIQUE
);