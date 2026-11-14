import sqlite3, unittest, app
class DiffTests(unittest.TestCase):
 def test_added_table(self):
  a=sqlite3.connect(":memory:");b=sqlite3.connect(":memory:")
  b.execute("CREATE TABLE notes(id INTEGER PRIMARY KEY, body TEXT)")
  r=app.compare(a,b)
  self.assertIn("notes",r["added"])
  self.assertTrue(any("CREATE TABLE" in s for s in r["suggested_sql"]))
if __name__=="__main__":unittest.main()
