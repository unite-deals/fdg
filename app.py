import streamlit as st
import sqlite3

# ---------- DB ----------
conn = sqlite3.connect("voting.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    voted INTEGER DEFAULT 0
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS votes (
    option TEXT
)
""")

conn.commit()

# ---------- Functions ----------
def register(username, password):
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except:
        return False

def login(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return c.fetchone()

def vote(username, option):
    c.execute("SELECT voted FROM users WHERE username=?", (username,))
    if c.fetchone()[0] == 1:
        return False

    c.execute("INSERT INTO votes (option) VALUES (?)", (option,))
    c.execute("UPDATE users SET voted=1 WHERE username=?", (username,))
    conn.commit()
    return True

def results():
    c.execute("SELECT option, COUNT(*) FROM votes GROUP BY option")
    return dict(c.fetchall())

def total_votes():
    c.execute("SELECT COUNT(*) FROM votes")
    return c.fetchone()[0]

# ---------- UI ----------
st.title("নির্বাচনের সম্ভাব্য ফলাফল অনলাইনে যাচাই করুন")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

# Register
if choice == "Register":
    st.subheader("Register")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Register"):
        if register(u, p):
            st.success("Registered!")
        else:
            st.error("User exists")

# Login
if choice == "Login":
    st.subheader("Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if login(u, p):
            st.session_state.user = u
            st.success("Logged in")
        else:
            st.error("Invalid login")

# Voting
if "user" in st.session_state:
    st.write(f"Welcome {st.session_state.user}")

    option = st.radio("Vote করুন:", ["Party A", "Party B", "Party C"])

    if st.button("Vote"):
        if vote(st.session_state.user, option):
            st.success("Vote submitted")
        else:
            st.warning("Already voted")

    st.subheader("Results")
    res = results()

    for k in ["Party A", "Party B", "Party C"]:
        st.write(f"{k}: {res.get(k, 0)}")

    st.subheader(f"মোট ভোট: {total_votes()}")

    if st.button("Logout"):
        del st.session_state.user