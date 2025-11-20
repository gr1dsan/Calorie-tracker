# Calorie Tracker App

A simple web app to track your daily food intake and calories. Built with **Python**, **Flask** and **MySQL**.  

---

### 1. Clone the Repository
```bash
git clone https://github.com/gr1dsan/Calorie-tracker.git
cd Calorie-tracker
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
```

Activate it:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up MySQL Database

1. Start your MySQL server.

2. Create a database:
```bash
CREATE DATABASE c_t;
```

3. Import initial SQL schema:
```bash
mysql -u root -p c_t < db.sql
```

### 5. Configure Environment Variables

Change this part of the code according to your database configurations.

```bash
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=c_t
```

### 6. Run the app
```bash
python app.py
```
