from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# --------------------------
# รายชื่ออาคารและห้องเรียน
# --------------------------
buildings = {
    "อาคาร 3": [
        "311","312","313","314","315",
        "321","322","323","324","325",
        "331","332","333","334","335"
    ],

    "อาคาร 5": [
        "511","512","513","514","515","516","517","518",
        "521","522","523","524","525","526","527","528",
        "531","532","533","534","535","536","537","538"
    ],

    "อาคาร 6": [
        "611","612","613","614","615","616","617","618",
        "621","622","623","624","625","626","627","628",
        "631","632","633","634","635","636","637","638"
    ]
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
    rooms=room_list,
    today=thai_date()
    )


# --------------------------
# จองห้อง
# --------------------------
@app.route("/booking/<building>/<room>", methods=["GET", "POST"])
def booking(building, room):

    if request.method == "POST":

        name = request.form["name"]

        date = thai_date()

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
    room=room,
    today=thai_date()
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
    
from datetime import datetime

today = datetime.now().strftime("%d/%m/%Y")
def thai_date():
    months = [
        "",
        "มกราคม", "กุมภาพันธ์", "มีนาคม",
        "เมษายน", "พฤษภาคม", "มิถุนายน",
        "กรกฎาคม", "สิงหาคม", "กันยายน",
        "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]

    now = datetime.now()

    day = now.day
    month = months[now.month]
    year = now.year + 543

    return f"{day} {month} {year}"
