import pyotp
from SmartApi import SmartConnect
import time
import logging

# --- YAHAN APNI DETAIL BHAR ---
API_KEY = "ZnpCcXHa"
CLIENT_ID = "AABS241306"
PASSWORD = "9783"
TOTP_SECRET = "AABS241306" # smartapi.angelone.in wala secret
# ------------------------------

print("AAKAR BOT STARTED...")
try:
    totp = pyotp.TOTP(TOTP_SECRET).generate()
    print(f"TOTP Generated: {totp}")
    smartApi = SmartConnect(api_key=API_KEY)
    data = smartApi.generateSession(CLIENT_ID, PASSWORD, totp)
    print("LOGIN SUCCESS")
    print(data)
    while True:
        print("Live dekh raha hu...")
        time.sleep(1)
except Exception as e:
    print(f"LOGIN FAILED: {e}")
    time.sleep(10)