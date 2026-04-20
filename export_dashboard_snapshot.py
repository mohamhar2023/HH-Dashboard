#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime, timezone

SHEET_ID = "1RsiHWDbSHfO58He4Y7x-JJWEqOPHMVDnS_NitS9yLwY"
OUT = "public-data.js"


def get_range(range_name):
    res = subprocess.run(
        ["gog", "sheets", "get", SHEET_ID, range_name, "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(res.stdout).get("values", [])


def parse_money(value):
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace("$", "").replace(",", "")
    if not text:
        return 0.0
    try:
        return float(text)
    except Exception:
        return 0.0


projects_rows = get_range("Dashboard!A2:F1000")
projects = []
for row in projects_rows:
    if not row or len(row) < 2 or not row[0]:
        continue
    projects.append({
        "projectId": row[0],
        "projectName": row[1] if len(row) > 1 else "",
        "income": parse_money(row[2] if len(row) > 2 else 0),
        "expenses": parse_money(row[3] if len(row) > 3 else 0),
        "materials": parse_money(row[4] if len(row) > 4 else 0),
        "profit": parse_money(row[5] if len(row) > 5 else 0),
        "status": "Active",
    })


def build_recent(range_name, kind, field_map):
    rows = get_range(range_name)
    if not rows:
        return []
    header, *data_rows = rows
    items = []
    for row in data_rows:
        if not row or not any(str(cell).strip() for cell in row):
            continue
        item = {"kind": kind}
        for out_key, idx in field_map.items():
            item[out_key] = row[idx] if len(row) > idx else ""
        amount = parse_money(item.get("amount", 0))
        item["amount"] = amount
        items.append(item)
    items.reverse()
    return items[:10]


recent_income = build_recent(
    "Income!A2:I1000",
    "income",
    {
        "date": 0,
        "projectId": 1,
        "projectName": 2,
        "party": 3,
        "reference": 4,
        "description": 5,
        "amount": 6,
        "status": 7,
        "notes": 8,
    },
)

recent_expenses = build_recent(
    "Expenses!A2:J1000",
    "expense",
    {
        "date": 0,
        "projectId": 1,
        "projectName": 2,
        "party": 3,
        "category": 4,
        "reference": 5,
        "description": 6,
        "amount": 7,
        "paidBy": 8,
        "notes": 9,
    },
)

recent_materials = build_recent(
    "Materials!A2:J1000",
    "material",
    {
        "date": 0,
        "projectId": 1,
        "projectName": 2,
        "party": 3,
        "description": 4,
        "quantity": 5,
        "unitCost": 6,
        "amount": 7,
        "priceCheck": 8,
        "notes": 9,
    },
)

payload = {
    "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
    "source": "sanitized-export",
    "projects": projects,
    "recent": {
        "income": recent_income,
        "expenses": recent_expenses,
        "materials": recent_materials,
    },
}
with open(OUT, "w", encoding="utf-8") as f:
    f.write("window.HH_DASHBOARD_DATA = ")
    json.dump(payload, f, indent=2)
    f.write(";\n")

print(f"Wrote {OUT} with {len(projects)} projects")
