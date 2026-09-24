import datetime
import subprocess
from google.cloud import firestore
from google.oauth2 import credentials

# Hardcode project ID to ensure compatibility with deployed Agent Engine
PROJECT_ID = "qwiklabs-gcp-02-26648d09f310"

def seed_database():
    print(f"Connecting to Firestore in project: {PROJECT_ID}")
    db = firestore.Client(project=PROJECT_ID)


    # Seed Support Tickets
    tickets_ref = db.collection("tickets")
    sample_tickets = [
        {
            "ticket_id": "TCK-1001",
            "employee_name": "Alice Smith",
            "issue_title": "Laptop screen flickering intermittently",
            "category": "Hardware",
            "priority": "High",
            "status": "In Progress",
            "description": "External display works fine, but primary MacBook display flickers on battery power.",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        {
            "ticket_id": "TCK-1002",
            "employee_name": "Alice Smith",
            "issue_title": "VPN connection drops after 10 minutes",
            "category": "Network",
            "priority": "Medium",
            "status": "Open",
            "description": "GlobalProtect VPN keeps disconnecting every 10 minutes on home Wi-Fi.",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        {
            "ticket_id": "TCK-1003",
            "employee_name": "Bob Jones",
            "issue_title": "Request for Figma Pro license renewal",
            "category": "Software",
            "priority": "Low",
            "status": "Resolved",
            "description": "Need renewal for Figma Pro enterprise seat.",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    ]

    for ticket in sample_tickets:
        tickets_ref.document(ticket["ticket_id"]).set(ticket)
        print(f"Seeded ticket: {ticket['ticket_id']}")

    # Seed Hardware Inventory
    hardware_ref = db.collection("hardware")
    sample_hardware = [
        {
            "asset_id": "HW-8801",
            "device_name": "MacBook Pro 16\" M3 Max",
            "assigned_to": "Alice Smith",
            "status": "Assigned",
            "serial_number": "SN-C02XL9981",
            "purchase_year": 2024,
        },
        {
            "asset_id": "HW-8802",
            "device_name": "Dell XPS 15 9530",
            "assigned_to": "Bob Jones",
            "status": "Assigned",
            "serial_number": "SN-DELL44012",
            "purchase_year": 2023,
        }
    ]

    for hw in sample_hardware:
        hardware_ref.document(hw["asset_id"]).set(hw)
        print(f"Seeded hardware: {hw['asset_id']}")

    print("Firestore seeding complete!")

if __name__ == "__main__":
    seed_database()
