import json
import sqlite3
import sys

from sqlalchemy import create_engine, text

ALIASES = {
    ".tables": "SELECT type, name FROM sqlite_master WHERE type='table'",
    ".schema": "SELECT sql FROM sqlite_master",
    ".tablecount": "SELECT COUNT(name) FROM sqlite_master WHERE type='table'",
}

if __name__ == "__main__":
    if sys.argv[1] == "query":
        file = sys.argv[2]
        query = " ".join(sys.argv[3:]).strip()
        query = ALIASES.get(query.lower(), query)
        engine = create_engine(file if "://" in file else f"sqlite:///{file}")
        try:
            with engine.connect() as con:
                res = con.execute(text(query))
                all_ = [[str(j) for j in i] for i in res.fetchall()]
                one = all_[0] if all_ else None
                d = {
                    "one": one,
                    "all": all_,
                    "success": res.rowcount > 0,
                    "query": query,
                }
                j = json.dumps(d, indent=4)
                j = j.replace("\\n", "%n").replace('\\"', "'").replace("\\t", "    ")
                print(j)
                con.commit()
                con.close()
        except Exception as e:
            d = {
                "one": None,
                "all": (),
                "success": False,
                "error": str(e),
                "query": str(query),
            }
            j = json.dumps(d, indent=4)
            j = j.replace("\\n", "\n")
            print(j)
    elif sys.argv[1] == "new":
        file = sys.argv[2]
        if "://" in file and not "sqlite" in file:
            file = f"sqlite:///{file.split('://')[1]}"
        con = sqlite3.connect(file)
        con.commit()
        con.close()
