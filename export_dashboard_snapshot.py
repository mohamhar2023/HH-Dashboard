#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime, timezone

SHEET_ID = "1RsiHWDbSHfO58He4Y7x-JJWEqOPHMVDnS_NitS9yLwY"
RANGE = "Dashboard!A2:F1000"
OUT = "public-data.js"

res = subprocess.run(
    ["gog", "sheets", "get", SHEET_ID, RANGE, "--json"],
    check=True,
    capture_output=True,
    text=True,
)
rows = json.loads(res.stdout).get("values", [])
projects = []
for row in rows:
    if not row or len(row) < 2 or not row[0]:
        continue
    def num(i):
        try:
            return float(row[i]) if len(row) > i and row[i] != "" else 0
        except Exception:
            return 0
    projects.append({
        "projectId": row[0],
        "projectName": row[1] if len(row) > 1 else "",
        "income": num(2),
        "expenses": num(3),
        "materials": num(4),
        "profit": num(5),
        "status": "Active",
    })

payload = {
    "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
    "source": "sanitized-export",
    "projects": projects,
}
with open(OUT, "w", encoding="utf-8") as f:
    f.write("window.HH_DASHBOARD_DATA = ")
    json.dump(payload, f, indent=2)
    f.write(";\n")

print(f"Wrote {OUT} with {len(projects)} projects")
