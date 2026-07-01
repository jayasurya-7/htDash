#!/usr/bin/env python
"""
One-time initialization script to seed data/credentials.json with bcrypt-hashed passwords
from Config.LOGIN_CREDENTIALS. Run once per environment.

Usage:
    python scripts/init_credentials.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from utils.encryption import EncryptionUtils, CredentialsManager
from datetime import datetime


def init_credentials():
    """Migrate all 13 credentials from config to local/S3 with bcrypt hashing."""
    print("Initializing credentials...")

    if not Config.LOGIN_CREDENTIALS:
        print("ERROR: No credentials found in config.py")
        return False

    # Load existing credentials (if any)
    existing = CredentialsManager.get_or_create_credentials()

    # Process each credential from config
    new_count = 0
    existing_count = 0
    credentials = existing.copy()

    for loginid, config_data in Config.LOGIN_CREDENTIALS.items():
        if loginid in credentials:
            existing_count += 1
            print(f"  [OK] {loginid} — already migrated (skipping)")
            continue

        # Hash password from config
        password_hash = EncryptionUtils.hash_password(config_data["password"])

        credentials[loginid] = {
            "place": config_data["place"],
            "privilege": config_data.get("privilege", "therapist"),
            "password_hash": password_hash,
            "created_by": "system",
            "created_at": datetime.now().isoformat(),
            "first_login": False,
            "password_changed": True
        }

        new_count += 1
        print(f"  [OK] {loginid} — migrated with bcrypt hash")

    # Save to local or S3
    if new_count > 0:
        success = CredentialsManager.save_credentials(credentials)
        if success:
            location = "local (data/credentials.json)" if not Config.USE_S3 else "S3"
            print(f"\n[OK] Saved {new_count} new credentials to {location}")
            print(f"  {existing_count} credentials already existed")
            print(f"  Total: {len(credentials)} credentials in store")
            print("\n[OK] No plaintext passwords stored — only bcrypt hashes!")
            return True
        else:
            print(f"\n[ERROR] Failed to save credentials")
            return False
    else:
        print(f"\n[OK] All {existing_count} credentials already migrated")
        return True


if __name__ == "__main__":
    success = init_credentials()
    sys.exit(0 if success else 1)
