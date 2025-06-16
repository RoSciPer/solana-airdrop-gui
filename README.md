# Solana Token Airdrop Tool

This repository contains two Python scripts for sending SPL tokens (airdropping) to multiple Solana addresses. The tool supports both command-line execution and a graphical user interface (GUI).

## 🔧 airdrop4.py — Command-Line Tool

This script reads public keys from a CSV file and sends tokens using `spl-token transfer` via terminal.

Before running, edit the `.env` file with the appropriate values:

```env
TOKEN_ADDRESS=go9KJV94e4e4a8Npja9VLd2ehbxi2dtydtq7Kzbpump
DELAY_SECONDS=1
MAX_WORKERS=5
```
Run with:

```bash
python3 airdrop4.py
```
🖥️ airdrop5.py — GUI Version
A simple Tkinter-based GUI for performing token airdrops. The GUI allows manual input of:

Token address

Delay between transactions

Maximum number of concurrent threads

CSV file with public keys

Launch with:

```bash
python3 airdrop5.py
```

📌 Note: This version currently uses the default wallet configured via solana-cli. For more control (like connecting a wallet or entering a private key), future versions may include wallet login support.

You can also convert the GUI version into a standalone Windows application using tools like pyinstaller.

📁 Screenshots
GUI start screen:


Airdrop in progress:


Finished operation:


Terminal launch example:


📂 .gitignore
Sensitive and unnecessary files like the virtual environment folder, .env, and test scripts (e.g., airdrop1.py) are excluded using .gitignore.

📋 Requirements
Install required Python packages:

bash
Kopēt
Rediģēt
pip install -r requirements.txt
Ensure you have solana-cli and spl-token-cli installed and configured.

🔐 Security
Never upload your .env or private keys to public repositories. Use .gitignore to keep sensitive data private.

License
MIT License
