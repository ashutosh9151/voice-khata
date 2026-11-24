"""
Voice Khata - Text Interface (for testing + fallback)
Run this on mobile/Termux or laptop for testing ledger logic.
"""

import os
from dotenv import load_dotenv
from ledger import process_command, init_db
from prompts.system_prompt import SYSTEM_PROMPT

load_dotenv()


def main():
    init_db()
    print("=" * 50)
    print("  Khata Mitra - Voice Khata (Text Mode)")
    print("  BolBharat × Gnani Voice AI Challenge")
    print("=" * 50)
    print()
    print("AI Disclosure: Main ek AI assistant hoon (Khata Mitra).")
    print("Main aapka kirana udhaar khata sambhalta hoon.\n")
    print("Examples:")
    print("  • Ramesh ka 340 udhaar")
    print("  • Ramesh ne 200 diya")
    print("  • Ramesh ka total")
    print("  • Aaj kitna udhaar gaya")
    print("  • exit  → band karne ke liye")
    print("-" * 50)

    while True:
        try:
            user_input = input("\nShopkeeper: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "bye", "band"]:
                print("Khata Mitra: Dhanyavaad! Phir milenge.")
                break

            reply = process_command(user_input)
            print(f"Khata Mitra: {reply}")

        except KeyboardInterrupt:
            print("\nKhata Mitra: Bye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
