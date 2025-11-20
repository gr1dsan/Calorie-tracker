from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
import datetime

app = Flask(__name__)
app.secret_key = "super_secret_key"

db = pymysql.connect(
    host="localhost",
    user="your_user",
    password="your_password",
    database="c_t",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=False
)

def require_login():
    return 'user_id' in session


@app.route('/', methods=['GET'])
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()

        if not user or user['password'] != password:
            flash("Incorrect username or password", "danger")
            return render_template('login.html')

        session['user_id'] = user['user_id']
        session['username'] = user['username']

        return redirect(url_for('main'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        try:
            with db.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s)",
                    (username, password)
                )
            db.commit()
            flash("Registered successfully — please log in", "success")
            return redirect(url_for('login'))

        except pymysql.err.IntegrityError:
            db.rollback()
            flash("Username already exists", "danger")
            return render_template('register.html')

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if not require_login():
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        old = request.form.get('old_password')
        new = request.form.get('new_password')
        confirm = request.form.get('confirm_password')

        if not old or not new or not confirm:
            flash("All fields must be filled.", "danger")
            return render_template('edit_profile.html')

        if new != confirm:
            flash("New passwords do not match", "danger")
            return render_template('edit_profile.html')

        with db.cursor() as cursor:
            cursor.execute("SELECT password FROM users WHERE user_id=%s", (user_id,))
            row = cursor.fetchone()

        if not row or row['password'] != old:
            flash("Old password is incorrect", "danger")
            return render_template('edit_profile.html')

        with db.cursor() as cursor:
            cursor.execute("UPDATE users SET password=%s WHERE user_id=%s", (new, user_id))
        db.commit()

        flash("Password updated successfully", "success")
        return redirect(url_for('main'))

    return render_template('edit_profile.html')


@app.route('/instructions')
def instructions():
    if not require_login():
        return redirect(url_for('login'))
    return render_template('instructions.html')


@app.route('/main', methods=['GET', 'POST'])
def main():
    if not require_login():
        return redirect(url_for('login'))

    user_id = session['user_id']
    username = session.get('username', 'User')

    if request.method == 'POST':
        date = request.form.get('current_date') or request.form.get('date')
        if not date:
            date = datetime.date.today().isoformat()
    else:
        date = datetime.date.today().isoformat()

    if request.method == 'POST' and request.form.get('form_type') == 'add_food':

        try:
            food_name = request.form.get('food_name', '').strip()
            food_calories = float(request.form.get('food_calories') or 0)
            food_protein = float(request.form.get('food_protein') or 0)
            food_carbs = float(request.form.get('food_carbohydrants') or 0)
            food_fats = float(request.form.get('food_fats') or 0)

            with db.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO food_track "
                    "(food_name, date_added, calories, protein, carbohydrants, fats, user_id) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (food_name, date, food_calories, food_protein, food_carbs, food_fats, user_id)
                )
            db.commit()
            flash("Food added", "success")

        except Exception:
            db.rollback()
            flash("Error adding food", "danger")

    if request.method == 'POST' and request.form.get('form_type') == 'action':

        action = request.form.get('action')
        food_id = request.form.get('food_id')
        table = request.form.get('table', 'food_track')

        try:
            with db.cursor() as cursor:

                if action == 'delete':
                    if table == 'food_track':
                        cursor.execute("DELETE FROM food_track WHERE id=%s AND user_id=%s", (food_id, user_id))
                    elif table == 'food_db':
                        cursor.execute("DELETE FROM food_db WHERE id=%s AND user_id=%s", (food_id, user_id))

                elif action == 'save' and table == 'food_track':
                    cursor.execute(
                        "INSERT INTO food_db (food_name, calories, protein, carbohydrants, fats, user_id) "
                        "SELECT food_name, calories, protein, carbohydrants, fats, user_id "
                        "FROM food_track WHERE id=%s AND user_id=%s",
                        (food_id, user_id)
                    )

            db.commit()
            flash("Action completed", "success")

        except Exception:
            db.rollback()
            flash("Action failed", "danger")

    with db.cursor() as cursor:

        cursor.execute(
            "SELECT * FROM food_track WHERE date_added=%s AND user_id=%s ORDER BY id DESC",
            (date, user_id)
        )
        foods = cursor.fetchall()

        totals = {
            'calories': round(sum(float(f['calories'] or 0) for f in foods), 2),
            'protein': round(sum(float(f['protein'] or 0) for f in foods), 2),
            'carbs': round(sum(float(f['carbohydrants'] or 0) for f in foods), 2),
            'fats': round(sum(float(f['fats'] or 0) for f in foods), 2)
        }

        cursor.execute(
            "SELECT id, food_name, calories, protein, carbohydrants, fats "
            "FROM food_db WHERE user_id=%s ORDER BY food_name",
            (user_id,)
        )
        saved_foods = cursor.fetchall()

    return render_template(
        "index.html",
        username=username,
        date=date,
        foods=foods,
        totals=totals,
        saved_foods=saved_foods
    )


if __name__ == '__main__':
    app.run(debug=True)
