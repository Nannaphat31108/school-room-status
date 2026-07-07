from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# --------------------------
# รายชื่ออาคารและห้องเรียน
# --------------------------
buildings = {
    "อาคาร 4": ["411", "412", "413", "414", "415"],
    "อาคาร 5": ["511", "512", "513", "514", "515"]
}


# --------------------------
# เชื่อมต่อฐานข้อมูล
# --------------------------
def connect_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------
# สร้างฐานข้อมูลครั้งแรก
# --------------------------
def create_table():

    conn = connect_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS booking(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        building TEXT,

        room TEXT,

        name TEXT,

        date TEXT,

        start_time TEXT,

        end_time TEXT

    )
    """)

    conn.commit()
    conn.close()


create_table()


# --------------------------
# หน้าแรก
# --------------------------
@app.route("/")
def home():

    return render_template(
        "index.html",
        buildings=buildings
    )


# --------------------------
# แสดงห้อง
# --------------------------
@app.route("/building/<building>")
def rooms(building):

    conn = connect_db()

    room_list = []

    for room in buildings.get(building, []):

        book = conn.execute(
            "SELECT * FROM booking WHERE building=? AND room=?",
            (building, room)
        ).fetchone()

        if book:

            room_list.append({

                "room": room,

                "status": "ไม่ว่าง",

                "name": book["name"]

            })

        else:

            room_list.append({

                "room": room,

                "status": "ว่าง",

                "name": "-"

            })

    conn.close()

    return render_template(

        "rooms.html",

        building=building,

        rooms=room_list

    )


# --------------------------
# จองห้อง
# --------------------------
@app.route("/booking/<building>/<room>", methods=["GET", "POST"])
def booking(building, room):

    if request.method == "POST":

        name = request.form["name"]

        date = request.form["date"]

        start = request.form["start"]

        end = request.form["end"]

        conn = connect_db()

        conn.execute("""

        INSERT INTO booking

        (building,room,name,date,start_time,end_time)

        VALUES(?,?,?,?,?,?)

        """,

        (

            building,

            room,

            name,

            date,

            start,

            end

        ))

        conn.commit()

        conn.close()

        return redirect(

            url_for(

                "rooms",

                building=building

            )

        )

    return render_template(

        "booking.html",

        building=building,

        room=room

    )


# --------------------------
# รายการจองทั้งหมด
# --------------------------
@app.route("/bookings")
def bookings():

    conn = connect_db()

    data = conn.execute(

        "SELECT * FROM booking"

    ).fetchall()

    conn.close()

    return render_template(

        "bookings.html",

        bookings=data

    )


# --------------------------
# ยกเลิกการจอง
# --------------------------
@app.route("/delete/<int:id>")
def delete(id):

    conn = connect_db()

    conn.execute(

        "DELETE FROM booking WHERE id=?",

        (id,)

    )

    conn.commit()

    conn.close()

    return redirect("/bookings")


# --------------------------
# เริ่มระบบ
# --------------------------
import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)