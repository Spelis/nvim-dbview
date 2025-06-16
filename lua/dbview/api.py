import json
import sqlite3
import sys

from sqlalchemy import create_engine, text

ALIASES = {
    "sqlite": {
        ".tables": "SELECT type, name FROM sqlite_master WHERE type='table'",
        ".schema": "SELECT sql FROM sqlite_master WHERE type='table'",
        ".tablecount": "SELECT COUNT(name) FROM sqlite_master WHERE type='table'",
    },
    "postgresql": {
        ".tables": "SELECT table_name FROM information_schema.tables WHERE table_schema='public'",
        ".schema": """
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
        """,
        ".tablecount": "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'",
    },
    "mysql": {
        ".tables": "SHOW TABLES",
        ".schema": "SELECT table_name, column_name, column_type FROM information_schema.columns WHERE table_schema = DATABASE()",
        ".tablecount": "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE()",
    },
}

if __name__ == "__main__":
    if sys.argv[1] == "query":
        file = sys.argv[2]
        query = " ".join(sys.argv[3:]).strip()
        engine = create_engine(file if "://" in file else f"sqlite:///{file}")
        dialect = engine.url.get_backend_name()  # gives 'sqlite', 'postgresql', etc.
        query = ALIASES.get(dialect, {}).get(query.lower(), query)
        try:
            with engine.connect() as con:
                res = con.execute(text(query))
                rows = res.fetchall()
                all_ = tuple([tuple(str(j) for j in row) for row in rows])
                one = all_[0:1]
                d = {
                    "one": one,
                    "all": all_,
                    "success": len(all_) > 0,
                    "query": query,
                }
                j = json.dumps(d, indent=4)
                j = j.replace("\\n", "%n").replace('\\"', "'").replace("\\t", "    ")
                print(j)
                # con.commit() # Should be auto commit...
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
