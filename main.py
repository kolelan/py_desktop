import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser, font
import random
import time
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SchulteTableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Таблицы Шульте")
        self.root.geometry("1000x800")

        # Настройки по умолчанию
        self.rows = 5
        self.cols = 5
        self.highlight_color = "yellow"
        self.font_color = "black"
        self.cell_color = "white"
        self.active_cell_color = "lightblue"
        self.font_family = "Arial"
        self.font_size = 12
        self.current_user = None
        self.stats = {}
        self.session_start_time = None
        self.session_data = []
        self.timer_running = False
        self.buttons = []
        self.hover_mode = False
        self.click_mode = True
        self.current_number = 1
        self.correct_hovers = 0
        self.correct_clicks = 0

        # Загружаем статистику
        self.load_stats()

        # Создаем интерфейс
        self.create_widgets()

    def create_widgets(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Фрейм управления
        control_frame = ttk.Frame(main_frame, padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Выбор пользователя
        ttk.Label(control_frame, text="Пользователь:").grid(row=0, column=0, padx=5, pady=5)
        self.user_var = tk.StringVar()
        self.user_combobox = ttk.Combobox(control_frame, textvariable=self.user_var)
        self.user_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.update_user_list()

        ttk.Button(control_frame, text="Новый пользователь", command=self.add_new_user).grid(row=0, column=2, padx=5,
                                                                                             pady=5)

        # Настройки таблицы
        ttk.Label(control_frame, text="Строки:").grid(row=1, column=0, padx=5, pady=5)
        self.rows_var = tk.IntVar(value=self.rows)
        ttk.Spinbox(control_frame, from_=3, to=10, textvariable=self.rows_var, width=5).grid(row=1, column=1, padx=5,
                                                                                             pady=5)

        ttk.Label(control_frame, text="Столбцы:").grid(row=1, column=2, padx=5, pady=5)
        self.cols_var = tk.IntVar(value=self.cols)
        ttk.Spinbox(control_frame, from_=3, to=10, textvariable=self.cols_var, width=5).grid(row=1, column=3, padx=5,
                                                                                             pady=5)

        # Цвета
        ttk.Button(control_frame, text="Цвет выделения", command=lambda: self.choose_color("highlight")).grid(row=1,
                                                                                                              column=4,
                                                                                                              padx=5,
                                                                                                              pady=5)
        self.highlight_color_label = ttk.Label(control_frame, background=self.highlight_color, width=3)
        self.highlight_color_label.grid(row=1, column=5, padx=5, pady=5)

        ttk.Button(control_frame, text="Цвет шрифта", command=lambda: self.choose_color("font")).grid(row=2, column=0,
                                                                                                      padx=5, pady=5)
        self.font_color_label = ttk.Label(control_frame, background=self.font_color, width=3)
        self.font_color_label.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(control_frame, text="Цвет ячеек", command=lambda: self.choose_color("cell")).grid(row=2, column=2,
                                                                                                     padx=5, pady=5)
        self.cell_color_label = ttk.Label(control_frame, background=self.cell_color, width=3)
        self.cell_color_label.grid(row=2, column=3, padx=5, pady=5)

        ttk.Button(control_frame, text="Цвет активной", command=lambda: self.choose_color("active")).grid(row=2,
                                                                                                          column=4,
                                                                                                          padx=5,
                                                                                                          pady=5)
        self.active_color_label = ttk.Label(control_frame, background=self.active_cell_color, width=3)
        self.active_color_label.grid(row=2, column=5, padx=5, pady=5)

        # Настройки шрифта
        ttk.Label(control_frame, text="Шрифт:").grid(row=3, column=0, padx=5, pady=5)
        self.font_family_var = tk.StringVar(value=self.font_family)
        try:
            available_fonts = list(font.families())
        except:
            available_fonts = ["Arial", "Times New Roman", "Courier New", "Verdana"]

        self.font_combobox = ttk.Combobox(control_frame, textvariable=self.font_family_var, values=available_fonts)
        self.font_combobox.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(control_frame, text="Размер:").grid(row=3, column=2, padx=5, pady=5)
        self.font_size_var = tk.IntVar(value=self.font_size)
        ttk.Spinbox(control_frame, from_=8, to=36, textvariable=self.font_size_var, width=5).grid(row=3, column=3,
                                                                                                  padx=5, pady=5)

        # Режимы игры
        self.click_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Режим нажатия", variable=self.click_mode_var,
                        command=self.toggle_game_modes).grid(row=3, column=4, padx=5, pady=5)

        self.hover_mode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(control_frame, text="Режим наведения", variable=self.hover_mode_var,
                        command=self.toggle_game_modes).grid(row=3, column=5, padx=5, pady=5)

        # Кнопки управления
        self.start_stop_button = ttk.Button(control_frame, text="Старт (Пробел)", command=self.toggle_start_stop)
        self.start_stop_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        ttk.Button(control_frame, text="Обновить таблицу", command=self.reset_table).grid(row=4, column=2, columnspan=2,
                                                                                          padx=5, pady=5)

        # Счетчики
        ttk.Label(control_frame, text="Правильные нажатия:").grid(row=4, column=4, padx=5, pady=5)
        self.clicks_counter = ttk.Label(control_frame, text="0")
        self.clicks_counter.grid(row=4, column=5, padx=5, pady=5)

        # Привязываем пробел к кнопке старт/стоп
        self.root.bind('<space>', lambda event: self.toggle_start_stop())

        # Контейнер для таблицы и статистики
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Фрейм таблицы с прокруткой
        self.table_frame = ttk.Frame(self.notebook)
        self.table_canvas = tk.Canvas(self.table_frame)
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.table_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.table_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.table_canvas.configure(
                scrollregion=self.table_canvas.bbox("all")
            )
        )

        self.table_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.table_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.table_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.table_frame.pack(fill="both", expand=True)

        self.notebook.add(self.table_frame, text="Таблица")

        # Фрейм статистики
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Статистика")

    def choose_color(self, color_type):
        color = colorchooser.askcolor(title=f"Выберите цвет {color_type}")[1]
        if color:
            if color_type == "highlight":
                self.highlight_color = color
                self.highlight_color_label.config(background=color)
            elif color_type == "font":
                self.font_color = color
                self.font_color_label.config(background=color)
            elif color_type == "cell":
                self.cell_color = color
                self.cell_color_label.config(background=color)
            elif color_type == "active":
                self.active_cell_color = color
                self.active_color_label.config(background=color)

            if self.timer_running:
                self.generate_table()

    def toggle_game_modes(self):
        self.hover_mode = self.hover_mode_var.get()
        self.click_mode = self.click_mode_var.get()

        # Гарантируем, что хотя бы один режим активен
        if not self.hover_mode and not self.click_mode:
            self.click_mode_var.set(True)
            self.click_mode = True

    def update_user_list(self):
        users = list(self.stats.keys())
        self.user_combobox['values'] = users
        if users and not self.user_var.get():
            self.user_var.set(users[0])

    def add_new_user(self):
        new_user = simpledialog.askstring("Новый пользователь", "Введите имя нового пользователя:")
        if new_user:
            if new_user not in self.stats:
                self.stats[new_user] = []
            self.user_var.set(new_user)
            self.update_user_list()

    def toggle_start_stop(self):
        if not self.user_var.get():
            messagebox.showwarning("Ошибка", "Выберите пользователя!")
            return

        if not self.timer_running:
            self.start_session()
        else:
            self.stop_session()

    def start_session(self):
        try:
            self.current_user = self.user_var.get()
            self.rows = self.rows_var.get()
            self.cols = self.cols_var.get()
            self.font_family = self.font_family_var.get()
            self.font_size = self.font_size_var.get()

            self.session_start_time = time.time()
            self.session_data = []
            self.timer_running = True
            self.current_number = 1
            self.correct_hovers = 0
            self.correct_clicks = 0
            self.clicks_counter.config(text="0")
            self.start_stop_button.config(text="Стоп (Пробел)")

            self.generate_table()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось начать сессию: {str(e)}")
            self.timer_running = False
            self.start_stop_button.config(text="Старт (Пробел)")

    def reset_table(self):
        if self.timer_running:
            self.stop_session(save_stats=False)
        self.generate_table()

    def generate_table(self):
        try:
            # Очищаем предыдущую таблицу
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            self.buttons = []

            # Генерируем случайные числа
            numbers = list(range(1, self.rows * self.cols + 1))
            random.shuffle(numbers)

            # Создаем стиль для кнопок
            style = ttk.Style()
            style.configure("Table.TButton",
                            font=(self.font_family, self.font_size),
                            foreground=self.font_color,
                            background=self.cell_color,
                            padding=10)
            style.configure("Highlight.TButton",
                            font=(self.font_family, self.font_size),
                            foreground=self.font_color,
                            background=self.highlight_color,
                            padding=10)
            style.configure("Active.TButton",
                            font=(self.font_family, self.font_size),
                            foreground=self.font_color,
                            background=self.active_cell_color,
                            padding=10)

            # Создаем таблицу
            for i in range(self.rows):
                self.scrollable_frame.rowconfigure(i, weight=1)
                for j in range(self.cols):
                    self.scrollable_frame.columnconfigure(j, weight=1)

                    number = numbers.pop()
                    btn = ttk.Button(
                        self.scrollable_frame,
                        text=str(number),
                        style="Table.TButton",
                        command=lambda n=number: self.cell_clicked(n)
                    )

                    # Привязываем события мыши
                    btn.bind("<Enter>", lambda e, n=number: self.cell_hover(n))
                    btn.bind("<Leave>", lambda e: self.cell_leave())

                    btn.grid(row=i, column=j, sticky="nsew", padx=2, pady=2)
                    self.buttons.append(btn)

            # Определяем центральные ячейки
            self.highlight_center_cells()

            # Обновляем область прокрутки
            self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all"))

            # Запоминаем время начала сессии
            self.last_click_time = time.time()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать таблицу: {str(e)}")
            self.stop_session()

    def highlight_center_cells(self):
        """Выделяет центральные ячейки в зависимости от размера таблицы"""
        center_row1 = self.rows // 2
        center_row2 = center_row1 if self.rows % 2 == 1 else center_row1 - 1
        center_col1 = self.cols // 2
        center_col2 = center_col1 if self.cols % 2 == 1 else center_col1 - 1

        for i in range(center_row2, center_row1 + 1):
            for j in range(center_col2, center_col1 + 1):
                for btn in self.buttons:
                    if btn.grid_info()["row"] == i and btn.grid_info()["column"] == j:
                        btn.config(style="Highlight.TButton")

    def cell_hover(self, number):
        if not self.timer_running or not self.hover_mode:
            return

        if number == self.current_number:
            self.current_number += 1
            self.correct_hovers += 1
            self.clicks_counter.config(text=str(self.correct_hovers))

            # Подсветка активной ячейки
            for btn in self.buttons:
                if btn.cget("text") == str(number):
                    btn.config(style="Active.TButton")

            # Если все ячейки пройдены
            if self.current_number > self.rows * self.cols:
                self.stop_session()

    def cell_leave(self):
        # Возвращаем обычный стиль для всех кнопок, кроме выделенных центральных
        for btn in self.buttons:
            if btn.cget("style") == "Active.TButton":
                btn.config(style="Table.TButton")

    def cell_clicked(self, number):
        if not self.timer_running or not self.click_mode:
            return

        if number == self.current_number:
            self.current_number += 1
            self.correct_clicks += 1
            self.clicks_counter.config(text=str(self.correct_clicks))

            # Запоминаем время реакции
            current_time = time.time()
            time_diff = current_time - self.last_click_time
            self.last_click_time = current_time
            self.session_data.append(time_diff)

            # Если все ячейки пройдены
            if self.current_number > self.rows * self.cols:
                self.stop_session()
            else:
                self.generate_table()

    def stop_session(self, save_stats=True):
        try:
            self.timer_running = False
            self.start_stop_button.config(text="Старт (Пробел)")

            if save_stats and self.session_start_time:
                session_time = time.time() - self.session_start_time
                avg_time = sum(self.session_data) / len(self.session_data) if self.session_data else 0

                # Сохраняем статистику
                self.stats[self.current_user].append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "rows": self.rows,
                    "cols": self.cols,
                    "font_family": self.font_family,
                    "font_size": self.font_size,
                    "total_time": session_time,
                    "avg_time_per_cell": avg_time,
                    "cells_clicked": len(self.session_data),
                    "correct_hovers": self.correct_hovers,
                    "correct_clicks": self.correct_clicks,
                    "mode": "hover" if self.hover_mode else "click"
                })

                self.save_stats()
                self.show_stats()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось завершить сессию: {str(e)}")

    def show_stats(self):
        try:
            # Очищаем предыдущую статистику
            for widget in self.stats_frame.winfo_children():
                widget.destroy()

            if not self.current_user or self.current_user not in self.stats:
                ttk.Label(self.stats_frame, text="Нет данных для отображения").pack()
                return

            user_stats = self.stats[self.current_user]
            if not user_stats:
                ttk.Label(self.stats_frame, text="Нет данных для отображения").pack()
                return

            # Создаем фрейм для графиков
            graph_frame = ttk.Frame(self.stats_frame)
            graph_frame.pack(fill=tk.BOTH, expand=True)

            # Создаем фигуру для графиков
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

            # Подготавливаем данные для графиков
            dates = []
            avg_times = []
            sizes = []
            modes = []
            clicks = []
            hovers = []

            for session in user_stats:
                dates.append(datetime.strptime(session["date"], "%Y-%m-%d %H:%M:%S"))
                avg_times.append(session["avg_time_per_cell"])
                sizes.append(f"{session['rows']}x{session['cols']}")
                modes.append(session.get("mode", "click"))
                clicks.append(session.get("correct_clicks", 0))
                hovers.append(session.get("correct_hovers", 0))

            # График средней скорости
            ax1.plot(dates, avg_times, 'o-')
            ax1.set_title(f"Среднее время на ячейку для {self.current_user}")
            ax1.set_ylabel("Время (сек)")
            ax1.grid(True)

            # График правильных действий
            ax2.plot(dates, clicks, 'o-', label='Правильные нажатия')
            ax2.plot(dates, hovers, 's-', label='Правильные наведения')
            ax2.set_title("Результаты по режимам")
            ax2.set_ylabel("Количество")
            ax2.legend()
            ax2.grid(True)

            # Вращаем даты для лучшего отображения
            for ax in [ax1, ax2]:
                plt.sca(ax)
                plt.xticks(rotation=45)

            plt.tight_layout()

            # Встраиваем график в Tkinter
            canvas = FigureCanvasTkAgg(fig, master=graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # Таблица с последними результатами
            last_sessions = user_stats[-5:]

            columns = ("Дата", "Размер", "Режим", "Время", "Нажатия", "Наведения")
            tree = ttk.Treeview(self.stats_frame, columns=columns, show="headings",
                                height=min(6, len(last_sessions) + 1))

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100, anchor=tk.CENTER)

            tree.column("Дата", width=150)

            for session in reversed(last_sessions):
                tree.insert("", 0, values=(
                    session["date"],
                    f"{session['rows']}x{session['cols']}",
                    session.get("mode", "click"),
                    f"{session['total_time']:.1f} сек",
                    session.get("correct_clicks", 0),
                    session.get("correct_hovers", 0)
                ))

            scrollbar = ttk.Scrollbar(self.stats_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)

            tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отобразить статистику: {str(e)}")

    def load_stats(self):
        try:
            if os.path.exists("schulte_stats.json"):
                with open("schulte_stats.json", "r") as f:
                    self.stats = json.load(f)
            else:
                self.stats = {}
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить статистику: {str(e)}")
            self.stats = {}

    def save_stats(self):
        try:
            with open("schulte_stats.json", "w") as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить статистику: {str(e)}")


if __name__ == "__main__":
    try:
        root = tk.Tk()
        style = ttk.Style()
        style.theme_use('clam')

        app = SchulteTableApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")