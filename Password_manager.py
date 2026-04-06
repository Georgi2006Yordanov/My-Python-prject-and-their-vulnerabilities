import tkinter as tk
from tkinter import messagebox, simpledialog
from cryptography.fernet import Fernet
import json
import os
import base64
import secrets
import string
import re  # Увери се, че re е импортнат
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptoEngine:
    def __init__(self, master_password):
        # Валидираме паролата преди всичко останало
        self._validate_password(master_password)

        # Статичен salt (за учебни цели). В реално приложение трябва да е уникален.
        salt = b'\x14\xeb\xef\x02\x1c\x94\x11\xde'

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        self.fernet = Fernet(key)

    def _validate_password(self, password):
        # Поправка: Използваме re.match вместо self.match
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$"
        if not re.match(pattern, password):
            raise ValueError(
                "Паролата трябва да е поне 12 символа и да съдържа: "
                "главна буква, малка буква, цифра и специален знак (@$!%*?&)."
            )

    def encrypt(self, data):
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data):
        # Добавяме try-except тук, в случай че ключът е грешен
        try:
            return self.fernet.decrypt(encrypted_data.encode()).decode()
        except Exception:
            raise Exception("Грешка при декриптиране. Вероятно грешна Master Password.")


class PasswordManager(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Modern Password Manager")
        self.geometry("750x550")

        self.db_file = "passwords.json"
        self.crypto = None

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.show_login_screen()

    def show_login_screen(self):
        self.login_frame = tk.Frame(self.container, bg="#f0f0f0")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(self.login_frame, text="Password Manager", font=("Arial", 24, "bold"), bg="#f0f0f0").pack(pady=20)
        tk.Label(self.login_frame, text="Въведете Master Password:", font=("Arial", 11), bg="#f0f0f0").pack()

        self.pwd_entry = tk.Entry(self.login_frame, show="*", width=35, font=("Arial", 11))
        self.pwd_entry.pack(pady=10)
        self.pwd_entry.focus_set()

        btn = tk.Button(self.login_frame, text="Влез / Създай", command=self.login_attempt, width=20, bg="#4CAF50",
                        fg="white",
                        font=("Arial", 11, "bold"))
        btn.pack(pady=15)
        self.bind('<Return>', lambda e: self.login_attempt())

    def login_attempt(self):
        password = self.pwd_entry.get()
        if not password:
            messagebox.showwarning("Грешка", "Моля, въведете парола!")
            return

        try:
            # Опит за създаване на крипто енджин (тук се задейства RegEx проверката)
            self.crypto = CryptoEngine(password)
            self.unbind('<Return>')
            self.login_frame.destroy()
            self.setup_main_ui()
        except ValueError as e:
            messagebox.showerror("Слаба парола", str(e))

    def setup_main_ui(self):
        self.main_frame = tk.Frame(self.container)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        content_frame = tk.Frame(self.main_frame)
        content_frame.pack(fill="both", expand=True)

        # Лява част - Форма
        self.form_frame = tk.LabelFrame(content_frame, text="Добави нов запис", font=("Arial", 11, "bold"), padx=15,
                                        pady=15)
        self.form_frame.pack(side="left", fill="y", padx=(0, 20))

        tk.Label(self.form_frame, text="Уебсайт / Услуга:").pack(anchor="w")
        self.entry_site = tk.Entry(self.form_frame, width=30)
        self.entry_site.pack(pady=(0, 10))

        tk.Label(self.form_frame, text="Имейл / Потребител:").pack(anchor="w")
        self.entry_email = tk.Entry(self.form_frame, width=30)
        self.entry_email.pack(pady=(0, 10))

        tk.Label(self.form_frame, text="Парола:").pack(anchor="w")
        pwd_frame = tk.Frame(self.form_frame)
        pwd_frame.pack(pady=(0, 10))

        self.entry_pass = tk.Entry(pwd_frame, width=20, show="*")
        self.entry_pass.pack(side="left")

        btn_gen = tk.Button(pwd_frame, text="Ген.", command=self.generate_password_field)
        btn_gen.pack(side="left", padx=5)

        btn_save = tk.Button(self.form_frame, text="Запази в сейфа", command=self.save_entry,
                             bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
        btn_save.pack(fill="x", pady=(20, 0))

        # Дясна част - Списък
        self.list_frame = tk.LabelFrame(content_frame, text="Запазени пароли", font=("Arial", 11, "bold"), padx=15,
                                        pady=15)
        self.list_frame.pack(side="right", fill="both", expand=True)

        list_scroll = tk.Scrollbar(self.list_frame)
        list_scroll.pack(side="right", fill="y")

        self.pwd_listbox = tk.Listbox(self.list_frame, font=("Arial", 10), yscrollcommand=list_scroll.set)
        self.pwd_listbox.pack(side="left", fill="both", expand=True)
        list_scroll.config(command=self.pwd_listbox.yview)

        # Контроли отдолу
        controls_frame = tk.Frame(self.main_frame)
        controls_frame.pack(fill="x", pady=(20, 0))

        tk.Button(controls_frame, text="Копирай парола", command=self.get_selected_password).pack(side="left", padx=5)
        tk.Button(controls_frame, text="Изтрий запис", command=self.delete_entry).pack(side="left", padx=5)
        tk.Button(controls_frame, text="Изход", command=self.logout).pack(side="right", padx=5)

        self.populate_list()

    def generate_password_field(self):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        pwd = ''.join(secrets.choice(alphabet) for i in range(16))
        self.entry_pass.delete(0, tk.END)
        self.entry_pass.insert(0, pwd)
        # Временно показване на паролата
        self.entry_pass.config(show="")
        self.after(3000, lambda: self.entry_pass.config(show="*"))

    def load_data(self):
        if not os.path.exists(self.db_file):
            return {}
        try:
            with open(self.db_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def populate_list(self):
        self.pwd_listbox.delete(0, tk.END)
        data = self.load_data()
        for site in data.keys():
            self.pwd_listbox.insert(tk.END, site)

    def save_entry(self):
        site = self.entry_site.get()
        email = self.entry_email.get()
        pwd = self.entry_pass.get()

        if not site or not email or not pwd:
            messagebox.showwarning("Грешка", "Моля, попълнете всички полета!")
            return

        try:
            encrypted_pwd = self.crypto.encrypt(pwd)
            data = self.load_data()
            data[site] = {"email": email, "password": encrypted_pwd}

            with open(self.db_file, "w") as f:
                json.dump(data, f, indent=4)

            messagebox.showinfo("Успех", f"Записът за {site} е запазен!")
            self.entry_site.delete(0, tk.END)
            self.entry_email.delete(0, tk.END)
            self.entry_pass.delete(0, tk.END)
            self.populate_list()
        except Exception as e:
            messagebox.showerror("Грешка", f"Проблем при запис: {e}")

    def get_selected_password(self):
        try:
            selected_idx = self.pwd_listbox.curselection()[0]
            site_key = self.pwd_listbox.get(selected_idx)

            data = self.load_data()
            if site_key in data:
                encrypted_pwd = data[site_key]["password"]
                decrypted_pwd = self.crypto.decrypt(encrypted_pwd)

                self.clipboard_clear()
                self.clipboard_append(decrypted_pwd)
                messagebox.showinfo("Копирано", f"Паролата за {site_key} е в клипборда!")
        except IndexError:
            messagebox.showwarning("Внимание", "Изберете запис от списъка!")
        except Exception as e:
            messagebox.showerror("Грешка", str(e))

    def delete_entry(self):
        try:
            selected_idx = self.pwd_listbox.curselection()[0]
            site_key = self.pwd_listbox.get(selected_idx)

            if messagebox.askyesno("Потвърждение", f"Изтриване на {site_key}?"):
                data = self.load_data()
                if site_key in data:
                    del data[site_key]
                    with open(self.db_file, "w") as f:
                        json.dump(data, f, indent=4)
                    self.populate_list()
        except IndexError:
            messagebox.showwarning("Внимание", "Изберете запис!")

    def logout(self):
        self.crypto = None
        self.main_frame.destroy()
        self.show_login_screen()


if __name__ == "__main__":
    app = PasswordManager()
    app.mainloop()