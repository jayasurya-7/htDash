"""
Per-request session proxy.

Reads/writes Flask's per-browser cookie session so every logged-in user
sees only their own data. Drop-in replacement for the old global singleton.
"""
from flask import session as flask_session


class _SessionProxy:

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        if name == "device_name":
            return flask_session.get("device_name", "Pluto")
        if name == "place_info":
            return flask_session.get("place_info", {})
        return flask_session.get(name)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            super().__setattr__(name, value)
            return
        flask_session[name] = value
        flask_session.modified = True

    def set_session(self, login_place, privilege, device_name="Pluto"):
        flask_session["login_place"] = login_place
        flask_session["privilege"]   = privilege
        flask_session["device_name"] = device_name
        flask_session["place_info"]  = {}
        flask_session.modified = True

    def set_place_info(self, mapping):
        """Fully replace place_info dict — use instead of place_info[k]=v
        so Flask detects the change and saves it to the cookie."""
        flask_session["place_info"] = mapping
        flask_session.modified = True

    def is_admin(self):
        """True only for the global lab admin (place == 'admin') who is NOT the supervisor.
        Site admins (RP-HS-ADMIN etc.) have privilege==admin but a real place,
        so they should see ONLY their own site — not all centres."""
        return (flask_session.get("login_place") == "admin"
                and flask_session.get("privilege") != "supervisor")

    def is_site_admin(self):
        """True for site-level admins who can do admin actions but only for their site."""
        return (flask_session.get("privilege") or "").lower() == "admin"

    def is_supervisor(self):
        """True for the global supervisor — view-only across all centres."""
        return (flask_session.get("privilege") or "") == "supervisor"

    def is_therapist(self):
        """True for therapists — file clinical events, no device management."""
        return (flask_session.get("privilege") or "") == "therapist"

    def is_engineer(self):
        """True for engineers — file device events, no clinical events."""
        return (flask_session.get("privilege") or "") == "engineer"


current_session = _SessionProxy()