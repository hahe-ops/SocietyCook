from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-secret-key")

# Update these values for your local MySQL setup.
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "societycook")
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        role = request.form["role"]
        society = request.form["society"].strip()

        if role not in ("resident", "cook"):
            flash("Please select a valid account type.")
            return redirect(url_for("register"))

        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (name, email, password_hash, role, society) VALUES (%s,%s,%s,%s,%s)",
                (name, email, generate_password_hash(password), role, society)
            )
            conn.commit()
            user_id = cur.lastrowid
            if role == "cook":
                cur.execute("INSERT INTO cooks (user_id, monthly_fee, available) VALUES (%s,%s,%s)",
                            (user_id, 20000, True))
                conn.commit()
            flash("Registration successful. Please log in.")
            return redirect(url_for("login"))
        except Error as e:
            conn.rollback()
            flash("Could not register. This email may already be registered.")
        finally:
            cur.close()
            conn.close()

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]
            session["society"] = user["society"]
            return redirect(url_for("dashboard"))
        flash("Incorrect email or password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    if session["role"] == "cook":
        cur.execute("""
            SELECT b.id, b.slot_date, b.slot_time, b.status, u.name AS resident_name
            FROM bookings b JOIN users u ON b.resident_id = u.id
            WHERE b.cook_id=%s ORDER BY b.slot_date, b.slot_time
        """, (session["user_id"],))
        bookings = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("dashboard.html", bookings=bookings, cooks=[])

    cur.execute("""
        SELECT c.user_id, u.name, c.monthly_fee, c.available
        FROM cooks c JOIN users u ON c.user_id=u.id
        WHERE u.society=%s AND c.available=1
    """, (session["society"],))
    cooks = cur.fetchall()

    cur.execute("""
        SELECT b.id, b.slot_date, b.slot_time, b.status, u.name AS cook_name
        FROM bookings b JOIN users u ON b.cook_id=u.id
        WHERE b.resident_id=%s ORDER BY b.slot_date, b.slot_time
    """, (session["user_id"],))
    bookings = cur.fetchall()

    # Simple estimate: divide a cook's monthly fee among distinct households
    # that have an active booking with that cook in the same society.
    for cook in cooks:
        cur.execute("""
            SELECT COUNT(DISTINCT b.resident_id) AS households
            FROM bookings b
            JOIN users r ON b.resident_id=r.id
            WHERE b.cook_id=%s AND r.society=%s AND b.status='Confirmed'
        """, (cook["user_id"], session["society"]))
        count = cur.fetchone()["households"]
        cook["share_estimate"] = round(cook["monthly_fee"] / max(count, 1), 2)

    cur.close()
    conn.close()
    return render_template("dashboard.html", bookings=bookings, cooks=cooks)

@app.route("/book/<int:cook_id>", methods=["POST"])
def book(cook_id):
    if "user_id" not in session or session["role"] != "resident":
        return redirect(url_for("login"))

    slot_date = request.form["slot_date"]
    slot_time = request.form["slot_time"]
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT u.society, c.available
        FROM users u JOIN cooks c ON c.user_id=u.id
        WHERE u.id=%s
    """, (cook_id,))
    cook = cur.fetchone()

    if not cook or not cook["available"] or cook["society"] != session["society"]:
        flash("This cook is not available for your society.")
        cur.close()
        conn.close()
        return redirect(url_for("dashboard"))

    cur.execute("""
        SELECT id FROM bookings
        WHERE cook_id=%s AND slot_date=%s AND slot_time=%s AND status='Confirmed'
    """, (cook_id, slot_date, slot_time))
    conflict = cur.fetchone()

    if conflict:
        flash("That cook already has a booking at this date and time.")
    else:
        cur.execute("""
            INSERT INTO bookings (resident_id, cook_id, slot_date, slot_time, status)
            VALUES (%s,%s,%s,%s,'Confirmed')
        """, (session["user_id"], cook_id, slot_date, slot_time))
        conn.commit()
        flash("Booking confirmed.")

    cur.close()
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/cancel/<int:booking_id>", methods=["POST"])
def cancel(booking_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    if session["role"] == "resident":
        cur.execute("UPDATE bookings SET status='Cancelled' WHERE id=%s AND resident_id=%s",
                    (booking_id, session["user_id"]))
    else:
        cur.execute("UPDATE bookings SET status='Cancelled' WHERE id=%s AND cook_id=%s",
                    (booking_id, session["user_id"]))
    conn.commit()
    cur.close()
    conn.close()
    flash("Booking cancelled.")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
