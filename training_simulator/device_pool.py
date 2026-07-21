"""
Training-only device inventory pool.

Seeds TRNDEV-* prefixed devices into Ranipet's real inventory at cohort creation,
and removes them at teardown, keeping HOCMCV002-005's real devices untouched.
"""

from training_simulator.bootstrap import Config
from utils.data_access import (
    read_device_inventory,
    write_device_inventory,
    read_device_assignments,
    write_device_assignments,
    read_sims,
    write_sims,
)

HOSPITAL = 'ranipet'
PREFIX = 'TRNDEV'

# Fixed training device pool constants
PLUTO_1, PLUTO_2, PLUTO_3, PLUTO_4, PLUTO_5, PLUTO_6, PLUTO_7, PLUTO_8 = ('TRNDEV-PLUTO-1', 'TRNDEV-PLUTO-2', 'TRNDEV-PLUTO-3', 'TRNDEV-PLUTO-4', 'TRNDEV-PLUTO-5', 'TRNDEV-PLUTO-6', 'TRNDEV-PLUTO-7', 'TRNDEV-PLUTO-8')
MARS_1, MARS_2, MARS_3, MARS_4, MARS_5, MARS_6, MARS_7, MARS_8 = ('TRNDEV-MARS-1', 'TRNDEV-MARS-2', 'TRNDEV-MARS-3', 'TRNDEV-MARS-4', 'TRNDEV-MARS-5', 'TRNDEV-MARS-6', 'TRNDEV-MARS-7', 'TRNDEV-MARS-8')
AGW_1, AGW_2, AGW_3, AGW_4, AGW_5, AGW_6, AGW_7, AGW_8, AGW_9, AGW_10 = ('TRNDEV-AGW-1', 'TRNDEV-AGW-2', 'TRNDEV-AGW-3', 'TRNDEV-AGW-4', 'TRNDEV-AGW-5', 'TRNDEV-AGW-6', 'TRNDEV-AGW-7', 'TRNDEV-AGW-8', 'TRNDEV-AGW-9', 'TRNDEV-AGW-10')
MODEM_1, MODEM_2, MODEM_3, MODEM_4, MODEM_5, MODEM_6, MODEM_7, MODEM_8 = ('TRNDEV-MODEM-1', 'TRNDEV-MODEM-2', 'TRNDEV-MODEM-3', 'TRNDEV-MODEM-4', 'TRNDEV-MODEM-5', 'TRNDEV-MODEM-6', 'TRNDEV-MODEM-7', 'TRNDEV-MODEM-8')
LAPTOP_1, LAPTOP_2, LAPTOP_3, LAPTOP_4, LAPTOP_5, LAPTOP_6, LAPTOP_7, LAPTOP_8 = ('TRNDEV-LAPTOP-1', 'TRNDEV-LAPTOP-2', 'TRNDEV-LAPTOP-3', 'TRNDEV-LAPTOP-4', 'TRNDEV-LAPTOP-5', 'TRNDEV-LAPTOP-6', 'TRNDEV-LAPTOP-7', 'TRNDEV-LAPTOP-8')
SIM_1, SIM_2, SIM_3, SIM_4, SIM_5, SIM_6, SIM_7, SIM_8 = 'TRNDEV-SIM-1', 'TRNDEV-SIM-2', 'TRNDEV-SIM-3', 'TRNDEV-SIM-4', 'TRNDEV-SIM-5', 'TRNDEV-SIM-6', 'TRNDEV-SIM-7', 'TRNDEV-SIM-8'

POOL_SPEC = {
    'pluto': [PLUTO_1, PLUTO_2, PLUTO_3, PLUTO_4, PLUTO_5, PLUTO_6, PLUTO_7, PLUTO_8],
    'mars': [MARS_1, MARS_2, MARS_3, MARS_4, MARS_5, MARS_6, MARS_7, MARS_8],
    'agwatch': [AGW_1, AGW_2, AGW_3, AGW_4, AGW_5, AGW_6, AGW_7, AGW_8, AGW_9, AGW_10],
    'modems': [MODEM_1, MODEM_2, MODEM_3, MODEM_4, MODEM_5, MODEM_6, MODEM_7, MODEM_8],
    'laptops': [LAPTOP_1, LAPTOP_2, LAPTOP_3, LAPTOP_4, LAPTOP_5, LAPTOP_6, LAPTOP_7, LAPTOP_8],
}

SIM_SPEC = [SIM_1, SIM_2, SIM_3, SIM_4, SIM_5, SIM_6, SIM_7, SIM_8]


def seed_training_devices(num_patients: int = 4) -> None:
    """
    Idempotent append-only: seed training device constants into Ranipet's
    real inventory files if not already present. Never modifies existing devices.

    Args:
        num_patients: Total number of patients. Ensures enough devices are seeded.
                     Device pool supports up to 8 patients. Default 4 (legacy: 2 exp + 2 ctrl).
    """
    if num_patients > 8:
        print(f"  WARNING: Device pool supports max 8 patients; requested {num_patients}")
        return
    # Seed devices for each type
    for dtype, device_ids in POOL_SPEC.items():
        devices = read_device_inventory(HOSPITAL, dtype)
        existing_ids = {d.get('id') for d in devices if d.get('id')}

        added = 0
        for device_id in device_ids:
            if device_id not in existing_ids:
                devices.append({
                    'id': device_id,
                    'serial': device_id,  # dummy serial
                    'clinic_only': False,
                    'inclusion_date': None,
                    'removal_date': None,
                    'faulty': False,
                    'lost_date': None,
                    'has_issue': False,  # added field for agwatch-compat
                })
                added += 1

        if added:
            write_device_inventory(HOSPITAL, dtype, {'devices': devices})
            print(f"  Seeded {added} new {dtype} device(s)")

    # Seed SIMs
    sims = read_sims(HOSPITAL)
    existing_sim_ids = {s.get('id') for s in sims if s.get('id')}

    added = 0
    for sim_id in SIM_SPEC:
        if sim_id not in existing_sim_ids:
            sims.append({
                'id': sim_id,
                'phoneNumber': '0000000001',  # dummy phone
                'network': 'Training',
                'dataPlan': '1GB',
                'status': 'active',
            })
            added += 1

    if added:
        write_sims(HOSPITAL, sims)
        print(f"  Seeded {added} new SIM(s)")


def teardown_training_devices() -> None:
    """
    Remove all TRNDEV-* prefixed rows from inventory and assignments.
    Leaves all non-prefixed devices/assignments untouched.
    """
    # Remove from device inventory
    for dtype in POOL_SPEC.keys():
        devices = read_device_inventory(HOSPITAL, dtype)
        filtered = [d for d in devices if not str(d.get('id', '')).startswith(PREFIX)]
        removed = len(devices) - len(filtered)
        if removed:
            write_device_inventory(HOSPITAL, dtype, {'devices': filtered})
            print(f"  Removed {removed} training {dtype} device(s)")

    # Remove from SIMs
    sims = read_sims(HOSPITAL)
    filtered = [s for s in sims if not str(s.get('id', '')).startswith(PREFIX)]
    removed = len(sims) - len(filtered)
    if removed:
        write_sims(HOSPITAL, filtered)
        print(f"  Removed {removed} training SIM(s)")

    # Remove from device assignments (all types)
    for dtype in list(POOL_SPEC.keys()) + ['sims']:
        assignments = read_device_assignments(HOSPITAL, dtype)
        filtered = [
            a for a in assignments
            if not str(a.get('device_id', '')).startswith(PREFIX)
            and not str(a.get('homer_id', '')).startswith('TRN')
        ]
        removed = len(assignments) - len(filtered)
        if removed:
            write_device_assignments(HOSPITAL, dtype, filtered)
            print(f"  Removed {removed} training {dtype} assignment(s)")
