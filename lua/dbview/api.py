import json
import os
import sys

if __name__ == "__main__":
    if sys.argv[1] == "ginfo":
        DTYPE_LOOKUP = {
            b"SQLite format 3\x00": "sqlite",
            b"PGDMP": "postgres",
            b"\x00\x01\x00\x00": "microsoft",
            b"FORM": "berkeley",
            b"IB": "interbase",
            b"\x00\x05\x00\x00": "paradox",
        }
        file = sys.argv[2]
        with open(file, "rb") as f:
            header = f.read(100)

        dtype = "unknown"
        for magic, dbtype in DTYPE_LOOKUP.items():
            if header.startswith(magic):
                dtype = dbtype
                break

        d = {"filesize": os.path.getsize(file), "dbtype": dtype}
    if sys.argv[1] == "sqlite":
        import sqlite3

        ALIASES = {
            ".tables": "SELECT type, name FROM sqlite_master WHERE type='table'",
            ".schema": "SELECT sql FROM sqlite_master",
            ".tablecount": "SELECT COUNT(name) FROM sqlite_master WHERE type='table'",
        }
        if sys.argv[2] == "query":
            file = sys.argv[3]
            query = sys.argv[4].strip()
            query = ALIASES.get(query.lower(), query)
            try:
                with sqlite3.connect(file) as con:
                    cur = con.cursor()
                    res = cur.execute(query)
                    all_ = res.fetchall()
                    one = all_[0] if all_ else None
                    d = {
                        "one": one,
                        "all": all_,
                        "success": bool(cur.rowcount),
                        "query": query,
                    }
                    j = json.dumps(d, indent=4)
                    j = (
                        j.replace("\\n", "%n")
                        .replace('\\"', "'")
                        .replace("\\t", "    ")
                    )
                    print(j)
                    con.commit()
                    cur.close()
            except Exception as e:
                d = {
                    "one": None,
                    "all": (),
                    "success": False,
                    "error": str(e),
                    "query": query,
                }
                j = json.dumps(d, indent=4)
                j = j.replace("\\n", "\n")
                print(j)
        elif sys.argv[2] == "new":
            file = sys.argv[3]
            con = sqlite3.connect(file)
            con.commit()
            con.close()
    if sys.argv[1] == "postgres":
        import psycopg2

        if sys.argv[2] == "query":
            file = sys.argv[3]
            query = sys.argv[4].strip()
            try:
                conn = psycopg2.connect(dbname=sys.argv[3])
            except Exception as e:
                d = {
                    "one": None,
                    "all": (),
                    "success": False,
                    "error": str(e),
                    "query": query,
                }
                j = json.dumps(d, indent=4)
                j = j.replace("\\n", "\n")
