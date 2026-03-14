"""
Available trucks and drivers for logistics demo.
"""

AVAILABLE_TRUCKS = [
    {
        "truck_id": "TRK-001",
        "type": "small_van",
        "capacity_kg": 500,
        "location": "Depot North",
        "fuel_level": 90,
        "status": "available",
    },
    {
        "truck_id": "TRK-002",
        "type": "large_truck",
        "capacity_kg": 2000,
        "location": "Depot South",
        "fuel_level": 75,
        "status": "available",
    },
    {
        "truck_id": "TRK-003",
        "type": "medium_van",
        "capacity_kg": 800,
        "location": "Depot East",
        "fuel_level": 85,
        "status": "available",
    },
]

AVAILABLE_DRIVERS = [
    {
        "driver_id": "DRV-Ali",
        "name": "Ali Hassan",
        "license": "heavy_vehicle",
        "location": "Depot North",
        "shift": "06:00-18:00",
        "status": "available",
    },
    {
        "driver_id": "DRV-Sara",
        "name": "Sara Ahmed",
        "license": "all_vehicles",
        "location": "Depot South",
        "shift": "08:00-20:00",
        "status": "available",
    },
    {
        "driver_id": "DRV-Omar",
        "name": "Omar Khalid",
        "license": "standard",
        "location": "Depot East",
        "shift": "07:00-19:00",
        "status": "available",
    },
]
