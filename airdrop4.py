import csv
import subprocess
import time
import base58
import os
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()
TOKEN_ADDRESS = os.getenv("TOKEN_ADDRESS")
MIN_AMOUNT = 45_000_000
MAX_AMOUNT = 50_000_000
CSV_FILE = "adreses.csv"
LOG_FILE = "log.txt"
DELAY_SECONDS = int(os.getenv("DELAY_SECONDS"))
MAX_WORKERS = int(os.getenv("MAX_WORKERS"))  # Mainnet  5-7
MAX_RETRIES = 3
RETRY_DELAY = 2  # sekundes starp mēģinājumiem

if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)

def is_valid_pubkey(pubkey: str) -> bool:
    try:
        decoded = base58.b58decode(pubkey)
        return len(decoded) == 32
    except Exception:
        return False

def log_error(message: str):
    with open(LOG_FILE, "a") as log:
        log.write(message + "\n")

def send_tokens(index, pubkey):
    if not is_valid_pubkey(pubkey):
        msg = f"[{index}] ❌ Nederīgs pubkey: {pubkey}"
        print(msg)
        log_error(f"[{index}] INVALID PUBKEY: {pubkey}")
        return True  # Skaitām kā "apstrādātu", jo nav jēgas mēģināt vēlreiz

    amount = str(random.randint(MIN_AMOUNT, MAX_AMOUNT))
    print(f"[{index}] ➜ Send {amount} tokens to {pubkey}...")

    cmd = [
        "spl-token", "transfer",
        TOKEN_ADDRESS, amount, pubkey,
        "--fund-recipient",
        "--allow-unfunded-recipient"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"[{index}] ✅ OK: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[{index}] ❌ Error: {e.stderr.strip()}")
        log_error(f"[{index}] ERROR to {pubkey}: {e.stderr.strip()}")
        return False

def send_tokens_with_retry(index, pubkey):
    for attempt in range(1, MAX_RETRIES + 1):
        success = send_tokens(index, pubkey)
        if success:
            break
        if attempt < MAX_RETRIES:
            print(f"[{index}] ➡️ Try another time ({attempt}/{MAX_RETRIES}) after {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
    else:
        print(f"[{index}] ❌ Can't to send after {MAX_RETRIES} tryies.")
        log_error(f"[{index}] FAILED AFTER RETRIES: {pubkey}")

# Solana config (mainnet vai devnet)
# subprocess.run(["solana", "config", "set", "--url", "https://api.mainnet-beta.solana.com"], check=True)
subprocess.run(["solana", "config", "set", "--url", "https://api.devnet.solana.com"], check=True)
# Nolasām adreses no CSV
with open(CSV_FILE, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    pubkeys = [(i, row.get("pubkey", "").strip()) for i, row in enumerate(reader, 1)]

# Paralēlā izpilde ar retry
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(send_tokens_with_retry, index, pubkey) for index, pubkey in pubkeys]
    for future in as_completed(futures):
        pass  # Ja vēlies, vari apstrādāt rezultātus šeit

print("Work finished.")