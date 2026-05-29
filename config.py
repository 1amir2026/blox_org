from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))   # ← این خط باید دقیقاً این باشد

REFERRAL_NEEDED = 5

print("✅ TOKEN و ADMIN_ID با موفقیت لود شدند!")
print(f"ADMIN_ID = {ADMIN_ID}")