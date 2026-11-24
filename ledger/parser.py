"""
Simple rule-based + keyword parser for Kirana voice commands.
Handles Hindi + English code-mix common in Indian shops.
"""

import re
from typing import Optional
from . import db


# Common number words (Hindi + English)
NUMBER_MAP = {
    "zero": 0, "ek": 1, "do": 2, "teen": 3, "char": 4, "chaar": 4,
    "paanch": 5, "panch": 5, "chhe": 6, "che": 6, "saat": 7,
    "aath": 8, "nau": 9, "das": 10, "gyarah": 11, "barah": 12,
    "terah": 13, "chaudah": 14, "pandrah": 15, "solah": 16,
    "satrah": 17, "atharah": 18, "unnis": 19, "bees": 20,
    "tees": 30, "chalis": 40, "chaalis": 40, "pachaas": 50,
    "saath": 60, "sattar": 70, "assi": 80, "nabbe": 90,
    "sau": 100, "hazaar": 1000, "hazar": 1000,
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "hundred": 100, "thousand": 1000,
}


def extract_amount(text: str) -> Optional[float]:
    """
    Extract amount from spoken text.
    Supports: 340, 3 40, teen sau chaalis, three forty, ₹340 etc.
    """
    text = text.lower().replace(",", "").replace("₹", "").replace("rs", "").replace("rupees", "")

    # Direct number patterns
    match = re.search(r'(\d+(?:\.\d+)?)', text)
    if match:
        return float(match.group(1))

    # Word based (simple cases)
    words = text.split()
    total = 0
    current = 0

    for w in words:
        if w in NUMBER_MAP:
            val = NUMBER_MAP[w]
            if val == 100 or val == 1000:
                current = (current or 1) * val
                total += current
                current = 0
            else:
                current += val
        elif w in ["sau", "hundred"]:
            current = (current or 1) * 100
            total += current
            current = 0

    total += current
    return float(total) if total > 0 else None


def detect_intent(text: str) -> dict:
    """
    Detect what the shopkeeper wants to do.
    Returns: {intent, customer, amount, raw}
    """
    text_lower = text.lower().strip()
    result = {
        "intent": "unknown",
        "customer": None,
        "amount": None,
        "raw": text
    }

    # Payment keywords
    payment_keywords = ["diya", "diye", "payment", "jama", "jma", "paid", "de diya", "de diye"]
    # Credit keywords
    credit_keywords = ["udhaar", "udhar", "credit", "lena", "dena", "baaki", "baki"]
    # Query keywords
    query_keywords = ["total", "kitna", "kitni", "balance", "baaki", "baki", "hisab", "account"]
    # Today summary
    today_keywords = ["aaj", "today", "aaj ka"]

    amount = extract_amount(text_lower)
    result["amount"] = amount

    # Extract possible customer name (simple heuristic: first proper-looking word)
    # In real use, better to use LLM. Here we keep it lightweight.
    words = re.findall(r'[a-zA-Z\u0900-\u097F]+', text)
    # Filter common stop words
    stop = {"ka", "ki", "ke", "ko", "se", "mein", "me", "hai", "tha", "thi", "the",
            "udhaar", "udhar", "diya", "diye", "total", "kitna", "aaj", "kal", "parso",
            "rupees", "rupaye", "rs", "and", "the", "of", "for", "nahi", "nahin"}
    candidates = [w for w in words if w.lower() not in stop and len(w) > 2]

    if candidates:
        result["customer"] = candidates[0].title()

    # Intent detection order matters
    if any(k in text_lower for k in today_keywords) and any(k in text_lower for k in ["udhaar", "kitna", "total"]):
        result["intent"] = "today_summary"
    elif any(k in text_lower for k in query_keywords) and result["customer"]:
        result["intent"] = "query_balance"
    elif any(k in text_lower for k in payment_keywords) and amount:
        result["intent"] = "add_payment"
    elif any(k in text_lower for k in credit_keywords) and amount:
        result["intent"] = "add_credit"
    elif amount and result["customer"]:
        # Default to credit if amount + name present
        result["intent"] = "add_credit"
    elif any(k in text_lower for k in query_keywords):
        result["intent"] = "query_balance"

    return result


def process_command(text: str) -> str:
    """
    Main entry: take spoken/text command → return natural language reply.
    """
    parsed = detect_intent(text)
    intent = parsed["intent"]
    customer = parsed["customer"]
    amount = parsed["amount"]

    if intent == "add_credit":
        if not customer or not amount:
            return "Customer ka naam aur amount dono batao. Jaise: Ramesh ka 340 udhaar"
        result = db.add_transaction(customer, amount, "credit")
        return result["message"]

    elif intent == "add_payment":
        if not customer or not amount:
            return "Kisne kitna diya? Jaise: Ramesh ne 200 diya"
        result = db.add_transaction(customer, amount, "payment")
        return result["message"]

    elif intent == "query_balance":
        if not customer:
            return "Kis customer ka balance chahiye?"
        # Check if multiple similar names
        matches = db.find_customers_by_name(customer)
        if len(matches) > 1:
            names = ", ".join(matches[:3])
            return f"Kaunsa {customer}? {names} mein se?"
        balance = db.get_balance(customer)
        if balance == 0 and not matches:
            return f"{customer} ka koi record nahi mila."
        return f"{customer} ka total udhaar ₹{balance:.0f} hai."

    elif intent == "today_summary":
        summary = db.get_today_summary()
        return (f"Aaj ka hisab: ₹{summary['total_credit']:.0f} udhaar diya, "
                f"₹{summary['total_payment']:.0f} payment aaya.")

    else:
        return ("Samajh nahi aaya. Aap bol sakte ho:\n"
                "- Ramesh ka 340 udhaar\n"
                "- Ramesh ne 200 diya\n"
                "- Ramesh ka total\n"
                "- Aaj kitna udhaar gaya")
