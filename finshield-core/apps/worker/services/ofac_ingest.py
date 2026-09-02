import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "api"))

import csv
import io
import requests
from db import SessionLocal
from models.sanctions_entry import SanctionsEntry

# OFAC's official SDN list, published as a plain CSV — free, public, updated daily.
SDN_CSV_URL = "https://www.treasury.gov/ofac/downloads/sdn.csv"

# The SDN CSV has no header row; these are the documented column positions we care about.
COL_NAME = 1
COL_TYPE = 2
COL_PROGRAM = 3


def fetch_sdn_csv() -> str:
    response = requests.get(SDN_CSV_URL, timeout=30)
    response.raise_for_status()
    return response.text


def parse_sdn_csv(csv_text: str):
    reader = csv.reader(io.StringIO(csv_text))
    entries = []
    for row in reader:
        if len(row) <= COL_PROGRAM:
            continue  # skip malformed/short rows
        source_id = row[0].strip().strip('"')
        name = row[COL_NAME].strip().strip('"')
        entry_type = row[COL_TYPE].strip().strip('"')
        program = row[COL_PROGRAM].strip().strip('"')
        if name and name != "-0-":  # OFAC uses "-0-" as a placeholder for blank fields
            entries.append({
                "source_id": source_id,
                "name": name,
                "entry_type": entry_type,
                "program": program,
            })
    return entries


def ingest_sanctions_list():
    print("Fetching OFAC SDN list...")
    csv_text = fetch_sdn_csv()

    print("Parsing entries...")
    entries = parse_sdn_csv(csv_text)
    print(f"Parsed {len(entries)} entries.")

    db = SessionLocal()
    try:
        print("Clearing old sanctions_entries...")
        db.query(SanctionsEntry).delete()
        db.commit()

        print("Inserting new entries...")
        batch = []
        for e in entries:
            batch.append(SanctionsEntry(
                source_id=e["source_id"],
                name=e["name"],
                entry_type=e["entry_type"],
                program=e["program"],
            ))
            if len(batch) >= 500:
                db.bulk_save_objects(batch)
                db.commit()
                batch = []
        if batch:
            db.bulk_save_objects(batch)
            db.commit()

        print(f"Done. {len(entries)} entries loaded.")
    finally:
        db.close()


if __name__ == "__main__":
    ingest_sanctions_list()