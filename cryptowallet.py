import tkinter as tk
from tkinter import messagebox, simpledialog, font
import sqlite3
import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa

class CryptoWalletApp:
    def __init__(self, master):
        self.master = master
        master.title("Secure Cryptocurrency Wallet ™")
        master.geometry("600x430")  # Increased height to accommodate the trademark label
        master.configure(bg="#292929")  # Vintage-style background color

        self.custom_font = font.Font(family="Courier", size=12, weight="bold")  # Vintage-style bold font

        self.conn = sqlite3.connect('transaction.db')
        self.create_tables()

        self.check_pin_ui()
        self.add_trademark_label()  # Adding the trademark label

    def create_tables(self):
        self.conn.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      pin TEXT)''')

        self.conn.execute('''CREATE TABLE IF NOT EXISTS transactions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      timestamp TEXT,
                      recipient TEXT,
                      amount REAL,
                      sender TEXT)''')

    def check_pin_ui(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users")
        if not cursor.fetchone():
            self.create_pin_ui()
        else:
            self.enter_pin_ui()

    def create_pin_ui(self):
        self.pin_label = tk.Label(self.master, text="Create a 4-digit PIN:", bg="#292929", fg="#dcdcdc", font=self.custom_font)
        self.pin_label.pack(pady=10)

        self.pin_entry = tk.Entry(self.master, show="*", font=self.custom_font)
        self.pin_entry.pack(pady=5)

        self.pin_button = tk.Button(self.master, text="Create PIN", command=self.save_pin, bg="#555555", fg="#dcdcdc", font=self.custom_font)
        self.pin_button.pack(pady=5)

    def save_pin(self):
        pin = self.pin_entry.get()
        if len(pin) != 4 or not pin.isdigit():
            messagebox.showerror("Invalid PIN", "PIN must be a 4-digit number.")
            return

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users (pin) VALUES (?)", (pin,))
        self.conn.commit()

        self.enter_pin_ui()

    def enter_pin_ui(self):
        self.pin_label = tk.Label(self.master, text="Enter your 4-digit PIN:", bg="#292929", fg="#dcdcdc", font=self.custom_font)
        self.pin_label.pack(pady=10)

        self.pin_entry = tk.Entry(self.master, show="*", font=self.custom_font)
        self.pin_entry.pack(pady=5)

        self.pin_button = tk.Button(self.master, text="Enter PIN", command=self.verify_pin, bg="#555555", fg="#dcdcdc", font=self.custom_font)
        self.pin_button.pack(pady=5)

        self.forgot_pin_button = tk.Button(self.master, text="Forgot PIN?", command=self.reset_pin_ui, bg="#555555", fg="#dcdcdc", font=self.custom_font)
        self.forgot_pin_button.pack(pady=5)

    def verify_pin(self):
        entered_pin = self.pin_entry.get()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users")
        correct_pin = cursor.fetchone()[1]
        if entered_pin == correct_pin:
            self.open_tool()
        else:
            messagebox.showerror("Incorrect PIN", "Incorrect PIN. Please try again.")
            self.pin_entry.delete(0, tk.END)  # Clear the entry field

    def open_tool(self):
        self.pin_label.pack_forget()
        self.pin_entry.pack_forget()
        self.pin_button.pack_forget()
        self.forgot_pin_button.pack_forget()

        self.balance_label = tk.Label(self.master, text="Balance: 2000000 cryptocurrency", bg="#292929", fg="#dcdcdc", font=self.custom_font)
        self.balance_label.pack(pady=10)

        self.transaction_button = tk.Button(self.master, text="View Transaction History", command=self.view_transaction_history, bg="#555555", fg="#dcdcdc", font=self.custom_font)
        self.transaction_button.pack(pady=5)

        self.send_button = tk.Button(self.master, text="Send Cryptocurrency", command=self.send_crypto, bg="#555555", fg="#dcdcdc", font=self.custom_font)
        self.send_button.pack(pady=5)

        self.receive_button = tk.Button(self.master, text="Receive Cryptocurrency", command=self.receive_crypto, bg="#555555", fg="#dcdcdc", font=self.custom_font)
        self.receive_button.pack(pady=5)

        self.backup_button = tk.Button(self.master, text="Backup Wallet", command=self.backup_wallet, bg="#555555", fg="#dcdcdc", font=self.custom_font)
        self.backup_button.pack(pady=5)

        self.delete_button = tk.Button(self.master, text="Delete Transaction History", command=self.delete_transaction_history, bg="#555555", fg="#dcdcdc", font=self.custom_font)
        self.delete_button.pack(pady=5)

        self.exit_button = tk.Button(self.master, text="EXIT", command=self.exit_app, bg="#555555", fg="#dcdcdc", font=self.custom_font)
        self.exit_button.pack(pady=5)

    def view_transaction_history(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM transactions")
        result = cursor.fetchall()
        if not result:
            messagebox.showinfo("Transaction History", "No transactions yet.")
        else:
            history_text = "\n".join([f"{row[1]}: {row[3]} cryptocurrency sent to {row[2]} by {row[4]}" for row in result])
            messagebox.showinfo("Transaction History", history_text)

    def send_crypto(self):
        recipient = simpledialog.askstring("Send Cryptocurrency", "Enter recipient's public key:", parent=self.master)
        if not recipient:
            return

        try:
            amount = float(simpledialog.askstring("Send Cryptocurrency", "Enter amount to send:", parent=self.master))
        except ValueError:
            messagebox.showerror("Error", "Invalid amount. Please enter a valid number.", parent=self.master)
            return

        if amount <= 0:
            messagebox.showerror("Error", "Amount must be greater than zero.", parent=self.master)
            return

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO transactions (timestamp, recipient, amount, sender) VALUES (?, ?, ?, ?)", (timestamp, recipient, amount, 'self'))
        self.conn.commit()

        messagebox.showinfo("Success", f"Sent {amount} cryptocurrency to {recipient}.")
        self.update_balance_label()

    def receive_crypto(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        messagebox.showinfo("Receive Cryptocurrency", f"Your public key:\n{public_key.decode()}", parent=self.master)

    def backup_wallet(self):
        filename = simpledialog.askstring("Backup Wallet", "Enter backup file name:", parent=self.master)
        if not filename:
            return

        try:
            with open(filename, 'w') as f:
                cursor = self.conn.cursor()
                cursor.execute("SELECT * FROM transactions")
                transactions = cursor.fetchall()
                for transaction in transactions:
                    f.write(','.join(map(str, transaction)) + '\n')

            messagebox.showinfo("Backup", "Wallet backup created successfully.", parent=self.master)
        except Exception as e:
            messagebox.showerror("Backup Error", f"An error occurred while backing up the wallet: {e}", parent=self.master)

    def delete_transaction_history(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM transactions")
            self.conn.commit()
            messagebox.showinfo("Delete Transaction History", "Transaction history deleted successfully.", parent=self.master)
        except Exception as e:
            messagebox.showerror("Delete Error", f"An error occurred while deleting transaction history: {e}", parent=self.master)

    def update_balance_label(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE sender='self'")
        sent_amount = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(amount) FROM transactions WHERE recipient='self'")
        received_amount = cursor.fetchone()[0] or 0

        balance = 2000000 - sent_amount + received_amount
        self.balance_label.config(text=f"Balance: {balance} cryptocurrency")

    def reset_pin_ui(self):
        confirm = messagebox.askyesno("Reset PIN", "Are you sure you want to reset your PIN? This action cannot be undone.", parent=self.master)
        if confirm:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM users")
            self.conn.commit()
            self.create_pin_ui()

    def add_trademark_label(self):
        trademark_label = tk.Label(self.master, text="© Prashid 2024", bg="#292929", fg="#dcdcdc", font=("Helvetica", 10, "italic"))
        trademark_label.pack(side=tk.BOTTOM, pady=5)  # Adjust placement as needed

    def exit_app(self):
        self.master.destroy()  # Close the current window
        root = tk.Tk()  # Create a new window
        app = CryptoWalletApp(root)  # Initialize the CryptoWalletApp in the new window
        root.mainloop()  # Run the new window

def main():
    root = tk.Tk()
    app = CryptoWalletApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()