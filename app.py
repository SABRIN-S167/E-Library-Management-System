import streamlit as st, sqlite3
from pathlib import Path
DB=Path(__file__).parent/"elibrary.db"
def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,role TEXT DEFAULT 'Reader');
        CREATE TABLE IF NOT EXISTS ebooks(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,author TEXT,category TEXT,description TEXT,resource_url TEXT,access_level TEXT DEFAULT 'Open');
        CREATE TABLE IF NOT EXISTS bookmarks(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,ebook_id INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP,UNIQUE(user_id,ebook_id));
        """)
init()
st.set_page_config(page_title="E-Library",page_icon="📖",layout="wide")
st.title("📖 E-Library Management System")
st.caption("Digital book catalogue, reader accounts, search and bookmarks | SQLite")
t=st.tabs(["Explore e-books","Add e-book","Readers","My Bookmarks"])
with t[0]:
    with db() as c: rows=c.execute("SELECT * FROM ebooks ORDER BY title").fetchall()
    q=st.text_input("Search by title, author or category")
    cat=st.selectbox("Category",["All"]+sorted(set(r["category"] or "Uncategorised" for r in rows)))
    for r in rows:
        if q.lower() not in (r["title"]+" "+str(r["author"])+" "+str(r["category"])).lower(): continue
        if cat!="All" and (r["category"] or "Uncategorised")!=cat: continue
        with st.container(border=True):
            st.subheader(r["title"])
            st.write(f"**Author:** {r['author'] or 'Not specified'}  |  **Category:** {r['category'] or 'General'}")
            st.write(r["description"] or "No description added.")
            st.caption(f"Access: {r['access_level']}")
            if r["resource_url"]:
                st.markdown(f"[Open digital resource]({r['resource_url']})")
            else:
                st.info("No reading link has been added. Contact the library administrator.")
with t[1]:
    st.info("Only add digital files or links that you own or are authorised to distribute. This starter stores links; it does not host copyrighted books.")
    with st.form("ebook"):
        title=st.text_input("E-book title"); author=st.text_input("Author"); category=st.text_input("Category")
        desc=st.text_area("Short description"); url=st.text_input("Reading URL (https://...)"); access=st.selectbox("Access level",["Open","Institution only","Restricted"])
        ok=st.form_submit_button("Add e-book")
    if ok:
        if not title.strip(): st.error("Title is required.")
        elif url and not url.startswith(("https://","http://")): st.error("Enter a valid http:// or https:// URL.")
        else:
            with db() as c: c.execute("INSERT INTO ebooks(title,author,category,description,resource_url,access_level) VALUES(?,?,?,?,?,?)",(title,author,category,desc,url,access))
            st.success("E-book added.")
with t[2]:
    st.subheader("Register reader")
    with st.form("reader"):
        name=st.text_input("Reader name"); email=st.text_input("Email"); role=st.selectbox("Role",["Reader","Student","Faculty","Librarian"])
        ok=st.form_submit_button("Register")
    if ok:
        try:
            if not name.strip() or "@" not in email: st.error("Enter a name and valid email.")
            else:
                with db() as c: c.execute("INSERT INTO users(name,email,role) VALUES(?,?,?)",(name,email,role))
                st.success("Reader registered.")
        except sqlite3.IntegrityError: st.error("This email is already registered.")
    with db() as c: rows=c.execute("SELECT id,name,email,role FROM users ORDER BY name").fetchall()
    st.dataframe([dict(r) for r in rows],use_container_width=True)
with t[3]:
    with db() as c:
        users=c.execute("SELECT id,name,email FROM users ORDER BY name").fetchall()
        ebooks=c.execute("SELECT id,title FROM ebooks ORDER BY title").fetchall()
    if not users: st.info("Register a reader first.")
    elif not ebooks: st.info("Add an e-book first.")
    else:
        u=st.selectbox("Reader",users,format_func=lambda r:f"{r['name']} ({r['email']})")
        e=st.selectbox("E-book",ebooks,format_func=lambda r:r["title"])
        if st.button("Bookmark this e-book"):
            try:
                with db() as c: c.execute("INSERT INTO bookmarks(user_id,ebook_id) VALUES(?,?)",(u["id"],e["id"]))
                st.success("Bookmark saved.")
            except sqlite3.IntegrityError: st.warning("This reader has already bookmarked that e-book.")
        with db() as c: rows=c.execute("SELECT b.id,e.title,b.created_at FROM bookmarks b JOIN ebooks e ON e.id=b.ebook_id WHERE b.user_id=? ORDER BY b.created_at DESC",(u["id"],)).fetchall()
        st.markdown("#### Saved reading list")
        st.dataframe([dict(r) for r in rows],use_container_width=True)
st.caption("Academic prototype. Reader registration is a simple demo, not secure authentication. Do not use for confidential accounts.")
