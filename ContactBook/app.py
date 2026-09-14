# ==============================================================================
# CONTACT BOOK / ADDRESS MANAGER - MAIN FLASK APPLICATION
# ==============================================================================
# This is the main backend file for the project.
# It defines all routes (URLs), connects with MySQL, and coordinates with
# the DSA Hashing module for fast lookups.
# Designed to be simple, clean, and easy to explain in a college viva.
# ==============================================================================

from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import sys
import os

# Import our custom database functions
from database import get_db_connection, init_database

# Import our DSA Hashing module
from dsa.contact_hash import (
    add_contact_to_hash, 
    search_contact, 
    delete_contact_from_hash,
    load_contacts_to_hash
)

# Initialize the Flask application
app = Flask(__name__)

# Secret key required for session management and flash messages
app.secret_key = "contact_book_college_project_secret_key"


# ==============================================================================
# 0. AUTHENTICATION HELPERS & CONTEXT PROCESSOR
# ==============================================================================
@app.context_processor
def inject_user():
    """Provides current user authentication status to all Jinja templates."""
    return {
        "current_user": session.get("username"),
        "is_logged_in": "user_id" in session
    }


def login_required(f):
    """
    Decorator to protect routes requiring authentication.
    Redirects unauthenticated visitors to the login page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login_page", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


# ==============================================================================
# 1. HELPER FUNCTION: SYNC DATABASE TO DSA HASH TABLE
# ==============================================================================
def refresh_dsa_cache():
    """
    Fetches all contacts from MySQL and stores them in the in-memory
    Python dictionary (DSA Hash Table) for instant O(1) phone lookups.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM contacts")
            all_contacts = cursor.fetchall()
            load_contacts_to_hash(all_contacts)
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"[WARNING] Could not refresh DSA hash table: {e}")


# ==============================================================================
# 2. ROUTE: HOME / DASHBOARD (GET /)
# ==============================================================================
@app.route("/")
@login_required
def home():
    """
    Renders the Dashboard (index.html).
    Fetches real-time statistics and recently added contacts from MySQL.
    """
    conn = get_db_connection()
    if not conn:
        flash("Could not connect to MySQL database. Please check your credentials in database.py.", "danger")
        return render_template(
            "index.html", 
            total_contacts=0, 
            total_favorites=0, 
            total_groups=0, 
            recent_contacts=[]
        )

    try:
        cursor = conn.cursor(dictionary=True)

        # Query 1: Total Contacts Count
        cursor.execute("SELECT COUNT(*) AS total FROM contacts")
        total_contacts = cursor.fetchone()["total"]

        # Query 2: Favorite Contacts Count
        cursor.execute("SELECT COUNT(*) AS total FROM contacts WHERE favorite = 1")
        total_favorites = cursor.fetchone()["total"]

        # Query 3: Total Unique Groups Count
        cursor.execute("SELECT COUNT(DISTINCT group_name) AS total FROM contacts WHERE group_name IS NOT NULL AND group_name != ''")
        total_groups = cursor.fetchone()["total"]

        # Query 4: 5 Most Recently Added Contacts
        cursor.execute("SELECT * FROM contacts ORDER BY id DESC LIMIT 5")
        recent_contacts = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template(
            "index.html",
            total_contacts=total_contacts,
            total_favorites=total_favorites,
            total_groups=total_groups,
            recent_contacts=recent_contacts
        )

    except Exception as e:
        flash(f"Error fetching dashboard data: {e}", "danger")
        return render_template(
            "index.html", 
            total_contacts=0, 
            total_favorites=0, 
            total_groups=0, 
            recent_contacts=[]
        )


# ==============================================================================
# 3. ROUTE: ALL CONTACTS & SEARCH (GET /contacts)
# ==============================================================================
@app.route("/contacts")
@login_required
def contacts_page():
    """
    Renders the Contacts page (contacts.html).
    Supports searching by name or phone number via '?search=...'.
    """
    search_query = request.args.get("search", "").strip()

    conn = get_db_connection()
    if not conn:
        flash("Could not connect to MySQL database.", "danger")
        return render_template("contacts.html", contacts=[], search_query=search_query)

    try:
        cursor = conn.cursor(dictionary=True)

        if search_query:
            # SQL parameterized query to search by name or phone
            query = """
            SELECT * FROM contacts 
            WHERE name LIKE %s OR phone LIKE %s 
            ORDER BY name ASC
            """
            search_param = f"%{search_query}%"
            cursor.execute(query, (search_param, search_param))
        else:
            # Fetch all contacts alphabetically by name
            cursor.execute("SELECT * FROM contacts ORDER BY name ASC")

        contacts = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template("contacts.html", contacts=contacts, search_query=search_query)

    except Exception as e:
        flash(f"Error fetching contacts: {e}", "danger")
        return render_template("contacts.html", contacts=[], search_query=search_query)


# ==============================================================================
# 4. ROUTE: ADD CONTACT (GET /add & POST /add)
# ==============================================================================
@app.route("/add", methods=["GET", "POST"])
@login_required
def add_contact():
    """
    GET: Displays the Add Contact form (add_contact.html).
    POST: Validates inputs, checks for duplicates, and inserts a new contact.
    """
    if request.method == "POST":
        # Extract inputs from form
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()
        group_name = request.form.get("group_name", "General").strip()
        favorite = 1 if request.form.get("favorite") else 0

        form_data = {
            "name": name,
            "phone": phone,
            "email": email,
            "address": address,
            "group_name": group_name,
            "favorite": favorite
        }

        # 1. Basic Backend Validation
        if not name:
            flash("Contact name is required!", "danger")
            return render_template("add_contact.html", **form_data)

        if not phone:
            flash("Phone number is required!", "danger")
            return render_template("add_contact.html", **form_data)

        # 2. Check that phone contains valid digits
        clean_phone = phone.replace("+", "").replace("-", "").replace(" ", "")
        if not clean_phone.isdigit() or len(clean_phone) < 7:
            flash("Please enter a valid phone number (at least 7 digits)!", "danger")
            return render_template("add_contact.html", **form_data)

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed. Could not save contact.", "danger")
            return render_template("add_contact.html", **form_data)

        try:
            cursor = conn.cursor(dictionary=True)

            # 3. Check for Duplicate Phone Number
            cursor.execute("SELECT id, name FROM contacts WHERE phone = %s", (phone,))
            duplicate = cursor.fetchone()
            if duplicate:
                cursor.close()
                conn.close()
                flash(f"A contact with phone '{phone}' already exists ({duplicate['name']})!", "warning")
                return render_template("add_contact.html", **form_data)

            # 4. Insert query with parameterized values
            insert_query = """
            INSERT INTO contacts (name, phone, email, address, group_name, favorite)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (name, phone, email, address, group_name, favorite))
            conn.commit()

            # Add to DSA Hash Table for instant memory lookup
            add_contact_to_hash(phone, {
                "name": name, 
                "phone": phone, 
                "email": email, 
                "address": address, 
                "group_name": group_name, 
                "favorite": favorite
            })

            cursor.close()
            conn.close()

            flash(f"Contact '{name}' added successfully!", "success")
            return redirect(url_for("contacts_page"))

        except Exception as e:
            flash(f"Database error while saving contact: {e}", "danger")
            return render_template("add_contact.html", **form_data)

    # GET request: Show empty add contact form
    return render_template("add_contact.html")


# ==============================================================================
# 5. ROUTE: EDIT CONTACT (GET /edit/<id> & POST /edit/<id>)
# ==============================================================================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_contact(id):
    """
    GET: Loads contact data from MySQL and renders edit_contact.html.
    POST: Validates inputs, checks for duplicates, and updates the contact.
    """
    conn = get_db_connection()
    if not conn:
        flash("Could not connect to MySQL database.", "danger")
        return redirect(url_for("contacts_page"))

    if request.method == "POST":
        # Extract modified fields from form
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()
        group_name = request.form.get("group_name", "General").strip()
        favorite = 1 if request.form.get("favorite") else 0

        # Construct updated contact dict in case validation fails
        contact_data = {
            "id": id,
            "name": name,
            "phone": phone,
            "email": email,
            "address": address,
            "group_name": group_name,
            "favorite": favorite
        }

        # 1. Basic Validation
        if not name or not phone:
            flash("Name and Phone number are required fields!", "danger")
            conn.close()
            return render_template("edit_contact.html", contact=contact_data)

        # 2. Phone format validation
        clean_phone = phone.replace("+", "").replace("-", "").replace(" ", "")
        if not clean_phone.isdigit() or len(clean_phone) < 7:
            flash("Please enter a valid phone number (at least 7 digits)!", "danger")
            conn.close()
            return render_template("edit_contact.html", contact=contact_data)

        try:
            cursor = conn.cursor(dictionary=True)

            # 3. Check for Duplicate Phone Number on other contacts
            cursor.execute("SELECT id, name FROM contacts WHERE phone = %s AND id != %s", (phone, id))
            duplicate = cursor.fetchone()
            if duplicate:
                cursor.close()
                conn.close()
                flash(f"Another contact '{duplicate['name']}' already uses phone number '{phone}'!", "warning")
                return render_template("edit_contact.html", contact=contact_data)

            update_query = """
            UPDATE contacts 
            SET name = %s, phone = %s, email = %s, address = %s, group_name = %s, favorite = %s
            WHERE id = %s
            """
            cursor.execute(update_query, (name, phone, email, address, group_name, favorite, id))
            conn.commit()

            cursor.close()
            conn.close()

            # Refresh DSA cache
            refresh_dsa_cache()

            flash(f"Contact '{name}' updated successfully!", "success")
            return redirect(url_for("contacts_page"))

        except Exception as e:
            flash(f"Error updating contact: {e}", "danger")
            conn.close()
            return redirect(url_for("contacts_page"))

    # GET request: Safely fetch existing contact details to prefill the form
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (id,))
        contact = cursor.fetchone()
        cursor.close()
        conn.close()

        if not contact:
            flash("Contact not found!", "danger")
            return redirect(url_for("contacts_page"))

        return render_template("edit_contact.html", contact=contact)

    except Exception as e:
        flash(f"Error fetching contact details: {e}", "danger")
        conn.close()
        return redirect(url_for("contacts_page"))


# ==============================================================================
# 6. ROUTE: CONTACT DETAILS (GET /contact/<id>)
# ==============================================================================
@app.route("/contact/<int:id>")
@login_required
def contact_details(id):
    """
    Renders the full contact details page (contact_details.html).
    """
    conn = get_db_connection()
    if not conn:
        flash("Could not connect to MySQL database.", "danger")
        return redirect(url_for("contacts_page"))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (id,))
        contact = cursor.fetchone()
        cursor.close()
        conn.close()

        if not contact:
            flash("Contact not found!", "danger")
            return redirect(url_for("contacts_page"))

        return render_template("contact_details.html", contact=contact)

    except Exception as e:
        flash(f"Error loading contact details: {e}", "danger")
        return redirect(url_for("contacts_page"))


# ==============================================================================
# 7. ROUTE: DELETE CONTACT (POST /delete/<id>)
# ==============================================================================
@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_contact(id):
    """
    Deletes a contact from MySQL database and updates the DSA Hash Table.
    Uses POST method for security.
    """
    conn = get_db_connection()
    if not conn:
        flash("Could not connect to MySQL database.", "danger")
        return redirect(url_for("contacts_page"))

    try:
        cursor = conn.cursor(dictionary=True)

        # Get contact phone first to remove from DSA hash table
        cursor.execute("SELECT name, phone FROM contacts WHERE id = %s", (id,))
        contact = cursor.fetchone()

        if contact:
            # Delete from MySQL
            cursor.execute("DELETE FROM contacts WHERE id = %s", (id,))
            conn.commit()

            # Delete from DSA Hash Table
            if contact["phone"]:
                delete_contact_from_hash(contact["phone"])

            flash(f"Contact '{contact['name']}' deleted successfully.", "success")
        else:
            flash("Contact not found.", "warning")

        cursor.close()
        conn.close()

    except Exception as e:
        flash(f"Error deleting contact: {e}", "danger")

    return redirect(url_for("contacts_page"))


# ==============================================================================
# 8. ROUTE: FAVORITES PAGE (GET /favorites)
# ==============================================================================
@app.route("/favorites")
@login_required
def favorites_page():
    """
    Renders the Favorites page (favorites.html).
    Shows only contacts where favorite = 1.
    """
    conn = get_db_connection()
    if not conn:
        flash("Could not connect to MySQL database.", "danger")
        return render_template("favorites.html", favorites=[])

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM contacts WHERE favorite = 1 ORDER BY name ASC")
        favorites = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template("favorites.html", favorites=favorites)

    except Exception as e:
        flash(f"Error fetching favorites: {e}", "danger")
        return render_template("favorites.html", favorites=[])


# ==============================================================================
# 9. ROUTE: ABOUT PAGE (GET /about)
# ==============================================================================
@app.route("/about")
def about_page():
    """
    Renders the About page (about.html).
    Explains the project tech stack, purpose, and DSA concept.
    """
    return render_template("about.html")


# ==============================================================================
# 10. AUTHENTICATION ROUTES: LOGIN, REGISTER, LOGOUT
# ==============================================================================
@app.route("/login", methods=["GET", "POST"])
def login_page():
    """
    User login route.
    Validates username and password against users table using password hash checking.
    """
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please provide both username and password.", "danger")
            return render_template("login.html", username=username)

        conn = get_db_connection()
        if not conn:
            flash("Database connection error. Please try again.", "danger")
            return render_template("login.html", username=username)

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user and check_password_hash(user["password_hash"], password):
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                flash(f"Welcome back, {user['username']}! Logged in successfully.", "success")
                next_url = request.args.get("next")
                if next_url and next_url.startswith("/"):
                    return redirect(next_url)
                return redirect(url_for("home"))
            else:
                flash("Invalid username or password. Please try again.", "danger")
                return render_template("login.html", username=username)

        except Exception as e:
            flash(f"Login error: {e}", "danger")
            return render_template("login.html", username=username)

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register_page():
    """
    User registration route.
    Validates password confirmation, uniqueness of username, and saves hashed password.
    """
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return render_template("register.html", username=username)

        if len(username) < 3:
            flash("Username must be at least 3 characters long.", "warning")
            return render_template("register.html", username=username)

        if len(password) < 4:
            flash("Password must be at least 4 characters long.", "warning")
            return render_template("register.html", username=username)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html", username=username)

        conn = get_db_connection()
        if not conn:
            flash("Database connection error. Please try again.", "danger")
            return render_template("register.html", username=username)

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            existing = cursor.fetchone()

            if existing:
                cursor.close()
                conn.close()
                flash("Username is already taken. Please choose another or login.", "warning")
                return render_template("register.html", username=username)

            pwd_hash = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, pwd_hash)
            )
            conn.commit()
            cursor.close()
            conn.close()

            flash("Account registered successfully! You can now log in.", "success")
            return redirect(url_for("login_page"))

        except Exception as e:
            flash(f"Registration error: {e}", "danger")
            return render_template("register.html", username=username)

    return render_template("register.html")


@app.route("/logout")
def logout():
    """Logs the user out and clears the session."""
    user = session.pop("username", None)
    session.pop("user_id", None)
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login_page"))



# ==============================================================================
# APPLICATION ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Starting Contact Book Application...")
    print("Checking and Initializing MySQL Database...")
    init_database()

    print("Loading Contacts into DSA Hash Table...")
    refresh_dsa_cache()
    print("=" * 60)

    # Run the Flask local development server
    # debug=True allows automatic code reloading and helpful error messages
    app.run(debug=True, port=5000)
