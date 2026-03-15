"""Compliance checker for verifier agent."""

APPROVED_VENDORS = ["Fresh & Local", "Quick Bites", "Corporate Catering"]


def check_vendor_compliance(vendor_name: str) -> dict:
    approved = vendor_name.strip() in APPROVED_VENDORS
    return {
        "vendor": vendor_name,
        "approved": approved,
        "approved_list": APPROVED_VENDORS,
    }
