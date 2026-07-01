#!/usr/bin/env python
"""
Admin CLI tool to reset a user's password. Generates a temporary password or accepts one.

Usage:
    python scripts/reset_password.py <loginid>                    # Generate random temp password
    python scripts/reset_password.py <loginid> <new_password>    # Set specific password
"""

import sys
import os
import random
import string
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from utils.encryption import EncryptionUtils, CredentialsManager
from datetime import datetime


def generate_temp_password(length=8):
    """Generate a random alphanumeric temporary password."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def reset_password(loginid, new_password=None):
    """Reset a user's password and set first_login flag."""
    print(f"Resetting password for {loginid}...")

    # Load credentials
    credentials = CredentialsManager.get_or_create_credentials()

    if loginid not in credentials:
        print(f"✗ User {loginid} not found in credentials")
        return False

    # Generate or use provided password
    if new_password is None:
        new_password = generate_temp_password()
        is_temp = True
    else:
        is_temp = False

    # Validate password length
    if len(new_password) < 4:
        print("✗ Password must be at least 4 characters")
        return False

    # Hash and update
    password_hash = EncryptionUtils.hash_password(new_password)
    credentials[loginid]["password_hash"] = password_hash
    credentials[loginid]["first_login"] = True
    credentials[loginid]["password_changed"] = False
    credentials[loginid]["last_changed"] = datetime.now().isoformat()

    # Save
    success = CredentialsManager.save_credentials(credentials)

    if success:
        print(f"[OK] Password reset successfully")
        if is_temp:
            print(f"\n[TEMP_PASSWORD] {new_password}")
            print(f"   User MUST change this on first login")
        else:
            print(f"[OK] User can now log in with the new password")
        return True
    else:
        print(f"[ERROR] Failed to save credentials")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/reset_password.py <loginid> [new_password]")
        sys.exit(1)

    loginid = sys.argv[1]
    new_password = sys.argv[2] if len(sys.argv) > 2 else None

    success = reset_password(loginid, new_password)
    sys.exit(0 if success else 1)
