# 📖 Contact Book / Address Manager

A beginner-friendly, multi-page full-stack web application built using **Python (Flask)**, **MySQL**, and clean **HTML/CSS/JavaScript**. 

This project also demonstrates a fundamental Data Structures and Algorithms (**DSA**) concept: **Hashing & Constant-Time O(1) Lookup** using Python Dictionaries.

---

## 📌 Project Overview

The **Contact Book / Address Manager** is designed to help users store, manage, search, update, and categorize contact details efficiently. 

It is built specifically for a college project or viva presentation:
- **No over-engineering:** No heavy frameworks (no React, Next.js, or complex ORMs).
- **Separate HTML Pages:** Every main section (Home, Contacts, Add, Edit, View, Favorites, About) is a distinct HTML page.
- **Easy to Explain:** Clean code, readable variable names, parameterized SQL queries, and detailed comments throughout.

---

## 🚀 Key Features

1. **Dashboard (Home Page):**
   - Live statistics fetched directly from MySQL: Total Contacts, Favorite Contacts, and Total Contact Groups.
   - Quick preview of recently added contacts.
   - Shortcut button to add new contacts.

2. **Multi-Page Navigation:**
   - Common, clean navigation bar on every page.
   - `Home` (`/`), `Contacts` (`/contacts`), `Add Contact` (`/add`), `Favorites` (`/favorites`), and `About` (`/about`).

3. **Complete CRUD Operations (MySQL):**
   - **Create:** Add new contacts with Name, Phone, Email, Address, Group, and Favorite flag.
   - **Read:** View all contacts in a structured table or inspect full details on a dedicated view page (`/contact/<id>`).
   - **Update:** Edit existing contact details with prefilled form inputs (`/edit/<id>`).
   - **Delete:** Delete contacts securely with a JavaScript confirmation dialog.

4. **Search Functionality:**
   - Search contacts dynamically by either **Name** or **Phone Number**.

5. **Favorites Section:**
   - Dedicated page showing starred / favorite contacts only.

6. **Form Validation & Delete Confirmation:**
   - JavaScript validation for empty fields and valid phone numbers.
   - Safe delete confirmation prompt (`"Are you sure you want to delete this contact?"`).

---

## 🛠️ Technologies Used

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript | Pure CSS styling (no Tailwind/Bootstrap), responsive cards, tables, and modal alerts |
| **Backend** | Python 3, Flask | Handles routing, form submissions, and Jinja2 template rendering |
| **Database** | MySQL | Relational database for persistent storage using `mysql-connector-python` |
| **DSA** | Python Dictionary (Hash Table) | Demonstrates average **O(1)** search, insert, and delete operations |

---

## 💡 DSA Concept: Hashing & Fast Lookup

### Why Hashing?
When storing contacts in an unsorted array or list:
- Searching for a contact requires **Linear Search**, which checks every record from start to finish.
- **Time Complexity:** $O(N)$ — if there are 1,000,000 contacts, it can take up to 1,000,000 operations.

### How this project uses Hashing:
In `dsa/contact_hash.py`:
- We map each contact's unique phone number as a **Key** in a **Python Dictionary**.
- Under the hood, Python dictionaries implement a **Hash Table**. A mathematical hash function converts the phone number directly into a memory address.
- **Time Complexity:**
  - **Insertion:** $O(1)$ (Constant time)
  - **Search:** $O(1)$ (Constant time)
  - **Deletion:** $O(1)$ (Constant time)

Even if the contact list grows to millions of records, phone lookups take only **1 operation on average**.

> **Viva Tip:** You can run the DSA demo directly in the terminal to demonstrate hashing to your teacher:
> ```bash
> python dsa/contact_hash.py
> ```

---

## 🗄️ Database Structure

### Database: `contact_book`
### Table: `contacts`

| Column | Data Type | Description |
| :--- | :--- | :--- |
| `id` | `INT PRIMARY KEY AUTO_INCREMENT` | Unique identifier for each contact |
| `name` | `VARCHAR(100) NOT NULL` | Full name of the contact |
| `phone` | `VARCHAR(20) NOT NULL` | Phone number |
| `email` | `VARCHAR(100)` | Email address |
| `address` | `VARCHAR(255)` | Postal address |
| `group_name` | `VARCHAR(50)` | Group category (e.g. Family, Friends, Work, College) |
| `favorite` | `BOOLEAN DEFAULT FALSE` | 1 if starred/favorite, 0 otherwise |
| `created_at` | `DATETIME DEFAULT CURRENT_TIMESTAMP` | Timestamp when contact was added |

---

## 📂 Project Structure

```text
ContactBook/
│
├── app.py                  # Main Flask application and URL routes
├── database.py             # MySQL connection and table creation script
├── requirements.txt        # Required Python packages
├── README.md               # Project documentation and guide
│
├── templates/              # Separate HTML page templates
│   ├── index.html          # 1. Home / Dashboard
│   ├── contacts.html       # 2. All Contacts & Search
│   ├── add_contact.html    # 3. Add New Contact Form
│   ├── edit_contact.html   # 4. Edit Contact Form
│   ├── contact_details.html# 5. Full Contact Details View
│   ├── favorites.html      # 6. Starred Favorite Contacts
│   └── about.html          # 7. About Project & Tech Stack
│
├── static/
│   ├── css/
│   │   └── style.css       # Clean, modern CSS styling
│   └── js/
│       └── script.js       # Delete confirmation and form validation
│
└── dsa/
    └── contact_hash.py     # Python Dictionary Hashing implementation
```

---

## ⚙️ How to Configure & Run the Project

### 1. Prerequisites
Make sure you have installed:
- **Python 3.8+**
- **MySQL Server** (via MySQL Server, MySQL Workbench, or XAMPP)

---

### 2. Configure MySQL Password (Important!)
Open `database.py` in any text editor and check lines 15-18:

```python
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "YOUR_MYSQL_PASSWORD_HERE"  # <-- If your root password is empty, keep ""
DB_NAME = "contact_book"
```

> **Note:** The application **automatically creates** the database `contact_book` and table `contacts` with sample contacts on its first run! You do not need to manually write SQL `CREATE DATABASE` queries.

---

### 3. Install Dependencies
Open your terminal or command prompt inside the `ContactBook` directory and run:

```bash
pip install -r requirements.txt
```

---

### 4. Run the Application
Start the Flask web server:

```bash
python app.py
```

You should see output similar to:
```text
============================================================
Starting Contact Book Application...
Checking and Initializing MySQL Database...
[SUCCESS] MySQL Database & Table initialized successfully.
Loading Contacts into DSA Hash Table...
============================================================
* Running on http://127.0.0.1:5000
```

---

### 5. Open in Web Browser
Open your browser and visit:
👉 **`http://127.0.0.1:5000`**

You can now:
- View dashboard metrics.
- Navigate to **Contacts** to see the list.
- Click **+ Add Contact** to add new people.
- Star contacts as **Favorites**.
- Search by name or phone number.
- Edit or delete contacts.

---

## 🎓 Sample College Viva Questions & Answers

**Q1: What architecture does this project follow?**  
> *Answer:* It follows a simple Model-View-Controller (MVC) style full-stack architecture using Python Flask. Flask routes act as controllers, MySQL acts as the model/storage, and HTML templates rendered via Jinja2 serve as the view.

**Q2: How does the application prevent SQL Injection?**  
> *Answer:* We use parameterized queries with `%s` placeholders (e.g. `cursor.execute("SELECT * FROM contacts WHERE id = %s", (id,))`). The MySQL driver automatically sanitizes the input parameters.

**Q3: How does the DSA Hashing component work?**  
> *Answer:* In `dsa/contact_hash.py`, contacts are stored in a Python dictionary with the phone number as the key. Python dictionaries use internal hash tables to compute memory buckets, providing average $O(1)$ constant-time lookup, as opposed to $O(N)$ linear search.

**Q4: Why did you not use React or single-page architecture?**  
> *Answer:* A traditional multi-page architecture with separate HTML pages and standard HTTP GET/POST routes was chosen to keep the code simple, clean, and easily understandable without extra framework overhead.

---

## 🔮 Future Improvements

1. Export contacts to CSV or PDF format.
2. Profile picture upload support for contacts.
3. Import contacts from Google Contacts (vCard format).
4. Sorting options (sort by newest, group, or alphabetical order).
