import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import os
import oracledb
import re
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    return oracledb.connect(
        user="register",
        password="P@ssw0rd",
        dsn="localhost:1521/orcl"
    )

class GameApp:

    def __init__(self, root):
        self.current_user = None
        self.current_password = None
        self.user_connection = None
        self.current_game = None

        self.root = root
        self.root.title("Слова из слова")
        self.root.geometry("1200x675")
        self.root.resizable(False, False)

        self.root.update_idletasks()
        self.root.geometry(self.root.geometry())

        self.canvas = tk.Canvas(self.root, width=1200, height=675)
        self.canvas.pack(fill="both", expand=True)

        self.set_background_image()
        self.create_interface()

    def set_background_image(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "background.png")
        if not os.path.exists(image_path):
            self.canvas.configure(bg="#2c3e50")
            return
        self.bg_image = Image.open(image_path).resize((1500, 845))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

    def create_interface(self):
        self.canvas.create_text(
            50, 30,
            text="🏆 ТОП-20 ИГРОКОВ",
            font=("Arial", 20),
            fill="white",
            anchor="nw"
        )

        self.update_leaderboard()

        self.auth_btn = self.create_button(self.canvas, "Авторизация", self.login)
        self.auth_btn.place(x=1200, y=30)

        self.reg_btn = self.create_button(self.canvas, "Регистрация", self.register)
        self.reg_btn.place(x=1200, y=100)

        self.user_label = None
        self.logout_btn = None
        self.find_game_btn = None

    def show_user_controls(self):
        if self.auth_btn: 
            self.auth_btn.place_forget()
        if self.reg_btn: 
            self.reg_btn.place_forget()

        # Обновляем данные из leaderboard
        register_connection = get_db_connection()
        with register_connection.cursor() as cursor:
            cursor.execute("SELECT score FROM REGISTER.leaderboard WHERE username = :username", {"username": self.current_user})
            score = cursor.fetchone()
            if score:
                score_text = f" — Очки: {score[0]}"
            else:
                score_text = " — Очки: 0"
        register_connection.close()

        # Удаляем старый label если он существует
        if hasattr(self, 'user_label') and self.user_label:
            self.user_label.destroy()

        self.user_label = tk.Label(
            self.canvas,
            text=f"👤 {self.current_user}{score_text}",
            font=("Arial", 14, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        self.user_label.place(x=1200, y=30)

        # Обновляем другие элементы управления
        if not hasattr(self, 'find_game_btn') or not self.find_game_btn:
            self.find_game_btn = self.create_button(self.canvas, "Найти игру", self.open_game_window)
        self.find_game_btn.place(x=1200, y=70)

        if not hasattr(self, 'logout_btn') or not self.logout_btn:
            self.logout_btn = self.create_button(self.canvas, "Выход", self.logout)
        self.logout_btn.place(x=1200, y=110)

    def logout(self):
        self.current_user = None
        self.current_password = None
        self.user_connection = None

        if self.user_label:
            self.user_label.destroy()
        if self.logout_btn:
            self.logout_btn.destroy()
        if self.find_game_btn:
            self.find_game_btn.destroy()

        self.auth_btn.place(x=1200, y=30)
        self.reg_btn.place(x=1200, y=100)

    def update_leaderboard(self):
        leaderboard_data = self.get_leaderboard_data()
        for i, (name, score) in enumerate(leaderboard_data, 1):
            self.canvas.create_text(
                50, 80 + i * 30,
                text=f"{i}. {name} — {score}",
                font=("Arial", 14),
                fill="white",
                anchor="nw"
            )

    def get_leaderboard_data(self):
        leaderboard_data = []
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT username, score
                FROM (
                    SELECT username, score
                    FROM leaderboard
                    ORDER BY score DESC
                )
                WHERE ROWNUM <= 20
            """)
            leaderboard_data = cursor.fetchall()
        connection.close()
        return leaderboard_data

    def create_button(self, parent, text, command):
        button = tk.Button(
            parent,
            text=text,
            font=("Arial", 14),
            width=25,
            command=command,
            bg="#3498db",
            fg="white",
            bd=0,
            highlightthickness=0,
            activebackground="#5dade2",
            cursor="hand2"
        )
        def on_enter(e): button.config(bg="#5dade2")
        def on_leave(e): button.config(bg="#3498db")
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        return button

    def login(self):
        connection = get_db_connection()
        login_window = tk.Toplevel(self.root)
        login_window.title("Авторизация")
        width = 400
        height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2) + 130)
        y = int((screen_height / 2) - (height / 2) + 20)
        login_window.geometry(f"{width}x{height}+{x}+{y}")
        login_window.configure(bg="#271b2f")
        login_window.transient(self.root)
        login_window.grab_set()
        login_window.focus_force()
        login_window.lift()

        container = tk.Frame(login_window, bg="#271b2f")
        container.pack(expand=True, fill="both")

        inner_frame = tk.Frame(container, bg="#271b2f")
        inner_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(inner_frame, text="Имя пользователя:", fg="white", bg="#271b2f", font=("Arial", 12)).pack(pady=(0, 5))
        username_entry = tk.Entry(inner_frame, font=("Arial", 12))
        username_entry.pack(pady=(0, 10), ipadx=5, ipady=2)

        tk.Label(inner_frame, text="Пароль:", fg="white", bg="#271b2f", font=("Arial", 12)).pack(pady=(0, 5))
        password_entry = tk.Entry(inner_frame, show="*", font=("Arial", 12))
        password_entry.pack(pady=(0, 20), ipadx=5, ipady=2)

        def execute_login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()

            if not username or not password:
                messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
                return

            try:
                with connection.cursor() as cursor:
                    cursor.callproc("LOGIN", [username, password])
                connection.commit()

                self.current_user = username
                self.current_password = password
                self.user_connection = oracledb.connect(
                    user=username,
                    password=password,
                    dsn="localhost:1521/orcl"
                )

                messagebox.showinfo("Успех", "Вы успешно вошли в систему!")
                login_window.destroy()
                self.show_user_controls()
                self.show_game_rules()

            except oracledb.DatabaseError as e:
                error_obj, = e.args
                error_code = error_obj.code
                
                # Проверяем, что это наша кастомная ошибка ORA-20008 (Неверный пароль)
                if error_code == 20008:
                    messagebox.showerror("Ошибка", "Неверный логин или пароль.")
                else:
                    # Для других ошибок базы данных показываем оригинальное сообщение
                    messagebox.showerror("Ошибка", f"Ошибка базы данных: {error_obj.message}")
                
            except Exception as e:
                # Для всех других ошибок показываем общее сообщение
                messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

        self.create_button(inner_frame, "Войти", execute_login).pack(pady=(10, 0))
        login_window.protocol("WM_DELETE_WINDOW", lambda: [connection.close(), login_window.destroy()])

    def show_game_rules(self):
        game_rules = self.user_connection.cursor().var(oracledb.CLOB)
        with self.user_connection.cursor() as cursor:
            cursor.callproc("register.GET_GAME_RULES", [self.current_user, game_rules])
        rules = game_rules.getvalue()

        rules_window = tk.Toplevel(self.root)
        rules_window.title("Правила игры")
        width = 750
        height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2) + 130)
        y = int((screen_height / 2) - (height / 2) + 20)
        rules_window.geometry(f"{width}x{height}+{x}+{y}")
        rules_window.configure(bg="#271b2f")
        rules_window.transient(self.root)
        rules_window.grab_set()
        rules_window.focus_force()
        rules_window.lift()

        container = tk.Frame(rules_window, bg="#271b2f")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        rules_label = tk.Label(container, text=rules, fg="white", bg="#271b2f", font=("Arial", 12), justify="left")
        rules_label.pack(pady=10)

        close_btn = tk.Button(container, text="Закрыть", font=("Arial", 12), command=lambda: self.on_rules_closed(rules_window))
        close_btn.pack(pady=10)
        rules_window.protocol("WM_DELETE_WINDOW", lambda: self.on_rules_closed(rules_window))

    def on_rules_closed(self, rules_window):
        rules_window.destroy()
        self.open_game_window()



























    def register(self):
        try:
            connection = get_db_connection()

            reg_window = tk.Toplevel(self.root)
            reg_window.title("Регистрация")
            width = 400
            height = 300
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = int((screen_width / 2) - (width / 2)+130)
            y = int((screen_height / 2) - (height / 2)+20)
            reg_window.geometry(f"{width}x{height}+{x}+{y}")

            reg_window.configure(bg="#271b2f")
            reg_window.transient(self.root)
            reg_window.grab_set()
            reg_window.focus_force()
            reg_window.lift()

            container = tk.Frame(reg_window, bg="#271b2f")
            container.pack(expand=True, fill="both", pady=20)

            tk.Label(container, text="Имя пользователя:", fg="white", bg="#271b2f", font=("Arial", 12)).pack(pady=(0, 5))
            username_entry = tk.Entry(container, font=("Arial", 12))
            username_entry.pack(pady=(0, 10), ipadx=5, ipady=2)

            tk.Label(container, text="Пароль:", fg="white", bg="#271b2f", font=("Arial", 12)).pack(pady=(0, 5))
            password_entry = tk.Entry(container, show="*", font=("Arial", 12))
            password_entry.pack(pady=(0, 10), ipadx=5, ipady=2)

            tk.Label(container, text="Повторите пароль:", fg="white", bg="#271b2f", font=("Arial", 12)).pack(pady=(0, 5))
            confirm_entry = tk.Entry(container, show="*", font=("Arial", 12))
            confirm_entry.pack(pady=(0, 20), ipadx=5, ipady=2)

            def execute_register():
                try:
                    with connection.cursor() as cursor:
                        cursor.callproc("REGISTER", [
                            username_entry.get(),
                            password_entry.get(),
                            confirm_entry.get()
                        ])
                    connection.commit()
                    messagebox.showinfo("Успех", "Регистрация завершена!")
                    reg_window.destroy()
                except oracledb.DatabaseError as e:
                    try:
                        error_obj, = e.args
                        raw_message = getattr(error_obj, "message", str(e))
                    except Exception:
                        raw_message = str(e)

                    # Удаляем префиксы ORA-xxxxx:
                    raw_message = re.sub(r"ORA-\d+:\s*", "", raw_message)

                    # Удаляем строки, содержащие трассировку или слово "line"
                    cleaned_lines = [
                        line for line in raw_message.splitlines()
                        if "line" not in line.lower() and not line.strip().startswith("на \"")
                    ]

                    error_message = "\n".join(cleaned_lines).strip()
                    messagebox.showerror("Ошибка", error_message or "Произошла неизвестная ошибка.")






            self.create_button(container, "Зарегистрироваться", execute_register).pack(pady=(10, 0))
            reg_window.protocol("WM_DELETE_WINDOW", lambda: [connection.close(), reg_window.destroy()])

        except Exception as e:
            messagebox.showerror("Ошибка подключения", str(e))

    def open_game_window(self):
        # Закрываем предыдущее окно, если оно есть
        if hasattr(self, 'game_menu_window') and self.game_menu_window.winfo_exists():
            self.game_menu_window.destroy()
        
        # Создаем новое окно
        self.game_menu_window = tk.Toplevel(self.root)
        self.game_menu_window.title("Выберите действие")
        
        # Центрируем окно
        width = 400
        height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2) + 130)
        y = int((screen_height / 2) - (height / 2) + 20)
        self.game_menu_window.geometry(f"{width}x{height}+{x}+{y}")

        self.game_menu_window.configure(bg="#271b2f")
        self.game_menu_window.transient(self.root)
        self.game_menu_window.grab_set()
        self.game_menu_window.focus_force()
        self.game_menu_window.lift()

        container = tk.Frame(self.game_menu_window, bg="#271b2f")
        container.pack(expand=True, fill="both")

        inner_frame = tk.Frame(container, bg="#271b2f")
        inner_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            inner_frame,
            text="Что вы хотите сделать?",
            fg="white",
            bg="#271b2f",
            font=("Arial", 18, "bold")
        ).pack(pady=(0, 10))

        # Создаем кнопки с правильными обработчиками
        buttons = [
            ("Присоединиться к игре", self.handle_join_game),
            ("Создать новую игру", self.handle_create_game),
            ("Одиночная игра", self.handle_single_player)
        ]
        
        for text, command in buttons:
            btn = self.create_button(inner_frame, text, command)
            btn.pack(pady=5)

        self.game_menu_window.protocol("WM_DELETE_WINDOW", self.close_game_menu)




    def close_game_menu(self):
        """Закрывает меню игры с проверкой существования"""
        if hasattr(self, 'game_menu_window') and self.game_menu_window.winfo_exists():
            self.game_menu_window.destroy()



    def handle_create_game(self):
        """Обработчик создания игры с правильным закрытием окон"""
        self.close_game_menu()  # Сначала закрываем меню
        self.create_game()      # Затем открываем окно создания игры

    def handle_join_game(self):
        """Обработчик присоединения к игре"""
        self.close_game_menu()
        self.join_game()

    def handle_single_player(self):
        """Обработчик одиночной игры"""
        self.close_game_menu()
        self.start_game_with_bot()

    def close_game_menu(self):
        """Безопасное закрытие меню игры"""
        if hasattr(self, 'game_menu_window') and self.game_menu_window.winfo_exists():
            self.game_menu_window.destroy()


    def join_game(self, room_name=None, password=None):
        try:
            with self.user_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM register.players
                    WHERE game_id = (
                        SELECT game_id FROM register.games 
                        WHERE room_name = :room_name
                    ) AND player_username = :username
                """, {'room_name': room_name, 'username': self.current_user})
                
                if cursor.fetchone()[0] > 0:
                    messagebox.showwarning("Ошибка", "Вы уже находитесь в этой игре!")
                    return
        except Exception as e:
            self.show_clean_error("Не удалось присоединиться", e)
            return

        if not self.user_connection:
            messagebox.showerror("Ошибка", "Нет подключения от имени пользователя.")
            return

        if room_name is None:
            self.show_game_selection_window()
            return

        try:
            with self.user_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT game_id, initial_word, max_players, password_hash 
                    FROM register.games 
                    WHERE room_name = :room_name AND status = 'waiting'
                """, {"room_name": room_name})
                game_info = cursor.fetchone()
                
                if not game_info:
                    messagebox.showerror("Ошибка", "Игра не найдена или уже началась.")
                    return
                    
                game_id, initial_word, max_players, stored_password = game_info

                if stored_password and password != stored_password:
                    messagebox.showerror("Ошибка", "Неверный пароль.")
                    return

                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM register.players 
                    WHERE game_id = :game_id
                """, {"game_id": game_id})
                current_players = cursor.fetchone()[0]
                
                if current_players >= max_players:
                    messagebox.showerror("Ошибка", "В игре нет свободных мест.")
                    return
                
                cursor.execute("""
                    INSERT INTO register.players (game_id, player_username, status, move_order)
                    VALUES (:game_id, :username, 'waiting', :move_order)
                """, {
                    "game_id": game_id,
                    "username": self.current_user,
                    "move_order": current_players + 1
                })

                self.user_connection.commit()
                messagebox.showinfo("Успех", f"Вы успешно присоединились к игре: {room_name}")
                self.show_waiting_room(game_id, room_name, max_players)

        except oracledb.DatabaseError as e:
            self.show_clean_error("Ошибка базы данных", e)
        except Exception as e:
            self.show_clean_error("Ошибка", e)


    def show_game_selection_window(self):
        join_window = tk.Toplevel(self.root)
        join_window.title("Присоединиться к игре")
        join_window.geometry("600x500")
        join_window.configure(bg="#271b2f")
        join_window.transient(self.root)
        join_window.grab_set()

        container = tk.Frame(join_window, bg="#271b2f")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(container, text="Поиск по названию:", font=("Arial", 12), bg="#271b2f", fg="white").pack(anchor="w")
        search_entry = tk.Entry(container, font=("Arial", 12))
        search_entry.pack(fill="x", pady=(0, 10))

        game_listbox = tk.Listbox(container, font=("Arial", 12), height=15, width=70)
        game_listbox.pack(pady=(0, 10))

        def update_game_list():
            filter_text = search_entry.get().strip()
            game_listbox.delete(0, tk.END)
            try:
                with self.user_connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT room_name, current_players, max_players, turn_time_minutes, password_hash
                        FROM register.games
                        WHERE status = 'waiting'
                        AND (room_name LIKE :filter OR :filter IS NULL)
                    """, {"filter": f"%{filter_text}%" if filter_text else None})

                    games = cursor.fetchall()
                    for room, current, max_, time, password_hash in games:
                        display = f"{room} — {current}/{max_} игроков, {time} мин. на ход"
                        game_listbox.insert(tk.END, (display, room, password_hash))
            except Exception as e:
                self.show_clean_error("Не удалось загрузить список игр", e)

        def on_search(*_):
            update_game_list()

        search_entry.bind("<KeyRelease>", on_search)
        update_game_list()

        def on_double_click(event):
            selected_game = game_listbox.curselection()
            if selected_game:
                game_info = game_listbox.get(selected_game[0])
                display, room_name, password_hash = game_info
                join_window.destroy()

                if not password_hash:
                    self.join_game(room_name)
                else:
                    self.prompt_for_password(room_name)

        game_listbox.bind("<Double-1>", on_double_click)


    def prompt_for_password(self, room_name):
        password_window = tk.Toplevel(self.root)
        password_window.title("Введите пароль")
        password_window.geometry("300x150")
        password_window.configure(bg="#271b2f")

        tk.Label(password_window, text="Введите пароль:", font=("Arial", 12), bg="#271b2f", fg="white").pack(anchor="w")
        password_entry = tk.Entry(password_window, font=("Arial", 12), show="*")
        password_entry.pack(fill="x", pady=(0, 10))

        def submit_password():
            password = password_entry.get()
            password_window.destroy()
            try:
                self.join_game(room_name, password)
            except Exception as e:
                self.show_clean_error("Ошибка при вводе пароля", e)

        submit_btn = tk.Button(password_window, text="Подтвердить", font=("Arial", 12), bg="#3498db", fg="white", command=submit_password)
        submit_btn.pack(pady=(10, 0))


    def show_clean_error(self, title, exception):
        try:
            error_obj, = exception.args
            raw_message = getattr(error_obj, "message", str(exception))
        except Exception:
            raw_message = str(exception)

        raw_message = re.sub(r"ORA-\d+:\s*", "", raw_message)

        cleaned_lines = [
            line for line in raw_message.splitlines()
            if "line" not in line.lower() and not line.strip().startswith("на \"")
        ]

        error_message = "\n".join(cleaned_lines).strip()
        messagebox.showerror(title, error_message or "Произошла неизвестная ошибка.")


    def create_game(self):
        """Создание новой игровой комнаты"""
        if hasattr(self, 'create_game_window') and self.create_game_window.winfo_exists():
            self.create_game_window.lift()
            return

        if not self.user_connection:
            messagebox.showerror("Ошибка", "Нет подключения от имени пользователя.")
            return

        try:
            self.create_game_window = tk.Toplevel(self.root)
            self.create_game_window.title("Создание игры")
            self.create_game_window.geometry("400x450")
            self.create_game_window.configure(bg="#271b2f")
            self.create_game_window.transient(self.root)
            self.create_game_window.grab_set()
            self.create_game_window.protocol("WM_DELETE_WINDOW", self.close_create_game_window)

            container = tk.Frame(self.create_game_window, bg="#271b2f")
            container.pack(expand=True, fill="both", padx=20, pady=20)

            # Название комнаты
            tk.Label(container, text="Название комнаты:", fg="white", bg="#271b2f", font=("Arial", 12)).pack(anchor="w")
            room_name_entry = tk.Entry(container, font=("Arial", 12))
            room_name_entry.pack(fill="x", pady=(0, 10))

            # Кол-во игроков
            tk.Label(container, text="Количество игроков (2-4):", fg="white", bg="#271b2f", font=("Arial", 12)).pack(anchor="w")
            player_count_spinbox = tk.Spinbox(container, from_=2, to=4, font=("Arial", 12), width=5)
            player_count_spinbox.pack(pady=(0, 10), fill="x")

            # Время на ход
            tk.Label(container, text="Время на ход (1-5 мин):", fg="white", bg="#271b2f", font=("Arial", 12)).pack(anchor="w")
            turn_time_spinbox = tk.Spinbox(container, from_=1, to=5, font=("Arial", 12), width=5)
            turn_time_spinbox.pack(pady=(0, 10), fill="x")

            # Пароль (опционально)
            use_password_var = tk.BooleanVar(value=False)
            password_entry = tk.Entry(container, font=("Arial", 12), show="*")

            def toggle_password():
                if use_password_var.get():
                    password_entry.pack(pady=(0, 10), fill="x", before=create_btn)
                else:
                    password_entry.pack_forget()

            tk.Checkbutton(
                container,
                text="Использовать пароль",
                variable=use_password_var,
                command=toggle_password,
                bg="#271b2f", fg="white",
                font=("Arial", 12),
                selectcolor="#271b2f",
                activebackground="#271b2f",
                activeforeground="white"
            ).pack(anchor="w", pady=(10, 0))

            # Кнопка создания
            def submit_create_game():
                room_name = room_name_entry.get().strip()
                player_count = int(player_count_spinbox.get())
                turn_time = int(turn_time_spinbox.get())
                password = password_entry.get().strip() if use_password_var.get() else None

                if not room_name:
                    messagebox.showerror("Ошибка", "Название комнаты не может быть пустым.")
                    return

                try:
                    with self.user_connection.cursor() as cursor:
                        result_var = cursor.var(int)
                        cursor.callproc("REGISTER.CREATE_GAME", [
                            self.current_user, room_name,
                            player_count, password,
                            turn_time, 0, result_var
                        ])

                        result = result_var.getvalue()
                        if result == 0:
                            messagebox.showerror("Ошибка", "Игра с таким названием уже существует")
                            return
                        elif result == -1:
                            raise Exception("Неизвестная ошибка при создании игры")

                        cursor.execute("""
                            SELECT game_id FROM register.games 
                            WHERE room_name = :room_name
                        """, {'room_name': room_name})
                        game_id = cursor.fetchone()[0]

                        messagebox.showinfo("Успех", "Игра успешно создана!")
                        self.close_create_game_window()
                        self.show_waiting_room(game_id, room_name, player_count)

                except oracledb.DatabaseError as e:
                    error_obj, = e.args
                    messagebox.showerror("Ошибка", f"Ошибка базы данных: {error_obj.message}")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось создать игру: {str(e)}")

            create_btn = tk.Button(
                container,
                text="Создать игру",
                command=submit_create_game,
                font=("Arial", 12),
                bg="#3498db",
                fg="white",
                activebackground="#2980b9",
                activeforeground="white"
            )
            create_btn.pack(pady=(20, 10))

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при создании окна: {str(e)}")


    def close_create_game_window(self):
        """Безопасно закрывает окно создания игры"""
        if hasattr(self, 'create_game_window') and self.create_game_window.winfo_exists():
            self.create_game_window.destroy()
        self.create_game_window = None


    def show_waiting_room(self, game_id, room_name, max_players):
        """Окно ожидания игроков"""
        self.waiting_window = tk.Toplevel(self.root)
        self.waiting_window.title(f"Комната: {room_name}")
        self.waiting_window.geometry("500x400")
        self.waiting_window.configure(bg="#271b2f")
        self.waiting_window.resizable(False, False)

        def complete_exit():
            try:
                with self.user_connection.cursor() as cursor:
                    cursor.execute("""
                        DELETE FROM register.players 
                        WHERE game_id = :game_id AND player_username = :username
                    """, {'game_id': game_id, 'username': self.current_user})

                    cursor.execute("""
                        SELECT COUNT(*) FROM register.players 
                        WHERE game_id = :game_id
                    """, {'game_id': game_id})
                    if cursor.fetchone()[0] == 0:
                        cursor.execute("""
                            DELETE FROM register.games 
                            WHERE game_id = :game_id AND status = 'waiting'
                        """, {'game_id': game_id})

                    self.user_connection.commit()
            except Exception as e:
                print(f"Ошибка при выходе из комнаты: {e}")
            finally:
                self.waiting_window.destroy()

        def on_closing():
            if messagebox.askokcancel("Подтверждение", "Вы действительно хотите покинуть комнату?"):
                complete_exit()

        self.waiting_window.protocol("WM_DELETE_WINDOW", on_closing)

        container = tk.Frame(self.waiting_window, bg="#271b2f")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        # Заголовок
        header = tk.Frame(container, bg="#271b2f")
        header.pack(fill="x", pady=(0, 15))
        tk.Label(header, text=f"Комната: {room_name}", fg="#f39c12", bg="#271b2f", font=("Arial", 14, "bold")).pack()

        # Список игроков
        players_frame = tk.Frame(container, bg="#271b2f")
        players_frame.pack(fill="x", pady=(0, 20))

        players_label = tk.Label(players_frame, text="Игроки (0/0):", fg="white", bg="#271b2f", font=("Arial", 12))
        players_label.pack(anchor="w")

        players_listbox = tk.Listbox(players_frame, font=("Arial", 12), height=5, width=40, bg="#3d3242", fg="white", selectbackground="#f39c12")
        players_listbox.pack(fill="x", pady=(5, 0))

        # Кнопки
        buttons = tk.Frame(container, bg="#271b2f")
        buttons.pack(fill="x", pady=(10, 0))

        start_btn = tk.Button(buttons, text="Начать игру", font=("Arial", 12), bg="#3498db", fg="white", state="disabled", command=lambda: self.start_game(game_id))
        leave_btn = tk.Button(buttons, text="Покинуть комнату", font=("Arial", 12), bg="#e74c3c", fg="white", command=on_closing)
        leave_btn.pack(side="right", fill="x", expand=True)

        is_owner = self.is_room_owner(game_id, self.current_user)
        if is_owner:
            start_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)

        def update_players_list():
            try:
                players = self.get_players_in_room(game_id)
                players_listbox.delete(0, tk.END)
                for p in players:
                    players_listbox.insert(tk.END, p)

                players_label.config(text=f"Игроки ({len(players)}/{max_players}):")
                if is_owner:
                    start_btn.config(state="normal" if len(players) >= max_players else "disabled")
                else:
                    self.check_game_status(game_id)

            except Exception as e:
                print(f"Ошибка обновления списка: {e}")
            finally:
                if hasattr(self, 'waiting_window') and self.waiting_window.winfo_exists():
                    self.waiting_window.after(2000, update_players_list)

        update_players_list()


    def get_players_in_room(self, game_id):
        with self.user_connection.cursor() as cursor:
            cursor.execute("""
                SELECT player_username FROM register.players 
                WHERE game_id = :game_id ORDER BY move_order
            """, {'game_id': game_id})
            return [row[0] for row in cursor.fetchall()]


    def is_room_owner(self, game_id, username):
        with self.user_connection.cursor() as cursor:
            cursor.execute("""
                SELECT owner_username FROM register.games 
                WHERE game_id = :game_id
            """, {'game_id': game_id})
            result = cursor.fetchone()
            return result and result[0] == username


    def leave_game(self, window, game_id):
        with self.user_connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM register.players 
                WHERE game_id = :game_id AND player_username = :username
            """, {'game_id': game_id, 'username': self.current_user})
            cursor.execute("""
                SELECT COUNT(*) FROM register.players 
                WHERE game_id = :game_id
            """, {'game_id': game_id})
            players_left = cursor.fetchone()[0]
            if players_left == 0:
                cursor.execute("""
                    DELETE FROM register.games 
                    WHERE game_id = :game_id
                """, {'game_id': game_id})
            self.user_connection.commit()
            window.destroy()


    def start_game(self, game_id):
        with self.user_connection.cursor() as cursor:
            cursor.execute("""
                SELECT owner_username, max_players, turn_time_minutes,
                    (SELECT COUNT(*) FROM register.players WHERE game_id = :game_id) as player_count
                FROM register.games 
                WHERE game_id = :game_id AND status = 'waiting'
            """, {'game_id': game_id})
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Ошибка", "Игра не найдена или уже началась!")
                return
            owner, max_players, turn_time, player_count = result
            if player_count < max_players:
                messagebox.showerror("Ошибка", f"Недостаточно игроков! Нужно {max_players}, есть {player_count}")
                return
            cursor.execute("""
                SELECT word FROM register.big_words 
                WHERE LENGTH(word) BETWEEN 12 AND 15
                ORDER BY DBMS_RANDOM.VALUE 
                FETCH FIRST 1 ROWS ONLY
            """)
            word_result = cursor.fetchone()
            if not word_result:
                messagebox.showerror("Ошибка", "Не удалось выбрать начальное слово!")
                return
            initial_word = word_result[0]
            cursor.execute("""
                SELECT player_username FROM register.players
                WHERE game_id = :game_id
                ORDER BY DBMS_RANDOM.VALUE
                FETCH FIRST 1 ROWS ONLY
            """, {'game_id': game_id})
            first_player = cursor.fetchone()[0]
            cursor.execute("""
                UPDATE register.games 
                SET status = 'in_progress',
                    initial_word = :word,
                    current_player = :first_player,
                    start_time = CURRENT_TIMESTAMP,
                    turn_end_time = CURRENT_TIMESTAMP + (:turn_time * INTERVAL '1' MINUTE)
                WHERE game_id = :game_id
            """, {
                'word': initial_word,
                'first_player': first_player,
                'game_id': game_id,
                'turn_time': turn_time
            })
            cursor.execute("""
                DELETE FROM register.game_notifications 
                WHERE game_id = :game_id
            """, {'game_id': game_id})
            cursor.execute("""
                INSERT INTO register.game_notifications (game_id, player_username)
                SELECT :game_id, player_username
                FROM register.players
                WHERE game_id = :game_id
            """, {'game_id': game_id})
            cursor.execute("""
                DELETE FROM register.player_states 
                WHERE game_id = :game_id
            """, {'game_id': game_id})
            cursor.execute("""
                INSERT INTO register.player_states (game_id, player_username, score)
                SELECT :game_id, player_username, 0
                FROM register.players
                WHERE game_id = :game_id
            """, {'game_id': game_id})
            self.user_connection.commit()
            self.close_waiting_window()
            self.show_game_field(game_id, initial_word, first_player, turn_time)
            print(f"Игра {game_id} начата. Первое слово: {initial_word}, первый игрок: {first_player}")


    def submit_word(self, game_id, initial_word):
        word = self.word_entry.get().strip().lower()
        self.word_entry.delete(0, tk.END)
        
        if not word:
            messagebox.showwarning("Ошибка", "Введите слово!")
            return
            
        if not self.can_form_word(initial_word, word):
            messagebox.showwarning("Ошибка", "Нельзя составить это слово из букв исходного!")
            return
            
        with self.user_connection.cursor() as cursor:
            try:
                # Проверяем существование слова в словаре
                cursor.execute("SELECT COUNT(*) FROM register.small_words WHERE word = :word", {'word': word})
                if cursor.fetchone()[0] == 0:
                    messagebox.showwarning("Ошибка", "Такого слова нет в словаре!")
                    return
                    
                # Проверяем, не использовалось ли слово ранее
                cursor.execute("""
                    SELECT COUNT(*) FROM register.game_moves
                    WHERE game_id = :game_id AND word = :word
                """, {'game_id': game_id, 'word': word})
                if cursor.fetchone()[0] > 0:
                    messagebox.showwarning("Ошибка", "Это слово уже использовалось в игре!")
                    return
                
                # Вызываем процедуру для добавления слова и передачи хода
                cursor.callproc("register.submit_word_and_pass_turn", [
                    game_id, 
                    self.current_user, 
                    word
                ])
                
                self.user_connection.commit()
                messagebox.showinfo("Успех", f"Слово '{word}' принято! Ход передан следующему игроку.")
                
                # Обновляем интерфейс
                self.update_game_data()
                
                # Проверяем, если это игра с ботом и следующий ход бота
                cursor.execute("""
                    SELECT is_single_player, current_player 
                    FROM register.games 
                    WHERE game_id = :game_id
                """, {'game_id': game_id})
                
                result = cursor.fetchone()
                if result and result[0] == 1 and result[1].startswith('BOT_'):
                    # Получаем сложность бота из имени
                    bot_difficulty = result[1].split('_')[1].lower()
                    
                    # Получаем начальное слово
                    cursor.execute("""
                        SELECT initial_word FROM register.games 
                        WHERE game_id = :game_id
                    """, {'game_id': game_id})
                    initial_word = cursor.fetchone()[0]
                    
                    # Запускаем ход бота с небольшой задержкой
                    self.root.after(1500, 
                        lambda: self._bot_make_move(game_id, initial_word, bot_difficulty))
                    
            except oracledb.DatabaseError as e:
                error_obj, = e.args
                messagebox.showerror("Ошибка", f"Ошибка базы данных: {error_obj.message}")
                self.user_connection.rollback()


    def notify_players(self, game_id):
        with self.user_connection.cursor() as cursor:
            cursor.execute("""
                UPDATE register.game_notifications
                SET notification_time = CURRENT_TIMESTAMP
                WHERE game_id = :game_id
            """, {'game_id': game_id})
            self.user_connection.commit()


    def end_game(self, game_id):
        if hasattr(self, '_game_ended') and self._game_ended:
            return
        self._game_ended = True
        
        with self.user_connection.cursor() as cursor:
            # Проверяем, является ли это игрой с ботом
            cursor.execute("""
                SELECT is_single_player FROM register.games 
                WHERE game_id = :game_id
            """, {'game_id': game_id})
            
            is_single_player = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT ps.player_username, ps.score, 
                    RANK() OVER (ORDER BY ps.score DESC) as rank
                FROM register.player_states ps
                WHERE ps.game_id = :game_id
                ORDER BY ps.score DESC
            """, {'game_id': game_id})
            
            players = cursor.fetchall()
            winner = None
            max_score = -1
            draw = False
            
            if players:
                max_score = players[0][1]
                # Фильтруем только реальных игроков (не ботов) для определения победителя
                real_players = [p for p in players if not p[0].startswith('BOT_')]
                if real_players:
                    max_real_score = real_players[0][1]
                    winners = [p[0] for p in real_players if p[1] == max_real_score]
                    winner = ", ".join(winners) if len(winners) > 1 else winners[0]
                    draw = len(winners) > 1
            
            # Обновляем рейтинг ТОЛЬКО для реальных игроков и ТОЛЬКО если это не одиночная игра
            if not is_single_player:
                for player in players:
                    if not player[0].startswith('BOT_') and player[1] == max_score:
                        cursor.execute("""
                            MERGE INTO register.leaderboard l
                            USING (
                                SELECT :username AS username, :score AS score FROM dual
                            ) s
                            ON (l.username = s.username)
                            WHEN MATCHED THEN
                                UPDATE SET l.score = l.score + s.score
                            WHEN NOT MATCHED THEN
                                INSERT (username, score)
                                VALUES (s.username, s.score)
                        """, {
                            'username': player[0],
                            'score': player[1]
                        })
            
            cursor.execute("""
                UPDATE register.games
                SET status = 'finished',
                    end_time = CURRENT_TIMESTAMP,
                    winner = :winner,
                    need_end_game = 0
                WHERE game_id = :game_id
            """, {
                'game_id': game_id,
                'winner': winner if winner else 'Не определен'
            })
            
            self.user_connection.commit()
            
            # ОБНОВЛЯЕМ ИНТЕРФЕЙС ПОСЛЕ ОКОНЧАНИЯ ИГРЫ
            if hasattr(self, 'user_label') and self.user_label:
                self.update_user_score_display()
            
            # Формируем сообщение о результате
            if is_single_player:
                # Для одиночной игры показываем специальное сообщение
                user_score = next((p[1] for p in players if p[0] == self.current_user), 0)
                bot_score = next((p[1] for p in players if p[0].startswith('BOT_')), 0)
                
                if user_score > bot_score:
                    message = f"Поздравляем! Вы победили бота со счетом {user_score}:{bot_score}!"
                elif user_score < bot_score:
                    message = f"Бот победил со счетом {bot_score}:{user_score}. Попробуйте еще раз!"
                else:
                    message = f"Ничья! Счет {user_score}:{bot_score}. Интересная игра!"
            else:
                # Для многопользовательской игры
                if draw:
                    message = f"Ничья! Победители: {winner} с {max_score} очками!"
                elif winner:
                    message = f"Победитель: {winner} с {max_score} очками!"
                else:
                    message = "Игра завершена. Нет победителя."
            
            messagebox.showinfo("Игра завершена", message)
            
            if hasattr(self, 'game_window') and self.game_window.winfo_exists():
                self.game_window.destroy()

    def _get_player_score(self, players, username):
        """Получить счет конкретного игрока из списка"""
        for player in players:
            if player[0] == username:
                return player[1]
        return 0

    def update_user_score_display(self):
        """Обновляет отображение счета пользователя в главном окне"""
        if not self.current_user:
            return
            
        register_connection = get_db_connection()
        with register_connection.cursor() as cursor:
            cursor.execute("SELECT score FROM REGISTER.leaderboard WHERE username = :username", {"username": self.current_user})
            score = cursor.fetchone()
            if score:
                score_text = f" — Очки: {score[0]}"
            else:
                score_text = " — Очки: 0"
        register_connection.close()

        if hasattr(self, 'user_label') and self.user_label:
            self.user_label.config(text=f"👤 {self.current_user}{score_text}")


    def on_game_window_close(self):
        if messagebox.askokcancel("Выход из игры", "Вы действительно хотите выйти из текущей игры? Ваш прогресс может быть потерян."):
            if hasattr(self, 'timer_id'):
                self.root.after_cancel(self.timer_id)
            if hasattr(self, 'update_id'):
                self.root.after_cancel(self.update_id)
            
            # Обновляем счет после закрытия игрового окна
            if hasattr(self, 'current_user') and self.current_user:
                self.update_user_score_display()
                
            self.game_window.destroy()
            self.current_game = None
            self.root.deiconify()


    def show_game_field(self, game_id, initial_word, current_player, turn_time_minutes):
        self.game_window = tk.Toplevel(self.root)
        self.game_window.title(f"Игра - {initial_word}")
        self.game_window.geometry("1200x800")
        self.game_window.configure(bg="#271b2f")
        self.current_game = {
            'game_id': game_id,
            'initial_word': initial_word,
            'current_player': current_player,
            'time_left': turn_time_minutes * 60,
            'turn_time_minutes': turn_time_minutes
        }
        
        word_frame = tk.Frame(self.game_window, bg="#271b2f")
        word_frame.pack(pady=20)
        tk.Label(word_frame, text="Составьте слова из:", font=("Arial", 14), fg="white", bg="#271b2f").pack(side="left")
        tk.Label(word_frame, text=initial_word, font=("Arial", 16, "bold"), fg="#f39c12", bg="#271b2f").pack(side="left", padx=10)
        
        turn_frame = tk.Frame(self.game_window, bg="#271b2f")
        turn_frame.pack(pady=10)
        self.turn_label = tk.Label(turn_frame, text=f"Сейчас ходит: {current_player} (время на ход: {turn_time_minutes} мин)", font=("Arial", 14), fg="white", bg="#271b2f")
        self.turn_label.pack()
        
        timer_frame = tk.Frame(self.game_window, bg="#271b2f")
        timer_frame.pack(pady=10)
        self.timer_label = tk.Label(timer_frame, text=f"{turn_time_minutes:02d}:00", font=("Arial", 14), fg="white", bg="#271b2f")
        self.timer_label.pack()
        self.update_timer()
        
        self.input_frame = tk.Frame(self.game_window, bg="#271b2f")
        self.input_frame.pack(pady=20)
        tk.Label(self.input_frame, text="Ваше слово:", font=("Arial", 12), fg="white", bg="#271b2f").pack()
        self.word_entry = tk.Entry(self.input_frame, font=("Arial", 14))
        self.word_entry.pack()
        self.word_submit_btn = tk.Button(
            self.input_frame, 
            text="Отправить слово",
            font=("Arial", 12),
            bg="#3498db",
            fg="white",
            command=lambda: self.submit_word(
                self.current_game['game_id'],
                self.current_game['initial_word']
            )
        )
        self.word_submit_btn.pack(pady=10)
        self.word_entry.bind("<Return>", lambda e: self.submit_word(self.current_game['game_id'], self.current_game['initial_word']))
        self.update_input_state()
        
        # История ходов с скроллбаром
        moves_frame = tk.Frame(self.game_window, bg="#271b2f")
        moves_frame.pack(pady=10, fill="both", padx=20, expand=True)
        
        tk.Label(moves_frame, text="История ходов:", font=("Arial", 12), fg="white", bg="#271b2f").pack(anchor="w")
        
        moves_container = tk.Frame(moves_frame, bg="#271b2f")
        moves_container.pack(fill="both", expand=True)
        
        self.moves_listbox = tk.Listbox(moves_container, font=("Arial", 11), bg="#3d3242", fg="white", selectbackground="#f39c12")
        moves_scrollbar = tk.Scrollbar(moves_container, orient="vertical", command=self.moves_listbox.yview)
        self.moves_listbox.configure(yscrollcommand=moves_scrollbar.set)
        
        self.moves_listbox.pack(side="left", fill="both", expand=True)
        moves_scrollbar.pack(side="right", fill="y")
        
        # Рейтинг игроков с скроллбаром
        scores_frame = tk.Frame(self.game_window, bg="#271b2f")
        scores_frame.pack(pady=10, fill="both", padx=20, expand=True)
        
        tk.Label(scores_frame, text="Рейтинг игроков:", font=("Arial", 12), fg="white", bg="#271b2f").pack(anchor="w")
        
        scores_container = tk.Frame(scores_frame, bg="#271b2f")
        scores_container.pack(fill="both", expand=True)
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Game.Treeview", background="#3d3242", foreground="white", fieldbackground="#3d3242", font=("Arial", 10))
        style.configure("Game.Treeview.Heading", background="#3498db", foreground="white", font=("Arial", 11, "bold"))
        
        self.scores_tree = ttk.Treeview(scores_container, style="Game.Treeview", columns=("player", "score"), show="headings", height=4)
        scores_scrollbar = tk.Scrollbar(scores_container, orient="vertical", command=self.scores_tree.yview)
        self.scores_tree.configure(yscrollcommand=scores_scrollbar.set)
        
        self.scores_tree.heading("player", text="Игрок", anchor="w")
        self.scores_tree.heading("score", text="Очки", anchor="center")
        self.scores_tree.column("player", width=200)
        self.scores_tree.column("score", width=100)
        
        self.scores_tree.pack(side="left", fill="both", expand=True)
        scores_scrollbar.pack(side="right", fill="y")
        
        self.update_game_data()
        self.periodic_update()
        self.game_window.protocol("WM_DELETE_WINDOW", self.on_game_window_close)

    def update_timer(self):
        if not hasattr(self, 'game_window') or not self.game_window.winfo_exists():
            return
        try:
            with self.user_connection.cursor() as cursor:
                cursor.execute("""SELECT status, need_end_game FROM register.games WHERE game_id = :game_id""", {'game_id': self.current_game['game_id']})
                result = cursor.fetchone()
                if result:
                    status, need_end = result
                    if status == 'finished' or need_end == 1:
                        self.end_game(self.current_game['game_id'])
                        return
                    cursor.execute("""
                        SELECT 
                            EXTRACT(DAY FROM (turn_end_time - CURRENT_TIMESTAMP)) * 86400 +
                            EXTRACT(HOUR FROM (turn_end_time - CURRENT_TIMESTAMP)) * 3600 +
                            EXTRACT(MINUTE FROM (turn_end_time - CURRENT_TIMESTAMP)) * 60 +
                            EXTRACT(SECOND FROM (turn_end_time - CURRENT_TIMESTAMP))
                        FROM register.games
                        WHERE game_id = :game_id
                    """, {'game_id': self.current_game['game_id']})
                    result = cursor.fetchone()
                    # ЗАЩИТА ОТ None
                    if result and result[0] is not None:
                        time_left = int(result[0])
                    else:
                        time_left = self.current_game['time_left']  # Используем текущее значение
                    
                    time_left = max(0, time_left)
                    if time_left > 0:
                        mins, secs = divmod(time_left, 60)
                        self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
                        self.game_window.after(1000, self.update_timer)
                    else:
                        cursor.execute("""BEGIN register.game_timer_pkg.check_turn_time(:game_id); END;""", {'game_id': self.current_game['game_id']})
                        self.user_connection.commit()
                        self.game_window.after(1000, self.update_timer)
        except Exception as e:
            print(f"Ошибка в update_timer: {e}")

    def update_input_state(self):
        if not hasattr(self, 'current_game') or not self.current_game:
            return
        if self.current_game['current_player'] == self.current_user:
            self.word_entry.config(state="normal")
            self.word_submit_btn.config(state="normal")
        else:
            self.word_entry.config(state="disabled")
            self.word_submit_btn.config(state="disabled")

    def start_game_with_bot(self):
        """Запуск одиночной игры с выбором сложности"""
        if not self.user_connection:
            messagebox.showerror("Ошибка", "Нет подключения к базе данных")
            return

        # Окно выбора сложности
        difficulty_window = tk.Toplevel(self.root)
        difficulty_window.title("Выбор сложности")
        difficulty_window.geometry("400x300")
        difficulty_window.configure(bg="#271b2f")
        difficulty_window.transient(self.root)
        difficulty_window.grab_set()

        container = tk.Frame(difficulty_window, bg="#271b2f")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(
            container, 
            text="Выберите уровень сложности:",
            fg="white", bg="#271b2f", font=("Arial", 14, "bold")
        ).pack(pady=(0, 20))

        difficulties = [
            ("Легкий", "easy", "Бот делает простые слова"),
            ("Средний", "medium", "Бот составляет слова средней сложности"),
            ("Сложный", "hard", "Бот составляет сложные слова"),
            ("Невозможный", "impossible", "Бот всегда находит самые длинные слова")
        ]

        selected_difficulty = tk.StringVar(value="medium")

        for text, value, description in difficulties:
            frame = tk.Frame(container, bg="#271b2f")
            frame.pack(fill="x", pady=5)
            
            tk.Radiobutton(
                frame, text=text, variable=selected_difficulty,
                value=value, bg="#271b2f", fg="white",
                selectcolor="#271b2f", font=("Arial", 12),
                activebackground="#271b2f", activeforeground="white"
            ).pack(side="left")
            
            tk.Label(
                frame, text=description, 
                fg="#bdc3c7", bg="#271b2f", font=("Arial", 9)
            ).pack(side="left", padx=(10, 0))

        def start_bot_game():
            difficulty = selected_difficulty.get()
            difficulty_window.destroy()
            self._create_bot_game(difficulty)

        tk.Button(
            container, text="Начать игру", 
            command=start_bot_game,
            font=("Arial", 12), bg="#3498db", fg="white"
        ).pack(pady=(20, 0))

    def _create_bot_game(self, difficulty):
        """Создание игры с ботом"""
        try:
            print(f"[DEBUG] Начало создания игры с ботом. Пользователь: {self.current_user}, Сложность: {difficulty}")
            
            with self.user_connection.cursor() as cursor:
                result_var = cursor.var(int)
                print(f"[DEBUG] Создан result_var: {result_var}")
                
                # Вызываем процедуру
                print("[DEBUG] Вызываем register.create_single_player_game...")
                cursor.callproc("register.create_single_player_game", [
                    self.current_user, difficulty, result_var
                ])
                print("[DEBUG] Процедура вызвана успешно")
                cursor.callproc("dbms_output.enable")
                # Проверяем, что результат не None
                game_id = result_var.getvalue()
                print(f"[DEBUG] result_var.getvalue() = {game_id} (тип: {type(game_id)})")
                
                if game_id is None:
                    raise Exception("Процедура не вернула значение game_id")
                
                if game_id == -1:
                    raise Exception("Не удалось создать игру с ботом")
                
                print(f"[DEBUG] Игра создана с ID: {game_id}")
                
                # Получаем информацию об игре
                print(f"[DEBUG] Запрашиваем информацию об игре {game_id}...")
                cursor.execute("""
                    SELECT initial_word, turn_time_minutes, current_player
                    FROM register.games 
                    WHERE game_id = :game_id
                """, {'game_id': game_id})
                
                result = cursor.fetchone()
                print(f"[DEBUG] Результат запроса: {result}")
                
                if result is None:
                    raise Exception("Игра не найдена после создания")
                    
                initial_word, turn_time, current_player = result
                print(f"[DEBUG] initial_word: {initial_word}, turn_time: {turn_time}, current_player: {current_player}")
                
                # Проверяем, что current_player не None
                if current_player is None:
                    current_player = self.current_user
                    print(f"[DEBUG] current_player был None, установлен в: {current_player}")
                
                # Инициализируем current_game
                self.current_game = {
                    'game_id': game_id,
                    'initial_word': initial_word,
                    'current_player': current_player,
                    'time_left': turn_time * 60,
                    'turn_time_minutes': turn_time,
                    'is_bot_game': current_player.startswith('BOT_') if current_player else False
                }
                print(f"[DEBUG] current_game инициализирован: {self.current_game}")
                
                # Показываем игровое поле
                print("[DEBUG] Показываем игровое поле...")
                self.show_game_field(game_id, initial_word, current_player, turn_time)
                
                # Запускаем бота, если он должен ходить первым
                if current_player and current_player.startswith('BOT_'):
                    bot_difficulty = current_player.split('_')[1].lower()
                    print(f"[DEBUG] Запускаем ход бота со сложностью: {bot_difficulty}")
                    self.root.after(2000, lambda: self._bot_make_move(game_id, initial_word, bot_difficulty))
                else:
                    print("[DEBUG] Первый ход пользователя")
                    
            print("[DEBUG] Создание игры завершено успешно")
            
        except oracledb.DatabaseError as e:
            error_obj, = e.args
            print(f"[DEBUG] Ошибка базы данных: {error_obj.message}")
            print(f"[DEBUG] Код ошибки: {error_obj.code}")
            self.show_clean_error("Ошибка базы данных", e)
            
        except Exception as e:
            print(f"[DEBUG] Общая ошибка: {str(e)}")
            print(f"[DEBUG] Тип ошибки: {type(e).__name__}")
            import traceback
            print(f"[DEBUG] Traceback: {traceback.format_exc()}")
            self.show_clean_error("Ошибка создания игры", e)

    def _bot_make_move(self, game_id, initial_word, difficulty):
        """Ход бота"""
        try:
            print(f"[DEBUG] Ход бота. Игра: {game_id}, Слово: {initial_word}, Сложность: {difficulty}")
            
            with self.user_connection.cursor() as cursor:
                # Вызываем функцию без указания схемы
                cursor.execute("""
                    SELECT register.bot_logic_pkg.generate_bot_word(
                        :game_id, 
                        :initial_word, 
                        :difficulty
                    ) FROM dual
                """, {
                    'game_id': game_id,
                    'initial_word': initial_word,
                    'difficulty': difficulty
                })
                
                result = cursor.fetchone()
                bot_word = result[0] if result else None
                print(f"[DEBUG] Бот сгенерировал слово: {bot_word}")
                
                if bot_word:
                    # Бот делает ход
                    cursor.callproc("register.submit_word_and_pass_turn", [
                        game_id, 
                        'BOT_' + difficulty.upper(), 
                        bot_word
                    ])
                    
                    self.user_connection.commit()
                    self.update_game_data()
                    
                    # Показываем уведомление
                    if hasattr(self, 'game_window') and self.game_window.winfo_exists():
                        messagebox.showinfo("Ход бота", f"Бот составил слово: {bot_word}")
                
                else:
                    # Бот пропускает ход - правильный вызов процедуры
                    print("[DEBUG] Бот пропускает ход")
                    # Пробуем разные варианты вызова skip_turn
                    try:
                        # Вариант 1: с указанием имени игрока
                        cursor.callproc("register.skip_turn", [
                            game_id,
                            'BOT_' + difficulty.upper()
                        ])
                    except:
                        try:
                            # Вариант 2: только game_id
                            cursor.callproc("register.skip_turn", [game_id])
                        except:
                            # Вариант 3: используем другую процедуру
                            cursor.callproc("register.submit_word_and_pass_turn", [
                                game_id, 
                                'BOT_' + difficulty.upper(), 
                                None  # Пустое слово для пропуска хода
                            ])
                    
                    self.user_connection.commit()
                    self.update_game_data()
                    
            # Проверяем, не закончилась ли игра
            self._check_bot_game_status(game_id)
            
        except Exception as e:
            print(f"Ошибка хода бота: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")

    def _check_bot_game_status(self, game_id):
        """Проверка статуса игры с ботом"""
        if not hasattr(self, 'game_window') or not self.game_window.winfo_exists():
            return
        
        try:
            with self.user_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT status, current_player, need_end_game
                    FROM register.games 
                    WHERE game_id = :game_id
                """, {'game_id': game_id})
                
                status, current_player, need_end = cursor.fetchone()
                
                if status == 'finished' or need_end == 1:
                    self.end_game(game_id)
                    return
                
                # Если следующий ход бота
                if current_player.startswith('BOT_'):
                    # Получаем сложность из имени бота
                    bot_difficulty = current_player.split('_')[1].lower()
                    
                    # Вычисляем задержку
                    delay_var = cursor.var(float)
                    cursor.callproc("register.bot_logic_pkg.calculate_bot_delay", [
                        bot_difficulty, delay_var
                    ])
                    
                    delay_seconds = delay_var.getvalue() * 1000  # в миллисекундах
                    
                    # Запускаем ход бота с задержкой
                    cursor.execute("""
                        SELECT initial_word FROM register.games 
                        WHERE game_id = :game_id
                    """, {'game_id': game_id})
                    
                    initial_word = cursor.fetchone()[0]
                    
                    self.root.after(int(delay_seconds), 
                        lambda: self._bot_make_move(game_id, initial_word, bot_difficulty))
                    
        except Exception as e:
            print(f"Ошибка проверки статуса: {e}")

    def show_game_field(self, game_id, initial_word, current_player, turn_time_minutes):
        self.game_window = tk.Toplevel(self.root)
        self.game_window.title(f"Игра - {initial_word}")
        self.game_window.geometry("1200x800")
        self.game_window.configure(bg="#271b2f")
        
        # Инициализируем current_game с флагом бот-игры
        self.current_game = {
            'game_id': game_id,
            'initial_word': initial_word,
            'current_player': current_player,
            'time_left': turn_time_minutes * 60,
            'turn_time_minutes': turn_time_minutes,
            'is_bot_game': current_player.startswith('BOT_')  # Добавляем определение типа игры
        }
        
        word_frame = tk.Frame(self.game_window, bg="#271b2f")
        word_frame.pack(pady=20)
        tk.Label(word_frame, text="Составьте слова из:", font=("Arial", 14), fg="white", bg="#271b2f").pack(side="left")
        tk.Label(word_frame, text=initial_word, font=("Arial", 16, "bold"), fg="#f39c12", bg="#271b2f").pack(side="left", padx=10)
        
        turn_frame = tk.Frame(self.game_window, bg="#271b2f")
        turn_frame.pack(pady=10)
        self.turn_label = tk.Label(turn_frame, text=f"Сейчас ходит: {current_player} (время на ход: {turn_time_minutes} мин)", font=("Arial", 14), fg="white", bg="#271b2f")
        self.turn_label.pack()
        
        timer_frame = tk.Frame(self.game_window, bg="#271b2f")
        timer_frame.pack(pady=10)
        self.timer_label = tk.Label(timer_frame, text=f"{turn_time_minutes:02d}:00", font=("Arial", 14), fg="white", bg="#271b2f")
        self.timer_label.pack()
        self.update_timer()
        
        self.input_frame = tk.Frame(self.game_window, bg="#271b2f")
        self.input_frame.pack(pady=20)
        tk.Label(self.input_frame, text="Ваше слово:", font=("Arial", 12), fg="white", bg="#271b2f").pack()
        self.word_entry = tk.Entry(self.input_frame, font=("Arial", 14))
        self.word_entry.pack()
        
        self.word_submit_btn = tk.Button(
            self.input_frame, 
            text="Отправить слово",
            font=("Arial", 12),
            bg="#3498db",
            fg="white",
            command=lambda: self.submit_word(
                self.current_game['game_id'],
                self.current_game['initial_word']
            )
        )
        self.word_submit_btn.pack(pady=10)
        self.word_entry.bind("<Return>", lambda e: self.submit_word(self.current_game['game_id'], self.current_game['initial_word']))
        self.update_input_state()
        
        # История ходов с скроллбаром
        moves_frame = tk.Frame(self.game_window, bg="#271b2f")
        moves_frame.pack(pady=10, fill="both", padx=20, expand=True)
        
        tk.Label(moves_frame, text="История ходов:", font=("Arial", 12), fg="white", bg="#271b2f").pack(anchor="w")
        
        moves_container = tk.Frame(moves_frame, bg="#271b2f")
        moves_container.pack(fill="both", expand=True)
        
        self.moves_listbox = tk.Listbox(moves_container, font=("Arial", 11), bg="#3d3242", fg="white", selectbackground="#f39c12")
        moves_scrollbar = tk.Scrollbar(moves_container, orient="vertical", command=self.moves_listbox.yview)
        self.moves_listbox.configure(yscrollcommand=moves_scrollbar.set)
        
        self.moves_listbox.pack(side="left", fill="both", expand=True)
        moves_scrollbar.pack(side="right", fill="y")
        
        # Рейтинг игроков с скроллбаром
        scores_frame = tk.Frame(self.game_window, bg="#271b2f")
        scores_frame.pack(pady=10, fill="both", padx=20, expand=True)
        
        tk.Label(scores_frame, text="Рейтинг игроков:", font=("Arial", 12), fg="white", bg="#271b2f").pack(anchor="w")
        
        scores_container = tk.Frame(scores_frame, bg="#271b2f")
        scores_container.pack(fill="both", expand=True)
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Game.Treeview", background="#3d3242", foreground="white", fieldbackground="#3d3242", font=("Arial", 10))
        style.configure("Game.Treeview.Heading", background="#3498db", foreground="white", font=("Arial", 11, "bold"))
        
        self.scores_tree = ttk.Treeview(scores_container, style="Game.Treeview", columns=("player", "score"), show="headings", height=4)
        scores_scrollbar = tk.Scrollbar(scores_container, orient="vertical", command=self.scores_tree.yview)
        self.scores_tree.configure(yscrollcommand=scores_scrollbar.set)
        
        self.scores_tree.heading("player", text="Игрок", anchor="w")
        self.scores_tree.heading("score", text="Очки", anchor="center")
        self.scores_tree.column("player", width=200)
        self.scores_tree.column("score", width=100)
        
        self.scores_tree.pack(side="left", fill="both", expand=True)
        scores_scrollbar.pack(side="right", fill="y")
        
        self.update_game_data()
        self.periodic_update()
        self.game_window.protocol("WM_DELETE_WINDOW", self.on_game_window_close)
        
        # Если это игра с ботом и бот ходит первым, запускаем его ход
        if self.current_game['is_bot_game'] and current_player.startswith('BOT_'):
            bot_difficulty = current_player.split('_')[1].lower()
            self.root.after(2000, lambda: self._bot_make_move(game_id, initial_word, bot_difficulty))

    def check_game_status(self, game_id):
        with self.user_connection.cursor() as cursor:
            cursor.execute("""SELECT status FROM register.games WHERE game_id = :game_id""", {'game_id': game_id})
            status = cursor.fetchone()
            if not status or status[0] != 'in_progress':
                self.root.after(2000, lambda: self.check_game_status(game_id))
                return
            cursor.execute("""SELECT 1 FROM register.game_notifications WHERE game_id = :game_id AND player_username = :username""", {'game_id': game_id, 'username': self.current_user})
            if cursor.fetchone():
                cursor.execute("""DELETE FROM register.game_notifications WHERE game_id = :game_id AND player_username = :username""", {'game_id': game_id, 'username': self.current_user})
                cursor.execute("""SELECT initial_word, current_player, turn_time_minutes FROM register.games WHERE game_id = :game_id""", {'game_id': game_id})
                initial_word, current_player, turn_time = cursor.fetchone()
                if hasattr(self, 'waiting_window') and self.waiting_window.winfo_exists():
                    self.waiting_window.destroy()
                self.show_game_field(game_id, initial_word, current_player, turn_time)
            else:
                self.root.after(2000, lambda: self.check_game_status(game_id))

    def update_game_data(self):
        try:
            # Сохраняем текущие позиции скролла
            listbox_scroll = self.moves_listbox.yview() if hasattr(self, 'moves_listbox') else (0, 0)
            tree_scroll = self.scores_tree.yview() if hasattr(self, 'scores_tree') else (0, 0)
            
            with self.user_connection.cursor() as cursor:
                cursor.execute("""SELECT player_username, word, is_valid FROM register.game_moves WHERE game_id = :game_id ORDER BY move_time""", {'game_id': self.current_game['game_id']})
                
                # Получаем текущие данные для сравнения
                current_moves = list(self.moves_listbox.get(0, tk.END)) if hasattr(self, 'moves_listbox') else []
                new_moves = []
                moves_data = cursor.fetchall()
                
                for player, word, is_valid in moves_data:
                    display_text = f"{player}: {word}" if is_valid else f"{player}: [Пропуск хода]"
                    new_moves.append(display_text)
                
                # Обновляем только если данные изменились
                if current_moves != new_moves and hasattr(self, 'moves_listbox'):
                    self.moves_listbox.delete(0, tk.END)
                    for move in new_moves:
                        self.moves_listbox.insert(tk.END, move)
                    # Восстанавливаем позицию скролла
                    self.moves_listbox.yview_moveto(listbox_scroll[0])
                
                # Аналогично для Treeview
                cursor.execute("""SELECT ps.player_username, ps.score FROM register.player_states ps WHERE ps.game_id = :game_id ORDER BY ps.score DESC""", {'game_id': self.current_game['game_id']})
                
                # Получаем текущие данные Treeview
                current_scores = {}
                if hasattr(self, 'scores_tree'):
                    for item in self.scores_tree.get_children():
                        values = self.scores_tree.item(item)['values']
                        if values:
                            current_scores[values[0]] = values[1]
                
                new_scores = {}
                scores_data = cursor.fetchall()
                for player, score in scores_data:
                    new_scores[player] = score
                
                # Обновляем только если данные изменились
                if current_scores != new_scores and hasattr(self, 'scores_tree'):
                    self.scores_tree.delete(*self.scores_tree.get_children())
                    for player, score in sorted(new_scores.items(), key=lambda x: x[1], reverse=True):
                        self.scores_tree.insert("", "end", values=(player, score))
                    # Восстанавливаем позицию скролла
                    self.scores_tree.yview_moveto(tree_scroll[0])
                
                cursor.execute("""SELECT current_player, turn_time_minutes FROM register.games WHERE game_id = :game_id""", {'game_id': self.current_game['game_id']})
                result = cursor.fetchone()
                if result:
                    current_player, turn_time = result
                    if self.current_game['current_player'] != current_player:
                        self.current_game['current_player'] = current_player
                        self.current_game['turn_time_minutes'] = turn_time
                        self.turn_label.config(text=f"Сейчас ходит: {current_player} (ход {turn_time} мин)")
                        self.update_input_state()
                        
        except Exception as e:
            print(f"Ошибка в update_game_data: {e}")

    def periodic_update(self):
        if hasattr(self, 'game_window') and self.game_window.winfo_exists():
            try:
                with self.user_connection.cursor() as cursor:
                    cursor.execute("""SELECT current_player, turn_time_minutes FROM register.games WHERE game_id = :game_id""", {'game_id': self.current_game['game_id']})
                    result = cursor.fetchone()
                    if result:
                        current_player, turn_time = result
                        cursor.execute("""SELECT EXTRACT(SECOND FROM (CURRENT_TIMESTAMP - start_time)) FROM register.games WHERE game_id = :game_id""", {'game_id': self.current_game['game_id']})
                        elapsed_result = cursor.fetchone()
                        
                        # ЗАЩИТА ОТ None
                        if elapsed_result and elapsed_result[0] is not None:
                            elapsed_seconds = int(elapsed_result[0])
                        else:
                            elapsed_seconds = 0  # Значение по умолчанию
                        
                        if self.current_game['current_player'] != current_player:
                            self.current_game['current_player'] = current_player
                            self.current_game['time_left'] = turn_time * 60 - elapsed_seconds
                            self.turn_label.config(text=f"Сейчас ходит: {current_player} (ход {turn_time} мин)")
                            self.update_timer()
                            self.update_input_state()
                self.update_game_data()
                self.game_window.after(1000, self.periodic_update)
            except Exception as e:
                print(f"Ошибка в periodic_update: {e}")
                # Все равно продолжаем обновление
                self.game_window.after(1000, self.periodic_update)

    def can_form_word(self, source_word, target_word):
        if len(target_word) < 3:
            return False
        if target_word == source_word.lower():
            return False
        from collections import defaultdict
        source_counts = defaultdict(int)
        for char in source_word.lower():
            source_counts[char] += 1
        for char in target_word.lower():
            if source_counts[char] <= 0:
                return False
            source_counts[char] -= 1
        return True

    def close_waiting_window(self):
        if hasattr(self, 'waiting_window') and self.waiting_window.winfo_exists():
            self.waiting_window.destroy()

    def check_game_start(self):
        with self.user_connection.cursor() as cursor:
            cursor.execute("""SELECT g.initial_word, g.current_player, g.turn_time_minutes, p.game_id FROM register.games g JOIN register.players p ON g.game_id = p.game_id WHERE p.player_username = :username AND g.status = 'in_progress'""", {'username': self.current_user})
            result = cursor.fetchone()
            if result:
                initial_word, current_player, turn_time, game_id = result
                self.close_waiting_window()
                self.show_game_field(game_id, initial_word, current_player, turn_time)
                return
        if hasattr(self, 'root') and self.root.winfo_exists():
            self.root.after(2000, self.check_game_start)


if __name__ == "__main__":
    root = ctk.CTk()

    window_width = 1200
    window_height = 675
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    app = GameApp(root)
    root.mainloop()
