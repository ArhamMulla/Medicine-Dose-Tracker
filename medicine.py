import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import csv

class MedicineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Medicine Reminder App")
        self.root.geometry("800x600")

        self.users = {}
        self.current_user = None

        self.title_label = tk.Label(root, text="Medicine Reminder App", font=("Helvetica", 20, "bold"))
        self.title_label.pack(pady=20)

        self.login_frame = tk.Frame(root)
        self.login_frame.pack(padx=20, pady=10)

        self.med_frame = tk.Frame(root)
        self.med_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        self.med_frame.grid_rowconfigure(0, weight=1)
        self.med_frame.grid_columnconfigure(0, weight=1)

        self.load_user_data()
        self.create_login_frame()

    def load_user_data(self):
        try:
            with open("medicine_data.csv", mode="r") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    username = row[0]
                    medicine = {"name": row[1], "dosage": row[2], "frequency": row[3]}
                    if username not in self.users:
                        self.users[username] = []
                    self.users[username].append(medicine)
        except FileNotFoundError:
            pass

    def create_login_frame(self):
        self.login_frame.destroy()
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(padx=20, pady=10)

        self.login_label = tk.Label(self.login_frame, text="Login or Register", font=("Helvetica", 14, "bold"))
        self.login_label.grid(row=0, columnspan=2, pady=5)

        self.username_label = tk.Label(self.login_frame, text="Username:")
        self.username_label.grid(row=1, column=0, sticky="w")

        self.username_entry = tk.Entry(self.login_frame, font=("Helvetica", 12))
        self.username_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.login_button = tk.Button(self.login_frame, text="Login / Register", command=self.login_or_register, bg="#4caf50", fg="white", font=("Helvetica", 12))
        self.login_button.grid(row=2, columnspan=2, pady=10)

    def login_or_register(self):
        username = self.username_entry.get()
        if username in self.users:
            self.current_user = username
            self.switch_to_med_frame()
        else:
            confirm_register = messagebox.askyesno("Registration", "User not found. Register as a new user?")
            if confirm_register:
                self.register_user(username)
                self.switch_to_med_frame()

    def register_user(self, username):
        self.users[username] = []
        self.current_user = username

    def switch_to_med_frame(self):
        self.login_frame.pack_forget()
        self.create_med_frame()

    def create_med_frame(self):
        self.med_frame.destroy()
        self.med_frame = tk.Frame(self.root)
        self.med_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        self.med_frame.grid_rowconfigure(0, weight=1)
        self.med_frame.grid_columnconfigure(0, weight=1)

        self.med_name_label = tk.Label(self.med_frame, text="Medicine Name:", font=("Helvetica", 12))
        self.med_name_label.grid(row=0, column=0, sticky="w")

        self.med_name_entry = tk.Entry(self.med_frame, font=("Helvetica", 12))
        self.med_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.med_dosage_label = tk.Label(self.med_frame, text="Dosage:", font=("Helvetica", 12))
        self.med_dosage_label.grid(row=1, column=0, sticky="w")

        self.med_dosage_entry = tk.Entry(self.med_frame, font=("Helvetica", 12))
        self.med_dosage_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.med_frequency_label = tk.Label(self.med_frame, text="Frequency (minutes):", font=("Helvetica", 12))
        self.med_frequency_label.grid(row=2, column=0, sticky="w")

        self.med_frequency_entry = tk.Entry(self.med_frame, font=("Helvetica", 12))
        self.med_frequency_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.add_med_button = tk.Button(self.med_frame, text="Add Medicine", command=self.add_medicine, bg="#4caf50", fg="white", font=("Helvetica", 12))
        self.add_med_button.grid(row=3, columnspan=2, pady=10)

        self.display_button = tk.Button(self.med_frame, text="Display Medicines", command=self.display_medicines, bg="#2196f3", fg="white", font=("Helvetica", 12))
        self.display_button.grid(row=4, columnspan=2, pady=10)

        self.delete_button = tk.Button(self.med_frame, text="Delete Medicine", command=self.delete_medicine, bg="#f44336", fg="white", font=("Helvetica", 12))
        self.delete_button.grid(row=5, columnspan=2, pady=10)

        self.tree = ttk.Treeview(self.med_frame, columns=("Name", "Dosage", "Frequency"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Dosage", text="Dosage")
        self.tree.heading("Frequency", text="Frequency (minutes)")
        self.tree.grid(row=6, columnspan=2, padx=10, pady=10)

    def add_medicine(self):
        med_name = self.med_name_entry.get()
        med_dosage = self.med_dosage_entry.get()
        med_frequency = self.med_frequency_entry.get()

        if med_name and med_dosage and med_frequency:
            self.users[self.current_user].append({"name": med_name, "dosage": med_dosage, "frequency": med_frequency})
            self.calculate_next_dose(self.users[self.current_user][-1])
            messagebox.showinfo("Success", "Medicine added successfully!")
            self.save_to_csv()
            self.clear_med_entries()
            self.schedule_medicine_reminder(med_name, med_frequency)
        else:
            messagebox.showwarning("Warning", "Please enter medicine information.")

    def save_to_csv(self):
        with open("medicine_data.csv", mode="w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            for user, medicines in self.users.items():
                for med in medicines:
                    writer.writerow([user, med["name"], med["dosage"], med["frequency"]])

    def schedule_medicine_reminder(self, med_name, frequency):
        frequency_minutes = int(frequency)
        self.calculate_next_dose({"name": med_name, "frequency": frequency_minutes})
        threading.Thread(target=self.check_medicines_schedule, daemon=True).start()

    def check_medicines_schedule(self):
        while True:
            current_time = time.time()
            for med in self.users.get(self.current_user, []):
                if current_time >= med['next_dose']:
                    self.show_notification(med['name'])
                    self.calculate_next_dose(med)
            time.sleep(60)  # Check every minute

    def show_notification(self, med_name):
        notification_title = "Medicine Reminder"
        notification_text = f"It's time to take your {med_name}"
        messagebox.showinfo(notification_title, notification_text)

    def calculate_next_dose(self, med):
        frequency_minutes = int(med['frequency'])
        med['next_dose'] = time.time() + (frequency_minutes * 60)

    def display_medicines(self):
        self.tree.delete(*self.tree.get_children())
        user_medicines = self.users.get(self.current_user, [])
        for med in user_medicines:
            self.tree.insert("", "end", values=(med["name"], med["dosage"], med["frequency"]))

    def delete_medicine(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a medicine to delete.")
            return

        for item in selected_item:
            med_name = self.tree.item(item, "values")[0]
            for med in self.users.get(self.current_user, []):
                if med['name'] == med_name:
                    self.users[self.current_user].remove(med)
                    self.save_to_csv()
                    self.display_medicines()
                    break

    def clear_med_entries(self):
        self.med_name_entry.delete(0, tk.END)
        self.med_dosage_entry.delete(0, tk.END)
        self.med_frequency_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = MedicineApp(root)
    root.mainloop()