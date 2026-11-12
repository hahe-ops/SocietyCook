# SocietyCook; Shared Cooking Service Management System
SocietyCook is a small college-project prototype built with **Python, Flask, MySQL, HTML and CSS**.
It demonstrates how residents in the same housing society can find a cook, book cooking slots and manage bookings. Cooks can log in to view their assigned bookings.
## Features

- Resident and cook registration
- Login and logout
- Cook list for residents in the same society
- Cooking-slot booking
- Basic prevention of double-booking
- View and cancel bookings
- Simple estimated cost sharing

## Project structure
SocietyCook/
├── app.py
├── schema.sql
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
└── static/
    └── style.css

## Requirements
- Python 3.10 or newer
- MySQL Server
- A web browser

## Setup instructions
### 1. Create the database

Open MySQL Workbench or the MySQL command line and run the contents of `schema.sql`.

### 2. Install Python packages

Open a terminal in the project folder:
python -m venv venv

Activate the environment:

**Windows**
venv\Scripts\activate

Then install dependencies:
pip install -r requirements.txt

### 3. Configure MySQL

The default settings in `app.py` are:

- Host: `localhost`
- User: `root`
- Password: empty
- Database: `societycook`

If your MySQL password is not empty, set the `DB_PASSWORD` environment variable before running the app.

**Windows Command Prompt**
set DB_PASSWORD=your_mysql_password

**PowerShell**
$env:DB_PASSWORD="your_mysql_password"

### 4. Run the application
python app.py
Open this address in your browser:
http://127.0.0.1:5000

## How to test

1. Register one account with the role **Cook**. Enter a society name, for example `Green Residency`.
2. Log out and register one or more **Resident** accounts using exactly the same society name.
3. Log in as a resident.
4. Choose a cook, select a date and time, and book a slot.
5. Log in as the cook to see the booking.
6. Try booking the same cook at the same date and time from another resident account. The application should reject the duplicate slot.

## Notes and limitations

- This is an educational prototype, not a production-ready service.
- Payments are not processed. The cost-sharing figure is only an estimate based on confirmed bookings.
- Cook availability is a simple on/off setting in the database; there is no separate availability calendar yet.
- The prototype uses a basic role system and does not include a separate administrator dashboard.
- For real deployment, add stronger security, CSRF protection, input validation, admin controls, privacy safeguards and proper worker-verification processes.
- Change the Flask secret key before deployment. Do not publish database passwords or secret keys on GitHub.

## Author
Ananya Garg
