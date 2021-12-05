from flask import Flask, render_template, request, flash, redirect, url_for
import sqlite3
import hashids

app = Flask(__name__)
app.config['SECRET_KEY'] = "your_own_secret_key"

hashids = hashids.Hashids(min_length=4, salt="<your_own_salt>")

def connect_to_db():
    conn = sqlite3.connect('urlShortener/database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/",methods=["GET","POST"])
def home():
    if request.method == "POST":
        conn = connect_to_db()
        original_url = request.form["original_url"]
        if "new_url_back" in request.form:
            new_url_back = request.form["new_url_back"]
        else:
            conn.execute('SELECT COUNT(*) FROM urls;')
            rows = conn.fetchone()[0]
            new_url_back = hashids.encode(rows)
        short_url = request.host_url + new_url_back
        url_check = conn.execute('SELECT original_url FROM urls WHERE short_url = (?)', (short_url,)).fetchone()
        if url_check:
            return render_template("index.html",error_msg="Custom URL pattern is already in use, please choose a different custom URL pattern!")
        else:
            conn.execute('INSERT INTO urls (original_url,short_url) VALUES (?,?)',(original_url,short_url))
            conn.commit()
            conn.close()
            
            return render_template("index.html",short_url=short_url)
    return render_template("index.html")

@app.route('/<pattern>')
def url_redirect(pattern):
    conn = connect_to_db()
    url = request.host_url + pattern
    url_data = conn.execute('SELECT original_url FROM urls WHERE short_url = (?)', (url,)).fetchone()[0]
    if url_data:
        original_url = url_data
    else:
        flash("URL not shortened")
        return redirect(url_for('home'))

    conn.commit()
    conn.close()
    return redirect(original_url)
    