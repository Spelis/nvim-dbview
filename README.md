
# nvim-dbview

**A lightweight database viewer and executor for Neovim.**  
Query and inspect database files directly inside a buffer using Lua and a Python bridge.


## 🔧 Features

- View and Execute sql queries
- Execute queries with `<C-x>` in normal, insert, or visual mode
- Quick aliases like `.tables`, `.schema`, and other handy aliases
- Clean buffer presentation
- Pretty formatted SELECT results
- New database creation right from Neovim
- Potentially dangerous commands only get ran once


## 📦 Requirements

- Neovim (the newer the better)
- Python 3.x
- `sqlite3` module (bundled with Python)
- `sqlalchemy` module
- Works on Unix-like systems (should work on windows too)


## 🚀 Installation

### Lazy.nvim:
```
{
    "Spelis/nvim-dbview",
    opts = {
        python_path = "python",
        exec_key = "<C-x>",
    },
    -- Lazy load if you want. no guarantee it will work.
}
```


## 📚 Usage

### Open an existing database
```
:DBOpen path/to/database.db
```

### Create a new database (and open)
```
:DBNew path/to/new.db
```

### Query a database and copy result to clipboard
```
:DBQuery path/to/database.db
```
(This opens a text input where you enter your query)

### Auto-open `.db` files
`.db` files are automatically opened using the dbviewer.

## 🧠 Keybinds

Currently only one keybind: `<C-x>`, will execute the SQL in the dbviewer buffer.

(will also make the keybind configurable)

## 💬 Query Format
- Ignored lines start with a `#` and are hidden.
- Ignored queries start with a `@` and are also hidden.
- Non-SELECT queries run only once to not cause damage.

## 🛠 Example Usage
1. Run `:DBOpen database.db`
2. Type SQL in the buffer:
    ```sql
    SELECT * FROM users
    ```
3. Hit `<C-x>` to see the results below:
    ```sql
    SELECT * FROM users
    # Alice   23
    # Bob     30
    ```

## 📜 License

[MIT](LICENSE). Go nuts.

## ❓ Why?

I was tired of switching to a DB browser or making debug functions to do the queries. And I couldn't find any Neovim plugins that do as I like (Others were too complicated, too basic etc.)
