import re
import json
from typing import List, Dict

# Initialize the JSON structure
order_data = {
    "line_items": [],
    "delivery_date": None,
    "location": None
}

# Function to parse transcription and update JSON
def update_order_json(transcription: str):
    global order_data

    # Match phrases like "3 kg of tomatoes" or "5 bunches of parsley"
    item_pattern = r"(\d+)\s*(\w+)?\s*of\s+([\w\s]+)"
    matches = re.findall(item_pattern, transcription.lower())

    # Handle replacement commands like "Change parsley to 10 bunches of mint"
    if "change" in transcription.lower():
        change_pattern = r"change\s+([\w\s]+)\s+to\s+(\d+)\s*(\w+)?\s*of\s+([\w\s]+)"
        change_match = re.search(change_pattern, transcription.lower())
        if change_match:
            old_item = change_match.group(1).strip()
            quantity = change_match.group(2)
            uom = change_match.group(3) or ""
            new_item = change_match.group(4).strip()

            # Remove the old item and add the new one
            order_data["line_items"] = [
                item for item in order_data["line_items"] if item["item_name"] != old_item
            ]
            order_data["line_items"].append({
                "item_name": new_item,
                "quantity": quantity,
                "uom": uom
            })
            return

    # Add new items to the order
    for match in matches:
        quantity, uom, item_name = match
        item_name = item_name.strip()
        uom = uom or ""  # Handle cases without UoM

        # Check if the item already exists
        existing_item = next((item for item in order_data["line_items"] if item["item_name"] == item_name), None)
        if existing_item:
            existing_item["quantity"] = quantity
            existing_item["uom"] = uom
        else:
            order_data["line_items"].append({
                "item_name": item_name,
                "quantity": quantity,
                "uom": uom
            })

# Simulate transcription input
transcriptions = [
    "Hi, can you hear me?",
    "So I'm calling from Gonzalez Restaurant and I'd like to order.",
    "3 kg of tomato",
    "5 bunches of parsley",
    "And 8 kg of beef.",
    "Change parsley to 10 bunches of mint."
]

# Process each transcription
for transcription in transcriptions:
    try:
        update_order_json(transcription)
        print("Updated JSON:", json.dumps(order_data, indent=4))
    except Exception as e:
        print("Error decoding JSON:", e)
