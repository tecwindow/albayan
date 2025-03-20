import sqlite3
import json
import os

# Database file path
db_path = "quran_info.DB"

def update_revelation_type():
    """Updates revelationType from English to Arabic in surah_info table."""
    
    if not os.path.isfile(db_path):
        print(f"❌ Database not found: {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Fetch all surah info records
        cursor.execute("SELECT sura_number, info FROM surah_info")
        records = cursor.fetchall()

        for record in records:
            sura_number = record["sura_number"]
            info_json = record["info"]

            if not info_json:
                continue  # Skip empty records

            try:
                info_dict = json.loads(info_json)
                revelation_type = info_dict.get("revelationType")

                # Map English names to Arabic
                arabic_mapping = {"Meccan": "مكية", "Medinan": "مدنية"}
                if revelation_type in arabic_mapping:
                    info_dict["revelationType"] = arabic_mapping[revelation_type]

                    # Update the database with the modified JSON
                    new_info_json = json.dumps(info_dict, ensure_ascii=False)
                    cursor.execute(
                        "UPDATE surah_info SET info = ? WHERE sura_number = ?",
                        (new_info_json, sura_number),
                    )

            except json.JSONDecodeError:
                print(f"⚠️ Invalid JSON for Surah {sura_number}, skipping.")

        conn.commit()
        print("✅ RevelationType successfully updated to Arabic.")

    except sqlite3.Error as e:
        print(f"❌ SQLite Error: {e}")

    finally:
        conn.close()

# Run the script
update_revelation_type()
