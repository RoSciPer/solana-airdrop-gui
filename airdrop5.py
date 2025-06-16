import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import csv
import subprocess
import time
import base58
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

MIN_AMOUNT = 45_000_000
MAX_AMOUNT = 50_000_000
LOG_FILE = "log.txt"
MAX_RETRIES = 3
RETRY_DELAY = 2

def is_valid_pubkey(pubkey: str) -> bool:
    try:
        decoded = base58.b58decode(pubkey)
        return len(decoded) == 32
    except Exception:
        return False

def log_error(message: str):
    with open(LOG_FILE, "a") as log:
        log.write(message + "\n")

def send_tokens(index, pubkey, token_address):
    if not is_valid_pubkey(pubkey):
        msg = f"[{index}] ❌ Nederīgs pubkey: {pubkey}"
        print(msg)
        log_error(f"[{index}] INVALID PUBKEY: {pubkey}")
        return True

    amount = str(random.randint(MIN_AMOUNT, MAX_AMOUNT))
    print(f"[{index}] ➜ Send {amount} tokens to {pubkey}...")

    cmd = [
        "spl-token", "transfer",
        token_address, amount, pubkey,
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

def send_tokens_with_retry(index, pubkey, token_address):
    for attempt in range(1, MAX_RETRIES + 1):
        success = send_tokens(index, pubkey, token_address)
        if success:
            break
        if attempt < MAX_RETRIES:
            print(f"[{index}] ➡️ Try another time ({attempt}/{MAX_RETRIES}) after {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
    else:
        print(f"[{index}] ❌ Can't to send after {MAX_RETRIES} tryies.")
        log_error(f"[{index}] FAILED AFTER RETRIES: {pubkey}")

def start_sending(token_address, delay_seconds, max_workers, csv_file):
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    # Solana config (mainnet vai devnet)
    subprocess.run(["solana", "config", "set", "--url", "https://api.devnet.solana.com"], check=True)

    # subprocess.run(["solana", "config", "set", "--url", "https://api.mainnet-beta.solana.com"], check=True)

    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        pubkeys = [(i, row.get("pubkey", "").strip()) for i, row in enumerate(reader, 1)]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(send_tokens_with_retry, index, pubkey, token_address) for index, pubkey in pubkeys]
        for future in as_completed(futures):
            pass

    print("Work finished.")

def browse_csv():
    file_path = filedialog.askopenfilename(
        title="Izvēlies CSV failu",
        filetypes=[("CSV faili", "*.csv")]
    )
    csv_entry.delete(0, tk.END)
    csv_entry.insert(0, file_path)

def on_submit():
    token_address = token_entry.get().strip()
    delay = delay_entry.get().strip()
    workers = workers_entry.get().strip()
    csv_file = csv_entry.get().strip()

    if not token_address or not delay.isdigit() or not workers.isdigit() or not csv_file:
        messagebox.showerror("Mistake", "Fill all fields!")
        return

    delay_seconds = int(delay)
    max_workers = int(workers)

    # Palaist sūtīšanu atsevišķā pavedienā, lai GUI neaizsaltu
    threading.Thread(target=start_sending, args=(token_address, delay_seconds, max_workers, csv_file), daemon=True).start()
    messagebox.showinfo("Info", "Sending process started!")

root = tk.Tk()
root.title("Tokens sender GUI")
root.geometry("1000x300") 

FONT = ("Helvetica", 16)

tk.Label(root, text="TOKEN_ADDRESS:").grid(row=0, column=0, sticky="e")
token_entry = tk.Entry(root, width=50, font=FONT)
token_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="DELAY_SECONDS:").grid(row=1, column=0, sticky="e")
delay_entry = tk.Entry(root, font=FONT)
delay_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="MAX_WORKERS:").grid(row=2, column=0, sticky="e")
workers_entry = tk.Entry(root, font=FONT)
workers_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(root, text="CSV fail:").grid(row=3, column=0, sticky="e")
csv_entry = tk.Entry(root, width=50, font=FONT)
csv_entry.grid(row=3, column=1, padx=5, pady=5)
browse_btn = tk.Button(root, text="Load file...", command=browse_csv)
browse_btn.grid(row=3, column=2, padx=5, pady=5)

submit_btn = tk.Button(root, font=FONT, text="Start to send", command=on_submit)
submit_btn.grid(row=4, column=1, pady=10)

root.mainloop()
