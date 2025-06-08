import json
import sqlite3
import sys

ALIASES = {
    ".tables": "SELECT type, name FROM sqlite_master WHERE type='table'",
    ".schema": "SELECT sql FROM sqlite_master",
    ".tablecount": "SELECT COUNT(name) FROM sqlite_master WHERE type='table'",
}

if __name__ == "__main__":
    if sys.argv[1] == "query":
        file = sys.argv[2]
        query = sys.argv[3].strip()
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
                j = j.replace("\\n", "%n").replace('\\"', "'").replace("\\t", "    ")
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
    elif sys.argv[1] == "new":
        file = sys.argv[2]
        con = sqlite3.connect(file)
        con.commit()
        con.close()
