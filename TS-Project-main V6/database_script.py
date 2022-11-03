import sqlite3


def execute_userinfo(command):
    connection = sqlite3.connect("userinfo_db.db")
    cur = connection.cursor()
    cur.execute(command)
    connection.commit()
    connection.close()


def view_userinfo():
    connection = sqlite3.connect("userinfo_db.db")
    cur = connection.cursor()
    cur.execute("SELECT * FROM userinfo")
    rows = cur.fetchall()
    # print(rows)
    connection.close()
    return rows

def view_posts():
    connection = sqlite3.connect("userinfo_db.db")
    cur = connection.cursor()
    cur.execute("SELECT * FROM posts")
    rows = cur.fetchall()
    print(rows)
    connection.close()
    return rows