<div align="center"><img src="assets/banner.svg" width="100%"><h1>SchemaDiff</h1><p>Compare SQLite database structures. Read-only by design.</p></div>

## What it compares
- Tables, views, indexes and triggers.
- Table columns, declared types, defaults, nullability and primary keys.
- Foreign-key definitions.
- Added, removed and changed schema objects.

## Run
```bash
python app.py before.db after.db
python app.py before.db after.db --json
python app.py before.db after.db --sql
```
The generated SQL is a review aid, not an automatic migration. Removed or complex changed objects require manual work. Both databases are opened in SQLite read-only mode.

Python 3.9+, standard library only.

## Tests
```bash
python -m unittest discover -s tests -v
```
MIT License.