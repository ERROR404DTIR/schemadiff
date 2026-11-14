#!/usr/bin/env python3
"""Compare two SQLite database schemas without modifying either database."""
import argparse,json,sqlite3
from pathlib import Path
def open_readonly(path):
 return sqlite3.connect(Path(path).resolve().as_uri()+"?mode=ro",uri=True)
def schema(conn):
 result={}
 objects=conn.execute("SELECT type,name,sql FROM sqlite_master WHERE type IN ('table','view','index','trigger') AND name NOT LIKE 'sqlite_%' ORDER BY type,name")
 for typ,name,sql in objects:
  item={"type":typ,"sql":sql or ""}
  if typ=="table":
   safe=name.replace('"','""')
   item["columns"]=[{"name":r[1],"type":r[2],"notnull":bool(r[3]),"default":r[4],"pk":bool(r[5])} for r in conn.execute(f'PRAGMA table_info("{safe}")')]
   item["foreign_keys"]=[list(r) for r in conn.execute(f'PRAGMA foreign_key_list("{safe}")')]
  result[name]=item
 return result
def compare(old,new):
 a,b=schema(old),schema(new);added=sorted(b.keys()-a.keys());removed=sorted(a.keys()-b.keys());changed=[]
 for name in sorted(a.keys()&b.keys()):
  if a[name]!=b[name]:changed.append({"name":name,"before":a[name],"after":b[name]})
 suggestions=[]
 for name in added:
  if b[name]["type"]=="table" and b[name]["sql"]:suggestions.append(b[name]["sql"]+";")
 for ch in changed:
  before={c["name"]:c for c in ch["before"].get("columns",[])};after={c["name"]:c for c in ch["after"].get("columns",[])}
  for col in sorted(after.keys()-before.keys()):
   c=after[col];typ=c["type"] or "TEXT"
   if c["notnull"] and c["default"] is None:suggestions.append(f'-- Manual migration required: {ch["name"]}.{col} is NOT NULL without a default')
   else:suggestions.append(f'ALTER TABLE "{ch["name"]}" ADD COLUMN "{col}" {typ}'+(f' DEFAULT {c["default"]}' if c["default"] is not None else "")+";")
 return {"added":added,"removed":removed,"changed":changed,"suggested_sql":suggestions}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("old");p.add_argument("new");p.add_argument("--json",action="store_true");p.add_argument("--sql",action="store_true");a=p.parse_args()
 try:
  with open_readonly(a.old) as x,open_readonly(a.new) as y:r=compare(x,y)
 except (OSError,sqlite3.Error) as e:p.error(str(e))
 if a.json:print(json.dumps(r,indent=2));return
 if a.sql:print("\n".join(r["suggested_sql"]) or "-- No safe SQL suggestions");return
 for k in ("added","removed"):print(k.upper()+": "+(", ".join(r[k]) or "none"))
 print("CHANGED: "+(", ".join(x["name"] for x in r["changed"]) or "none"))
 print("\nSuggested SQL (review before use):\n"+"\n".join(r["suggested_sql"]))
if __name__=="__main__":main()
