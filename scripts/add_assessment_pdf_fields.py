#!/usr/bin/env python3
"""Add missing assessment PDF upload timestamp fields to existing patients."""

import json
import os
import sys
from pathlib import Path

# Add parent directory to path so we can import config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config

def add_assessment_fields_to_patients():
    """Add a0PdfUploadedAt, a1PdfUploadedAt, a2PdfUploadedAt to all patients."""

    data_root = Path(Config.DATA_ROOT)

    for hospital in Config.HOSPITALS:
        hospital_path = data_root / hospital / 'patients'

        if not hospital_path.exists():
            print(f"Skipping {hospital} — folder not found")
            continue

        for patient_folder in hospital_path.iterdir():
            if not patient_folder.is_dir():
                continue

            patient_id = patient_folder.name
            patient_file = patient_folder / f'{patient_id}.json'

            if not patient_file.exists():
                continue

            try:
                with open(patient_file, 'r', encoding='utf-8') as f:
                    patient = json.load(f)

                # Add missing fields if not present
                added = False
                if 'a0PdfUploadedAt' not in patient:
                    patient['a0PdfUploadedAt'] = None
                    added = True
                if 'a1PdfUploadedAt' not in patient:
                    patient['a1PdfUploadedAt'] = None
                    added = True
                if 'a2PdfUploadedAt' not in patient:
                    patient['a2PdfUploadedAt'] = None
                    added = True

                if added:
                    with open(patient_file, 'w', encoding='utf-8') as f:
                        json.dump(patient, f, indent=2)
                    print(f"[OK] Updated {hospital}/{patient_id}")
                else:
                    print(f"[--] {hospital}/{patient_id} already has all fields")

            except Exception as e:
                print(f"[ERROR] {hospital}/{patient_id}: {str(e)}")

if __name__ == '__main__':
    print("Adding assessment PDF fields to existing patients...\n")
    add_assessment_fields_to_patients()
    print("\nDone!")
