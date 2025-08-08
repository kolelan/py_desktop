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
        self.rows = 4
        self.cols = 4
        self.cell_min_width = 0
        self.cell_min_height = 0
        self.logging_enabled = True

        # Цвета
        self.bg_color = "#f0f0f0"
        self.highlight_color = "yellow"
        self.font_color = "black"
        self.cell_color = "white"
        self.active_cell_color = "lightblue"
        self.target_color = "red"
        self.timer_color = "red"
        self.timer_bg_color = "#f0f0f0"
        self.timer2_color = "red"
        self.timer2_bg_color = "#f0f0f0"

        # Шрифты
        self.font_family = "Arial"
        self.font_size = 40
        self.target_font_family = "Arial"
        self.target_font_size = 40
        self.timer_font_family = "Arial"
        self.timer_font_size = 40
        self.timer2_font_family = "Arial"
        self.timer2_font_size = 40

        # Состояние приложения
        self.current_user = None
        self.stats = {}
        self.session_start_time = None
        self.session_data = []
        self.timer_running = False
        self.buttons = []
        self.click_refresh_mode = True
        self.click_no_refresh_mode = False
        self.hover_mode = False
        self.simple_mode = False
        self.current_number = 1
        self.correct_hovers = 0
        self.correct_clicks = 0
        self.after_id = None
        self.timer_after_id = None
        self.timer2_after_id = None
        self.generating_table = False
        self.is_closing = False

        # Переменные для режимов игры
        self.game_mode_var = tk.StringVar(value="click_refresh")

        # Переменные для управления видимостью элементов
        self.show_new_user = tk.BooleanVar(value=True)
        self.show_user_select = tk.BooleanVar(value=True)
        self.show_rows = tk.BooleanVar(value=True)
        self.show_cols = tk.BooleanVar(value=True)
        self.show_game_modes = tk.BooleanVar(value=True)
        self.show_target = tk.BooleanVar(value=True)
        self.show_timer = tk.BooleanVar(value=True)
        self.show_timer2 = tk.BooleanVar(value=True)
        self.show_reset_table = tk.BooleanVar(value=True)
        self.show_start_stop = tk.BooleanVar(value=True)

        # Загружаем статистику
        self.load_stats()

        # Создаем интерфейс
        self.create_widgets()

        # Применяем цвет фона
        self.apply_bg_color()

        # Переопределяем закрытие окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Обработка закрытия окна"""
        try:
            self.is_closing = True
            if self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None
            if self.timer_after_id:
                self.root.after_cancel(self.timer_after_id)
                self.timer_after_id = None
            if self.timer2_after_id:
                self.root.after_cancel(self.timer2_after_id)
                self.timer2_after_id = None
            self.root.unbind("<Configure>")
            self.root.destroy()
        except Exception as e:
            self.log_event("error", "on_closing", f"Ошибка при закрытии приложения: {str(e)}")
            print(f"Ошибка при закрытии приложения: {str(e)}")

    def log_event(self, event_type, method_name, details):
        """Записывает событие в shulte_log.json, если логирование включено"""
        if not self.logging_enabled or self.is_closing:
            return
        try:
            log_entry = {
                "type": event_type,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "method": method_name,
                "details": details
            }
            log_file = "shulte_log.json"
            logs = []
            if os.path.exists(log_file):
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        logs = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"Ошибка чтения JSON: {str(e)}")
                    logs = []
            logs.append(log_entry)
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка при записи лога: {str(e)}")

    def apply_bg_color(self):
        """Применяет цвет фона ко всем виджетам"""
        if self.is_closing:
            return
        try:
            self.root.configure(bg=self.bg_color)
            self.notebook.configure(style="Custom.TNotebook")
            self.table_frame.configure(style="Custom.TFrame")
            self.stats_frame.configure(style="Custom.TFrame")
            self.settings_frame.configure(style="Custom.TFrame")
            self.colors_frame.configure(style="Custom.TFrame")
            self.fonts_frame.configure(style="Custom.TFrame")
            self.controls_frame.configure(style="Custom.TFrame")
            self.control_frame.configure(style="Custom.TFrame")
        except Exception as e:
            self.log_event("error", "apply_bg_color", f"Ошибка при применении цвета фона: {str(e)}")

    def create_widgets(self):
        try:
            # Создаем стили для виджетов
            style = ttk.Style()
            style.configure("Custom.TFrame", background=self.bg_color)
            style.configure("Custom.TNotebook", background=self.bg_color)
            style.configure("Custom.TNotebook.Tab", background=self.bg_color)

            # Основной контейнер
            main_frame = ttk.Frame(self.root)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Фрейм управления
            self.control_frame = ttk.Frame(main_frame, padding="10")
            self.control_frame.pack(fill=tk.X, pady=(0, 10))

            # Настройка столбцов для равномерного распределения
            self.control_frame.columnconfigure(0, weight=1)
            self.control_frame.columnconfigure(1, weight=1)
            self.control_frame.columnconfigure(2, weight=1)
            self.control_frame.columnconfigure(3, weight=1)

            # Первый столбец: Пользователь, строки, столбцы
            self.new_user_button = ttk.Button(self.control_frame, text="Новый пользователь", command=self.add_new_user)
            self.new_user_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            self.user_label = ttk.Label(self.control_frame, text="Пользователь:")
            self.user_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.user_var = tk.StringVar()
            self.user_combobox = ttk.Combobox(self.control_frame, textvariable=self.user_var)
            self.user_combobox.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
            self.rows_label = ttk.Label(self.control_frame, text="Строки:")
            self.rows_label.grid(row=3, column=0, padx=(5, 2), pady=5, sticky="w")
            self.rows_var = tk.IntVar(value=self.rows)
            self.rows_spinbox = ttk.Spinbox(self.control_frame, from_=3, to=10, textvariable=self.rows_var, width=5)
            self.rows_spinbox.grid(row=3, column=0, padx=(60, 5), pady=5, sticky="w")
            self.cols_label = ttk.Label(self.control_frame, text="Столбцы:")
            self.cols_label.grid(row=4, column=0, padx=(5, 2), pady=5, sticky="w")
            self.cols_var = tk.IntVar(value=self.cols)
            self.cols_spinbox = ttk.Spinbox(self.control_frame, from_=3, to=10, textvariable=self.cols_var, width=5)
            self.cols_spinbox.grid(row=4, column=0, padx=(60, 5), pady=5, sticky="w")

            # Второй столбец: Режимы игры (радио кнопки)
            self.game_mode_frame = ttk.LabelFrame(self.control_frame, text="Режим игры", padding="5")
            self.game_mode_frame.grid(row=0, column=1, rowspan=5, padx=5, pady=5, sticky="nsw")
            ttk.Radiobutton(self.game_mode_frame, text="Нажатие с обновлением", value="click_refresh",
                            variable=self.game_mode_var, command=self.toggle_game_modes).pack(anchor="w", padx=5, pady=2)
            ttk.Radiobutton(self.game_mode_frame, text="Нажатие без обновления", value="click_no_refresh",
                            variable=self.game_mode_var, command=self.toggle_game_modes).pack(anchor="w", padx=5, pady=2)
            ttk.Radiobutton(self.game_mode_frame, text="Режим наведения", value="hover",
                            variable=self.game_mode_var, command=self.toggle_game_modes).pack(anchor="w", padx=5, pady=2)
            ttk.Radiobutton(self.game_mode_frame, text="Простой режим", value="simple",
                            variable=self.game_mode_var, command=self.toggle_game_modes).pack(anchor="w", padx=5, pady=2)

            # Третий столбец: Таймер 1, Ищем, Счетчик, Таймер 2
            self.timer_label = ttk.Label(self.control_frame, text="0.000",
                                         font=(self.timer_font_family, self.timer_font_size),
                                         foreground=self.timer_color, background=self.timer_bg_color)
            self.timer_label.grid(row=1, column=2, padx=5, pady=5, sticky="w")
            self.target_label = ttk.Label(self.control_frame, text="Ищем:")
            self.target_label.grid(row=2, column=2, padx=5, pady=5, sticky="w")
            self.clicks_counter = ttk.Label(self.control_frame, text="0",
                                            font=(self.target_font_family, self.target_font_size),
                                            foreground=self.target_color)
            self.clicks_counter.grid(row=3, column=2, padx=5, pady=5, sticky="w")
            self.timer2_label = ttk.Label(self.control_frame, text="0.000",
                                          font=(self.timer2_font_family, self.timer2_font_size),
                                          foreground=self.timer2_color, background=self.timer2_bg_color)
            self.timer2_label.grid(row=4, column=2, padx=5, pady=5, sticky="w")

            # Четвертый столбец: Кнопки управления
            self.reset_table_button = ttk.Button(self.control_frame, text="Обновить таблицу", command=self.reset_table)
            self.reset_table_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
            self.start_stop_button = ttk.Button(self.control_frame, text="Старт (Пробел)", command=self.toggle_start_stop)
            self.start_stop_button.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

            # Контейнер для таблицы, статистики и настроек
            self.notebook = ttk.Notebook(main_frame)
            self.notebook.pack(fill=tk.BOTH, expand=True)

            # Фрейм таблицы с прокруткой
            self.table_frame = ttk.Frame(self.notebook)
            self.table_canvas = tk.Canvas(self.table_frame, bg=self.bg_color)
            self.v_scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.table_canvas.yview)
            self.h_scrollbar = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.table_canvas.xview)
            self.scrollable_frame = ttk.Frame(self.table_canvas)

            self.scrollable_frame.bind(
                "<Configure>",
                lambda e: self.table_canvas.configure(
                    scrollregion=self.table_canvas.bbox("all")
                )
            )

            self.table_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            self.table_canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

            self.table_canvas.pack(side="top", fill="both", expand=True)
            self.v_scrollbar.pack(side="right", fill="y")
            self.h_scrollbar.pack(side="bottom", fill="x")
            self.table_frame.pack(fill="both", expand=True)

            self.notebook.add(self.table_frame, text="Таблица")

            # Фрейм статистики
            self.stats_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.stats_frame, text="Статистика")

            # Фрейм настроек
            self.settings_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.settings_frame, text="Настройки")

            # Фрейм цветов
            self.colors_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.colors_frame, text="Цвета")

            # Фрейм шрифтов
            self.fonts_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.fonts_frame, text="Шрифты")

            # Фрейм управления
            self.controls_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.controls_frame, text="Управление")

            # Создаем содержимое вкладок
            self.create_settings_tab()
            self.create_colors_tab()
            self.create_fonts_tab()
            self.create_controls_tab()

            # Привязываем пробел к кнопке старт/стоп
            self.root.bind('<space>', lambda event: self.toggle_start_stop())

            # Привязываем событие изменения размера только к корневому окну
            self.root.bind("<Configure>", self.update_table_size)

            # Обновляем список пользователей
            self.update_user_list()
        except Exception as e:
            self.log_event("error", "create_widgets", f"Ошибка при создании виджетов: {str(e)}")

    def create_colors_tab(self):
        """Создает вкладку с настройками цветов"""
        try:
            color_frame = ttk.LabelFrame(self.colors_frame, text="Цвета", padding="10")
            color_frame.pack(fill=tk.X, padx=5, pady=5)

            ttk.Button(color_frame, text="Цвет выделения", command=lambda: self.choose_color("highlight")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.highlight_color_label = ttk.Label(color_frame, background=self.highlight_color, width=3)
            self.highlight_color_label.grid(row=0, column=1, padx=5, pady=5)

            ttk.Button(color_frame, text="Цвет шрифта", command=lambda: self.choose_color("font")).grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.font_color_label = ttk.Label(color_frame, background=self.font_color, width=3)
            self.font_color_label.grid(row=1, column=1, padx=5, pady=5)

            ttk.Button(color_frame, text="Цвет ячеек", command=lambda: self.choose_color("cell")).grid(row=2, column=0, padx=5, pady=5, sticky="w")
            self.cell_color_label = ttk.Label(color_frame, background=self.cell_color, width=3)
            self.cell_color_label.grid(row=2, column=1, padx=5, pady=5)

            ttk.Button(color_frame, text="Цвет активной", command=lambda: self.choose_color("active")).grid(row=3, column=0, padx=5, pady=5, sticky="w")
            self.active_color_label = ttk.Label(color_frame, background=self.active_cell_color, width=3)
            self.active_color_label.grid(row=3, column=1, padx=5, pady=5)

            ttk.Button(color_frame, text="Цвет искомой цифры", command=lambda: self.choose_color("target")).grid(row=4, column=0, padx=5, pady=5, sticky="w")
            self.target_color_label = ttk.Label(color_frame, background=self.target_color, width=3)
            self.target_color_label.grid(row=4, column=1, padx=5, pady=5)

            ttk.Button(color_frame, text="Цвет таймера", command=lambda: self.choose_color("timer")).grid(row=5, column=0, padx=5, pady=5, sticky="w")
            self.timer_color_label = ttk.Label(color_frame, background=self.timer_color, width=3)
            self.timer_color_label.grid(row=5, column=1, padx=5, pady=5)

            ttk.Button(color_frame, text="Фон таймера", command=lambda: self.choose_color("timer_bg")).grid(row=6, column=0, padx=5, pady=5, sticky="w")
            self.timer_bg_color_label = ttk.Label(color_frame, background=self.timer_bg_color, width=3)
            self.timer_bg_color_label.grid(row=6, column=1, padx=5, pady=5)

            ttk.Button(color_frame, text="Цвет таймера 2", command=lambda: self.choose_color("timer2")).grid(row=7, column=0, padx=5, pady=5, sticky="w")
            self.timer2_color_label = ttk.Label(color_frame, background=self.timer2_color, width=3)
            self.timer2_color_label.grid(row=7, column=1, padx=5, pady=5)

            ttk.Button(color_frame, text="Фон таймера 2", command=lambda: self.choose_color("timer2_bg")).grid(row=8, column=0, padx=5, pady=5, sticky="w")
            self.timer2_bg_color_label = ttk.Label(color_frame, background=self.timer2_bg_color, width=3)
            self.timer2_bg_color_label.grid(row=8, column=1, padx=5, pady=5)

            ttk.Button(color_frame, text="Цвет фона", command=lambda: self.choose_color("bg")).grid(row=9, column=0, padx=5, pady=5, sticky="w")
            self.bg_color_label = ttk.Label(color_frame, background=self.bg_color, width=3)
            self.bg_color_label.grid(row=9, column=1, padx=5, pady=5)
        except Exception as e:
            self.log_event("error", "create_colors_tab", f"Ошибка при создании вкладки цветов: {str(e)}")

    def create_fonts_tab(self):
        """Создает вкладку с настройками шрифтов"""
        try:
            font_frame = ttk.LabelFrame(self.fonts_frame, text="Шрифты", padding="10")
            font_frame.pack(fill=tk.X, padx=5, pady=5)

            ttk.Label(font_frame, text="Шрифт таблицы:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.font_family_var = tk.StringVar(value=self.font_family)
            try:
                available_fonts = list(font.families())
            except:
                available_fonts = ["Arial", "Times New Roman", "Courier New", "Verdana"]
            self.font_combobox = ttk.Combobox(font_frame, textvariable=self.font_family_var, values=available_fonts)
            self.font_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

            ttk.Label(font_frame, text="Размер шрифта:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.font_size_var = tk.IntVar(value=self.font_size)
            ttk.Spinbox(font_frame, from_=8, to=72, textvariable=self.font_size_var, width=5).grid(row=1, column=1, padx=5, pady=5)

            ttk.Label(font_frame, text="Шрифт искомой цифры:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
            self.target_font_family_var = tk.StringVar(value=self.target_font_family)
            self.target_font_combobox = ttk.Combobox(font_frame, textvariable=self.target_font_family_var, values=available_fonts)
            self.target_font_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

            ttk.Label(font_frame, text="Размер искомой цифры:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
            self.target_font_size_var = tk.IntVar(value=self.target_font_size)
            ttk.Spinbox(font_frame, from_=8, to=72, textvariable=self.target_font_size_var, width=5).grid(row=3, column=1, padx=5, pady=5)

            ttk.Label(font_frame, text="Шрифт таймера:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
            self.timer_font_family_var = tk.StringVar(value=self.timer_font_family)
            self.timer_font_combobox = ttk.Combobox(font_frame, textvariable=self.timer_font_family_var, values=available_fonts)
            self.timer_font_combobox.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

            ttk.Label(font_frame, text="Размер таймера:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
            self.timer_font_size_var = tk.IntVar(value=self.timer_font_size)
            ttk.Spinbox(font_frame, from_=8, to=72, textvariable=self.timer_font_size_var, width=5).grid(row=5, column=1, padx=5, pady=5)

            ttk.Label(font_frame, text="Шрифт таймера 2:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
            self.timer2_font_family_var = tk.StringVar(value=self.timer2_font_family)
            self.timer2_font_combobox = ttk.Combobox(font_frame, textvariable=self.timer2_font_family_var, values=available_fonts)
            self.timer2_font_combobox.grid(row=6, column=1, padx=5, pady=5, sticky="ew")

            ttk.Label(font_frame, text="Размер таймера 2:").grid(row=7, column=0, padx=5, pady=5, sticky="w")
            self.timer2_font_size_var = tk.IntVar(value=self.timer2_font_size)
            ttk.Spinbox(font_frame, from_=8, to=72, textvariable=self.timer2_font_size_var, width=5).grid(row=7, column=1, padx=5, pady=5)
        except Exception as e:
            self.log_event("error", "create_fonts_tab", f"Ошибка при создании вкладки шрифтов: {str(e)}")

    def create_settings_tab(self):
        """Создает вкладку с настройками размеров ячеек"""
        try:
            size_frame = ttk.LabelFrame(self.settings_frame, text="Размеры ячеек", padding="10")
            size_frame.pack(fill=tk.X, padx=5, pady=5)

            ttk.Label(size_frame, text="Минимальная ширина (px):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.cell_min_width_var = tk.IntVar(value=self.cell_min_width)
            ttk.Spinbox(size_frame, from_=20, to=200, textvariable=self.cell_min_width_var, width=5).grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(size_frame, text="Минимальная высота (px):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.cell_min_height_var = tk.IntVar(value=self.cell_min_height)
            ttk.Spinbox(size_frame, from_=20, to=200, textvariable=self.cell_min_height_var, width=5).grid(row=1, column=1, padx=5, pady=5)

            ttk.Button(self.settings_frame, text="Применить настройки", command=self.apply_settings).pack(pady=10)
        except Exception as e:
            self.log_event("error", "create_settings_tab", f"Ошибка при создании вкладки настроек: {str(e)}")

    def create_controls_tab(self):
        """Создает вкладку с настройками видимости элементов управления"""
        try:
            controls_frame = ttk.LabelFrame(self.controls_frame, text="Управление элементами", padding="10")
            controls_frame.pack(fill=tk.X, padx=5, pady=5)

            ttk.Checkbutton(controls_frame, text="Показать кнопку 'Новый пользователь'", variable=self.show_new_user,
                            command=self.update_control_visibility).grid(row=0, column=0, padx=5, pady=5, sticky="w")
            ttk.Checkbutton(controls_frame, text="Показать выбор пользователя", variable=self.show_user_select,
                            command=self.update_control_visibility).grid(row=1, column=0, padx=5, pady=5, sticky="w")
            ttk.Checkbutton(controls_frame, text="Показать настройку строк", variable=self.show_rows,
                            command=self.update_control_visibility).grid(row=2, column=0, padx=5, pady=5, sticky="w")
            ttk.Checkbutton(controls_frame, text="Показать настройку столбцов", variable=self.show_cols,
                            command=self.update_control_visibility).grid(row=3, column=0, padx=5, pady=5, sticky="w")
            ttk.Checkbutton(controls_frame, text="Показать режимы игры", variable=self.show_game_modes,
                            command=self.update_control_visibility).grid(row=4, column=0, padx=5, pady=5, sticky="w")
            ttk.Checkbutton(controls_frame, text="Показать счетчик 'Ищем'", variable=self.show_target,
                            command=self.update_control_visibility).grid(row=5, column=0, padx=5, pady=5, sticky="w")
            ttk.Checkbutton(controls_frame, text="Показать таймер", variable=self.show_timer,
                            command=self.update_control_visibility).grid(row=6, column=0, padx=5, pady=5, sticky="w")
            ttk.Checkbutton(controls_frame, text="Показать таймер 2", variable=self.show_timer2,
                            command=self.update_control_visibility).grid(row=7, column=0, padx=5, pady=5, sticky="w")
            ttk.Checkbutton(controls_frame, text="Показать кнопку 'Обновить таблицу'", variable=self.show_reset_table,
                            command=self.update_control_visibility).grid(row=8, column=0, padx=5, pady=5, sticky="w")
            ttk.Checkbutton(controls_frame, text="Показать кнопку 'Старт/Стоп'", variable=self.show_start_stop,
                            command=self.update_control_visibility).grid(row=9, column=0, padx=5, pady=5, sticky="w")
        except Exception as e:
            self.log_event("error", "create_controls_tab", f"Ошибка при создании вкладки управления: {str(e)}")

    def update_control_visibility(self):
        """Обновляет видимость элементов управления"""
        if self.is_closing:
            return
        try:
            self.log_event("action", "update_control_visibility", "Обновление видимости элементов управления")
            if self.show_new_user.get():
                self.new_user_button.grid()
            else:
                self.new_user_button.grid_remove()

            if self.show_user_select.get():
                self.user_label.grid()
                self.user_combobox.grid()
            else:
                self.user_label.grid_remove()
                self.user_combobox.grid_remove()

            if self.show_rows.get():
                self.rows_label.grid()
                self.rows_spinbox.grid()
            else:
                self.rows_label.grid_remove()
                self.rows_spinbox.grid_remove()

            if self.show_cols.get():
                self.cols_label.grid()
                self.cols_spinbox.grid()
            else:
                self.cols_label.grid_remove()
                self.cols_spinbox.grid_remove()

            if self.show_game_modes.get():
                self.game_mode_frame.grid()
            else:
                self.game_mode_frame.grid_remove()

            if self.show_target.get():
                self.target_label.grid()
                self.clicks_counter.grid()
            else:
                self.target_label.grid_remove()
                self.clicks_counter.grid_remove()

            if self.show_timer.get():
                self.timer_label.grid()
            else:
                self.timer_label.grid_remove()

            if self.show_timer2.get():
                self.timer2_label.grid()
            else:
                self.timer2_label.grid_remove()

            if self.show_reset_table.get():
                self.reset_table_button.grid()
            else:
                self.reset_table_button.grid_remove()

            if self.show_start_stop.get():
                self.start_stop_button.grid()
            else:
                self.start_stop_button.grid_remove()
        except Exception as e:
            self.log_event("error", "update_control_visibility", f"Ошибка при обновлении видимости: {str(e)}")

    def update_timer(self):
        """Обновляет отображение таймера 1"""
        if self.is_closing or not self.timer_running:
            return
        try:
            elapsed_time = time.time() - self.session_start_time
            seconds = int(elapsed_time)
            milliseconds = int((elapsed_time - seconds) * 1000)
            self.timer_label.config(text=f"{seconds}.{milliseconds:03d}")
            self.timer_after_id = self.root.after(10, self.update_timer)
        except Exception as e:
            self.log_event("error", "update_timer", f"Ошибка при обновлении таймера: {str(e)}")

    def update_timer2(self):
        """Обновляет отображение таймера 2"""
        if self.is_closing or not self.timer_running:
            return
        try:
            elapsed_time = time.time() - self.session_start_time
            seconds = int(elapsed_time)
            milliseconds = int((elapsed_time - seconds) * 1000)
            self.timer2_label.config(text=f"{seconds}.{milliseconds:03d}")
            self.timer2_after_id = self.root.after(10, self.update_timer2)
        except Exception as e:
            self.log_event("error", "update_timer2", f"Ошибка при обновлении таймера 2: {str(e)}")

    def update_table_size(self, event=None):
        """Обновляет размеры таблицы при изменении размера окна"""
        if self.is_closing or self.generating_table or event.widget != self.root:
            return
        try:
            if self.buttons:
                if self.after_id:
                    self.root.after_cancel(self.after_id)
                self.after_id = self.root.after(500, self.generate_table)
        except Exception as e:
            self.log_event("error", "update_table_size", f"Ошибка при обновлении размеров таблицы: {str(e)}")

    def apply_settings(self):
        """Применяет все настройки с вкладок"""
        if self.is_closing:
            return
        try:
            self.log_event("action", "apply_settings", "Применение настроек")
            self.highlight_color = self.highlight_color_label.cget("background")
            self.font_color = self.font_color_label.cget("background")
            self.cell_color = self.cell_color_label.cget("background")
            self.active_cell_color = self.active_color_label.cget("background")
            self.target_color = self.target_color_label.cget("background")
            self.timer_color = self.timer_color_label.cget("background")
            self.timer_bg_color = self.timer_bg_color_label.cget("background")
            self.timer2_color = self.timer2_color_label.cget("background")
            self.timer2_bg_color = self.timer2_bg_color_label.cget("background")
            self.bg_color = self.bg_color_label.cget("background")

            self.font_family = self.font_family_var.get()
            self.font_size = self.font_size_var.get()
            self.target_font_family = self.target_font_family_var.get()
            self.target_font_size = self.target_font_size_var.get()
            self.timer_font_family = self.timer_font_family_var.get()
            self.timer_font_size = self.timer_font_size_var.get()
            self.timer2_font_family = self.timer2_font_family_var.get()
            self.timer2_font_size = self.timer2_font_size_var.get()

            self.cell_min_width = self.cell_min_width_var.get()
            self.cell_min_height = self.cell_min_height_var.get()

            self.clicks_counter.config(font=(self.target_font_family, self.target_font_size),
                                       foreground=self.target_color)
            self.timer_label.config(font=(self.timer_font_family, self.timer_font_size),
                                    foreground=self.timer_color, background=self.timer_bg_color)
            self.timer2_label.config(font=(self.timer2_font_family, self.timer2_font_size),
                                     foreground=self.timer2_color, background=self.timer2_bg_color)
            self.apply_bg_color()

            if self.timer_running and not self.generating_table:
                if self.after_id:
                    self.root.after_cancel(self.after_id)
                self.after_id = self.root.after(500, self.generate_table)

            messagebox.showinfo("Настройки", "Настройки успешно применены!")
        except Exception as e:
            self.log_event("error", "apply_settings", f"Ошибка при применении настроек: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось применить настройки: {str(e)}")

    def choose_color(self, color_type):
        """Выбирает цвет для указанного типа"""
        if self.is_closing:
            return
        try:
            self.log_event("action", "choose_color", f"Выбор цвета: {color_type}")
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
                elif color_type == "target":
                    self.target_color = color
                    self.target_color_label.config(background=color)
                    self.clicks_counter.config(foreground=color)
                elif color_type == "timer":
                    self.timer_color = color
                    self.timer_color_label.config(background=color)
                    self.timer_label.config(foreground=color)
                elif color_type == "timer_bg":
                    self.timer_bg_color = color
                    self.timer_bg_color_label.config(background=color)
                    self.timer_label.config(background=color)
                elif color_type == "timer2":
                    self.timer2_color = color
                    self.timer2_color_label.config(background=color)
                    self.timer2_label.config(foreground=color)
                elif color_type == "timer2_bg":
                    self.timer2_bg_color = color
                    self.timer2_bg_color_label.config(background=color)
                    self.timer2_label.config(background=color)
                elif color_type == "bg":
                    self.bg_color = color
                    self.bg_color_label.config(background=color)
                    self.apply_bg_color()

                if self.timer_running and color_type in ["highlight", "font", "cell", "active"] and not self.generating_table:
                    if self.after_id:
                        self.root.after_cancel(self.after_id)
                    self.after_id = self.root.after(500, self.generate_table)
        except Exception as e:
            self.log_event("error", "choose_color", f"Ошибка при выборе цвета {color_type}: {str(e)}")

    def toggle_game_modes(self):
        """Переключает режимы игры"""
        if self.is_closing:
            return
        try:
            self.log_event("action", "toggle_game_modes", "Переключение режимов игры")
            mode = self.game_mode_var.get()
            self.click_refresh_mode = mode == "click_refresh"
            self.click_no_refresh_mode = mode == "click_no_refresh"
            self.hover_mode = mode == "hover"
            self.simple_mode = mode == "simple"
        except Exception as e:
            self.log_event("error", "toggle_game_modes", f"Ошибка при переключении режимов игры: {str(e)}")

    def update_user_list(self):
        """Обновляет список пользователей"""
        if self.is_closing:
            return
        try:
            users = list(self.stats.keys())
            self.user_combobox['values'] = users
            if users and not self.user_var.get():
                self.user_var.set(users[0])
        except Exception as e:
            self.log_event("error", "update_user_list", f"Ошибка при обновлении списка пользователей: {str(e)}")

    def add_new_user(self):
        """Добавляет нового пользователя"""
        if self.is_closing:
            return
        try:
            self.log_event("action", "add_new_user", "Добавление нового пользователя")
            new_user = simpledialog.askstring("Новый пользователь", "Введите имя нового пользователя:")
            if new_user:
                if new_user not in self.stats:
                    self.stats[new_user] = []
                self.user_var.set(new_user)
                self.update_user_list()
        except Exception as e:
            self.log_event("error", "add_new_user", f"Ошибка при добавлении пользователя: {str(e)}")

    def toggle_start_stop(self):
        """Переключает старт/стоп"""
        if self.is_closing:
            return
        try:
            self.log_event("action", "toggle_start_stop", "Переключение старт/стоп")
            if not self.user_var.get():
                self.log_event("error", "toggle_start_stop", "Пользователь не выбран")
                messagebox.showwarning("Ошибка", "Выберите пользователя!")
                return

            if not self.timer_running:
                self.start_session()
            else:
                self.stop_session()
        except Exception as e:
            self.log_event("error", "toggle_start_stop", f"Ошибка при переключении старт/стоп: {str(e)}")

    def start_session(self):
        """Начинает сессию"""
        if self.is_closing:
            return
        try:
            self.log_event("action", "start_session", f"Начало сессии для пользователя {self.user_var.get()}")
            self.current_user = self.user_var.get()
            self.rows = min(max(self.rows_var.get(), 3), 10)
            self.cols = min(max(self.cols_var.get(), 3), 10)
            self.rows_var.set(self.rows)
            self.cols_var.set(self.cols)
            self.font_family = self.font_family_var.get()
            self.font_size = self.font_size_var.get()
            self.target_font_family = self.target_font_family_var.get()
            self.target_font_size = self.target_font_size_var.get()
            self.timer_font_family = self.timer_font_family_var.get()
            self.timer_font_size = self.timer_font_size_var.get()
            self.timer2_font_family = self.timer2_font_family_var.get()
            self.timer2_font_size = self.timer2_font_size_var.get()
            self.cell_min_width = self.cell_min_width_var.get()
            self.cell_min_height = self.cell_min_height_var.get()

            self.session_start_time = time.time()
            self.session_data = []
            self.timer_running = True
            self.current_number = 1
            self.correct_hovers = 0
            self.correct_clicks = 0
            self.clicks_counter.config(text=str(self.current_number),
                                       font=(self.target_font_family, self.target_font_size),
                                       foreground=self.target_color)
            self.timer_label.config(text="0.000",
                                    font=(self.timer_font_family, self.timer_font_size),
                                    foreground=self.timer_color, background=self.timer_bg_color)
            self.timer2_label.config(text="0.000",
                                     font=(self.timer2_font_family, self.timer2_font_size),
                                     foreground=self.timer2_color, background=self.timer2_bg_color)
            self.start_stop_button.config(text="Стоп (Пробел)")

            # Запускаем таймеры
            if self.timer_after_id:
                self.root.after_cancel(self.timer_after_id)
            self.timer_after_id = self.root.after(10, self.update_timer)
            if self.timer2_after_id:
                self.root.after_cancel(self.timer2_after_id)
            self.timer2_after_id = self.root.after(10, self.update_timer2)

            if self.after_id:
                self.root.after_cancel(self.after_id)
            self.after_id = self.root.after(500, self.generate_table)
        except Exception as e:
            self.log_event("error", "start_session", f"Ошибка при начале сессии: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось начать сессию: {str(e)}")
            self.timer_running = False
            self.start_stop_button.config(text="Старт (Пробел)")

    def reset_table(self):
        """Обновляет таблицу"""
        if self.is_closing:
            return
        try:
            self.log_event("action", "reset_table", "Обновление таблицы")
            self.rows = min(max(self.rows_var.get(), 3), 10)
            self.cols = min(max(self.cols_var.get(), 3), 10)
            self.rows_var.set(self.rows)
            self.cols_var.set(self.cols)
            if self.timer_running:
                self.stop_session(save_stats=False)
            self.apply_settings()
            if self.after_id:
                self.root.after_cancel(self.after_id)
            self.after_id = self.root.after(500, self.generate_table)
        except Exception as e:
            self.log_event("error", "reset_table", f"Ошибка при обновлении таблицы: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось обновить таблицу: {str(e)}")

    def generate_table(self):
        """Генерирует таблицу"""
        if self.is_closing or self.generating_table:
            self.log_event("action", "generate_table", "Пропуск генерации таблицы: приложение закрывается или генерация уже выполняется")
            return
        self.generating_table = True
        try:
            self.log_event("action", "generate_table", f"Генерация таблицы {self.rows}x{self.cols}")
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            self.buttons = []

            numbers = list(range(1, self.rows * self.cols + 1))
            random.shuffle(numbers)

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

            # Вычисляем доступное пространство
            canvas_width = self.table_canvas.winfo_width()
            canvas_height = self.table_canvas.winfo_height()
            self.log_event("action", "generate_table", f"Размеры canvas: ширина={canvas_width}, высота={canvas_height}")
            if canvas_width <= 1:
                canvas_width = self.root.winfo_width() - 50
                self.log_event("action", "generate_table", "Используется ширина окна по умолчанию")
            if canvas_height <= 1:
                canvas_height = self.root.winfo_height() - 200
                self.log_event("action", "generate_table", "Используется высота окна по умолчанию")

            # Вычисляем размеры ячеек, чтобы вписаться в пространство
            cell_width = min(self.cell_min_width, canvas_width // self.cols)
            cell_height = min(self.cell_min_height, canvas_height // self.rows)

            for i in range(self.rows):
                self.scrollable_frame.rowconfigure(i, weight=1, minsize=cell_height)
                for j in range(self.cols):
                    self.scrollable_frame.columnconfigure(j, weight=1, minsize=cell_width)

                    number = numbers.pop()
                    btn = ttk.Button(
                        self.scrollable_frame,
                        text=str(number),
                        style="Table.TButton",
                        command=lambda n=number: self.cell_clicked(n)
                    )

                    btn.bind("<Enter>", lambda e, n=number: self.cell_hover(n))
                    btn.bind("<Leave>", lambda e: self.cell_leave())

                    btn.grid(row=i, column=j, sticky="nsew", padx=2, pady=2)
                    self.buttons.append(btn)

            # Проверяем необходимость скроллбаров
            total_width = self.cols * cell_width
            total_height = self.rows * cell_height

            if total_width > canvas_width:
                self.h_scrollbar.pack(side="bottom", fill="x")
            else:
                self.h_scrollbar.pack_forget()

            if total_height > canvas_height:
                self.v_scrollbar.pack(side="right", fill="y")
            else:
                self.v_scrollbar.pack_forget()

            self.highlight_center_cells()
            self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all"))
            self.last_click_time = time.time()
        except Exception as e:
            self.log_event("error", "generate_table", f"Ошибка при создании таблицы: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось создать таблицу: {str(e)}")
            self.stop_session()
        finally:
            self.generating_table = False
            if self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None

    def highlight_center_cells(self):
        """Выделяет центральные ячейки"""
        if self.is_closing:
            return
        try:
            center_row1 = self.rows // 2
            center_row2 = center_row1 if self.rows % 2 == 1 else center_row1 - 1
            center_col1 = self.cols // 2
            center_col2 = center_col1 if self.cols % 2 == 1 else center_col1 - 1

            for i in range(center_row2, center_row1 + 1):
                for j in range(center_col2, center_col1 + 1):
                    for btn in self.buttons:
                        if btn.grid_info()["row"] == i and btn.grid_info()["column"] == j:
                            btn.config(style="Highlight.TButton")
        except Exception as e:
            self.log_event("error", "highlight_center_cells", f"Ошибка при выделении центральных ячеек: {str(e)}")

    def cell_hover(self, number):
        """Обрабатывает наведение на ячейку"""
        if self.is_closing:
            return
        try:
            if not self.timer_running or not self.hover_mode:
                return

            if number == self.current_number:
                self.current_number += 1
                self.correct_hovers += 1
                self.clicks_counter.config(text=str(self.current_number))
                if self.current_number > self.rows * self.cols:
                    self.current_number = 0
                    self.clicks_counter.config(text=str(self.current_number))
                    self.stop_session()

                for btn in self.buttons:
                    if btn.cget("text") == str(number):
                        btn.config(style="Active.TButton")
        except Exception as e:
            self.log_event("error", "cell_hover", f"Ошибка при наведении на ячейку {number}: {str(e)}")

    def cell_clicked(self, number):
        """Обрабатывает клик по ячейке"""
        if self.is_closing:
            return
        try:
            self.log_event("action", "cell_clicked", f"Клик по ячейке с номером {number}")
            if not self.timer_running or (not self.click_refresh_mode and not self.click_no_refresh_mode and not self.simple_mode):
                return

            if number == self.current_number:
                self.current_number += 1
                self.correct_clicks += 1
                self.clicks_counter.config(text=str(self.current_number))
                if self.current_number > self.rows * self.cols:
                    self.current_number = 0
                    self.clicks_counter.config(text=str(self.current_number))
                    self.stop_session()

                if self.click_refresh_mode or self.simple_mode:
                    current_time = time.time()
                    time_diff = current_time - self.last_click_time
                    self.last_click_time = current_time
                    self.session_data.append(time_diff)

                for btn in self.buttons:
                    if btn.cget("text") == str(number):
                        btn.config(style="Active.TButton")

                if self.click_refresh_mode and not self.simple_mode:
                    if self.after_id:
                        self.root.after_cancel(self.after_id)
                    self.after_id = self.root.after(500, self.generate_table)
        except Exception as e:
            self.log_event("error", "cell_clicked", f"Ошибка при клике по ячейке {number}: {str(e)}")

    def cell_leave(self):
        """Обрабатывает уход курсора с ячейки"""
        if self.is_closing:
            return
        try:
            for btn in self.buttons:
                if btn.cget("style") == "Active.TButton":
                    btn.config(style="Table.TButton")
        except Exception as e:
            self.log_event("error", "cell_leave", f"Ошибка при уходе с ячейки: {str(e)}")

    def stop_session(self, save_stats=True):
        """Завершает сессию"""
        if self.is_closing:
            return
        try:
            self.log_event("action", "stop_session", f"Завершение сессии, сохранение статистики: {save_stats}")
            self.timer_running = False
            self.start_stop_button.config(text="Старт (Пробел)")
            if self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None
            if self.timer_after_id:
                self.root.after_cancel(self.timer_after_id)
                self.timer_after_id = None
            if self.timer2_after_id:
                self.root.after_cancel(self.timer2_after_id)
                self.timer2_after_id = None

            if save_stats and self.session_start_time:
                session_time = time.time() - self.session_start_time
                if self.simple_mode:
                    avg_time = session_time / (self.rows * self.cols) if (self.rows * self.cols) > 0 else 0
                else:
                    avg_time = sum(self.session_data) / len(self.session_data) if self.session_data else 0

                mode = self.game_mode_var.get()
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
                    "mode": mode
                })

                self.save_stats()
                self.show_stats()
        except Exception as e:
            self.log_event("error", "stop_session", f"Ошибка при завершении сессии: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось завершить сессию: {str(e)}")

    def show_stats(self):
        """Отображает статистику"""
        if self.is_closing:
            return
        try:
            for widget in self.stats_frame.winfo_children():
                widget.destroy()

            if not self.current_user or self.current_user not in self.stats:
                ttk.Label(self.stats_frame, text="Нет данных для отображения").pack()
                return

            user_stats = self.stats[self.current_user]
            if not user_stats:
                ttk.Label(self.stats_frame, text="Нет данных для отображения").pack()
                return

            graph_frame = ttk.Frame(self.stats_frame)
            graph_frame.pack(fill=tk.BOTH, expand=True)

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

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
                modes.append(session.get("mode", "click_refresh"))
                clicks.append(session.get("correct_clicks", 0))
                hovers.append(session.get("correct_hovers", 0))

            ax1.plot(dates, avg_times, 'o-')
            ax1.set_title(f"Среднее время на ячейку для {self.current_user}")
            ax1.set_ylabel("Время (сек)")
            ax1.grid(True)

            ax2.plot(dates, clicks, 'o-', label='Правильные нажатия')
            ax2.plot(dates, hovers, 's-', label='Правильные наведения')
            ax2.set_title("Результаты по режимам")
            ax2.set_ylabel("Количество")
            ax2.legend()
            ax2.grid(True)

            for ax in [ax1, ax2]:
                plt.sca(ax)
                plt.xticks(rotation=45)

            plt.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

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
                    session.get("mode", "click_refresh"),
                    f"{session['total_time']:.1f} сек",
                    session.get("correct_clicks", 0),
                    session.get("correct_hovers", 0)
                ))

            scrollbar = ttk.Scrollbar(self.stats_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)

            tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
        except Exception as e:
            self.log_event("error", "show_stats", f"Ошибка при отображении статистики: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось отобразить статистику: {str(e)}")

    def load_stats(self):
        """Загружает статистику"""
        if self.is_closing:
            return
        try:
            if os.path.exists("schulte_stats.json"):
                with open("schulte_stats.json", "r", encoding="utf-8") as f:
                    self.stats = json.load(f)
            else:
                self.stats = {}
        except Exception as e:
            self.log_event("error", "load_stats", f"Ошибка при загрузке статистики: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить статистику: {str(e)}")
            self.stats = {}

    def save_stats(self):
        """Сохраняет статистику"""
        if self.is_closing:
            return
        try:
            with open("schulte_stats.json", "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log_event("error", "save_stats", f"Ошибка при сохранении статистики: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить статистику: {str(e)}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        style = ttk.Style()
        style.theme_use('clam')

        app = SchulteTableApp(root)
        app.logging_enabled = True
        root.mainloop()
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")