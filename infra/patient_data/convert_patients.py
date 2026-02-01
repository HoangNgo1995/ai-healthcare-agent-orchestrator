import json
import os
import uuid

# Process patient_1, patient_2, patient_3
for patient_num in [1, 2, 3]:
    patient_dir = f"patient_{patient_num}"
    notes_dir = os.path.join(patient_dir, "clinical_notes")

    if not os.path.exists(notes_dir):
        continue

    # Get all JSON files
    files = sorted([f for f in os.listdir(notes_dir) if f.endswith('.json')])

    for filename in files:
        filepath = os.path.join(notes_dir, filename)

        # Read the file
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Generate new UUID
        new_id = str(uuid.uuid4())

        # Restructure data to match patient_4 format
        new_data = {
            "date": data.get("date", ""),
            "note_type": data.get("type", ""),
            "text": data.get("text", ""),
            "id": new_id
        }

        # Create new filename with UUID
        new_filepath = os.path.join(notes_dir, f"{new_id}.json")

        # Write new file
        with open(new_filepath, 'w') as f:
            json.dump(new_data, f, indent=2)

        # Remove old file
        os.remove(filepath)

        print(f"Patient {patient_num}: {filename} -> {new_id}.json")

print("\nConversion complete!")
