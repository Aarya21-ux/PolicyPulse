import os
import ibm_db_dbi

_conn = None

def conn():
    global _conn
    if _conn is None:
        dsn = (
            f"DATABASE={os.getenv('DB2_NAME', 'testdb')};"
            f"HOSTNAME={os.getenv('DB2_HOST', 'localhost')};"
            f"PORT={os.getenv('DB2_PORT', '50000')};PROTOCOL=TCPIP;"
            f"UID={os.getenv('DB2_USER', 'db2inst1')};PWD={os.getenv('DB2_PASS', 'password123')};"
        )
        _conn = ibm_db_dbi.connect(dsn, "", "")
    return _conn

def q(sql, params=()):
    cur = conn().cursor()
    cur.execute(sql, params)
    rows = cur.fetchall() if cur.description else []
    conn().commit()
    return rows
    

def init_schema(path="schema.sql"):
    for stmt in open(path).read().split(";"):
        if stmt.strip():
            try:
                q(stmt)
            except Exception as e:
                print("skip:", str(e)[:80])