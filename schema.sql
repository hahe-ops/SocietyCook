CREATE DATABASE IF NOT EXISTS societycook;
USE societycook;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('resident', 'cook') NOT NULL,
    society VARCHAR(150) NOT NULL
);

CREATE TABLE IF NOT EXISTS cooks (
    user_id INT PRIMARY KEY,
    monthly_fee DECIMAL(10,2) NOT NULL DEFAULT 20000,
    available BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resident_id INT NOT NULL,
    cook_id INT NOT NULL,
    slot_date DATE NOT NULL,
    slot_time TIME NOT NULL,
    status ENUM('Confirmed', 'Cancelled') NOT NULL DEFAULT 'Confirmed',
    FOREIGN KEY (resident_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (cook_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_cook_slot (cook_id, slot_date, slot_time)
);
