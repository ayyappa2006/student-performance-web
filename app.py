@app.route('/admin')
def admin():
    conn = sqlite3.connect('students.db')
    data = conn.execute("SELECT * FROM records").fetchall()
    conn.close()

    total = len(data)
    avg_attendance = sum([row[3] for row in data]) / total if total else 0

    return render_template('admin.html',
                           total=total,
                           avg_attendance=avg_attendance,
                           records=data)
