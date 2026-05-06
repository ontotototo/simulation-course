import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import random

class ContinuousWeatherEngine:
    def __init__(self):
        self.q_matrix = np.zeros((3, 3))
        self.states = {1: 'Ясно', 2: 'Облачно', 3: 'Пасмурно'}
        self.current_state = 1
        self.daily_chronology = [] 
        self.total_hours_history = {1: 0.0, 2: 0.0, 3: 0.0}
        self.convergence_history = [] 
        self.is_initialized = False

    def is_empty(self):
        return np.all(self.q_matrix == 0)

    def set_intensities(self, row_idx, col_idx, value):
        self.q_matrix[row_idx, col_idx] = value
        # Пересчет диагонали
        row_sum = np.sum(self.q_matrix[row_idx]) - self.q_matrix[row_idx, row_idx]
        self.q_matrix[row_idx, row_idx] = -row_sum

    def step(self):
        if self.is_empty(): return False
        if not self.is_initialized:
            theo = self.get_stationary_distribution()
            self.current_state = np.random.choice([1, 2, 3], p=theo) #  начальное состояние случайно, основываясь на теоретических вероятностях
            self.is_initialized = True

        hours_left = 24.0
        this_day_events = []
        
        while hours_left > 0:
            lambda_out = abs(self.q_matrix[self.current_state-1, self.current_state-1]) # интенсивность выхода 
            wait_time = random.expovariate(lambda_out) if lambda_out > 1e-9 else 24.0 #  переход по экспоненциальному закону
            actual_duration = min(wait_time, hours_left)
            
            this_day_events.append((self.current_state, actual_duration))
            self.total_hours_history[self.current_state] += actual_duration
            hours_left -= actual_duration
            
            if wait_time < (hours_left + actual_duration):
                row = np.copy(self.q_matrix[self.current_state-1])
                row[self.current_state-1] = 0
                sum_row = row.sum()
                if sum_row > 0:
                    probs = row / sum_row # Вероятности перехода в другие состояния (qij/qii)
                    self.current_state = np.random.choice([1, 2, 3], p=probs)
        
        self.daily_chronology.append(this_day_events)
        
        # Считаем текущие доли времени для сходимости
        total_h = sum(self.total_hours_history.values())
        self.convergence_history.append([self.total_hours_history[i]/total_h for i in [1, 2, 3]])
        return True

    def get_stationary_distribution(self):
        if self.is_empty(): return np.array([0.33, 0.33, 0.34])
        try:
            Q = self.q_matrix.T
            Q[-1, :] = 1 # заменяет всю последнюю строку в транспонированной матрице единицами для ед решения
            rhs = np.zeros(3); rhs[-1] = 1 # вектор свободных [0,0,1]
            return np.linalg.solve(Q, rhs)
        except: return np.array([0.33, 0.33, 0.34])

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Analysis Pro")
        self.engine = ContinuousWeatherEngine()
        self.is_running = False
        self.colors = {1: '#FFD700', 2: '#B0C4DE', 3: '#708090'}
        self._setup_ui()
        self._setup_plots()
        self._loop()

    def _setup_ui(self):
        side = ttk.Frame(self.root, padding="15")
        side.pack(side=tk.LEFT, fill=tk.Y)
        
        ttk.Label(side, text="МАТРИЦА Q", font=('Arial', 10, 'bold')).pack()
        self.m_frame = ttk.Frame(side); self.m_frame.pack(pady=5)
        self._fill_matrix_entries()
        
        ttk.Separator(side).pack(fill=tk.X, pady=10)
        ttk.Label(side, text="Дней в окне:").pack()
        self.days_entry = ttk.Entry(side, width=15); self.days_entry.insert(0, "65"); self.days_entry.pack()
        
        ttk.Button(side, text="Смоделировать", command=self._run_batch).pack(fill=tk.X, pady=2)
        self.btn_start = ttk.Button(side, text="▶ Старт", command=self._toggle); self.btn_start.pack(fill=tk.X)
        ttk.Button(side, text="🔄 Сброс", command=self._reset).pack(fill=tk.X, pady=2)
        ttk.Button(side, text="📥 Экспорт в CSV", command=self._export_csv).pack(fill=tk.X, pady=5)
        
        self.info_box = tk.Text(side, height=6, width=30, font=('Courier', 9)); self.info_box.pack()

    def _fill_matrix_entries(self):
        for widget in self.m_frame.winfo_children(): widget.destroy()
        self.entries = {}
        for i in range(3):
            for j in range(3):
                ent = ttk.Entry(self.m_frame, width=7, justify='center')
                ent.grid(row=i, column=j, padx=2, pady=2)
                if i == j: 
                    ent.config(state='readonly', foreground='red')
                    ent.insert(0, "0.00")
                else: 
                    ent.bind('<KeyRelease>', lambda e, r=i, c=j: self._on_input(r, c))
                self.entries[(i, j)] = ent

    def _on_input(self, r, c):
        try:
            val = float(self.entries[(r,c)].get() or 0)
            self.engine.set_intensities(r, c, val)
            # Сразу обновляем диагональ
            diag_val = self.engine.q_matrix[r, r]
            self.entries[(r,r)].config(state='normal')
            self.entries[(r,r)].delete(0, tk.END); self.entries[(r,r)].insert(0, f"{diag_val:.2f}")
            self.entries[(r,r)].config(state='readonly')
        except: pass

    def _export_csv(self):
        if not self.engine.daily_chronology: return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if path:
            data = []
            for i, day in enumerate(self.engine.daily_chronology):
                row = {'day': i+1, 'Ясно': 0, 'Облачно': 0, 'Пасмурно': 0}
                for state, dur in day:
                    row[self.engine.states[state]] += dur
                data.append(row)
            pd.DataFrame(data).to_csv(path, index=False)
            messagebox.showinfo("Готово", "Данные успешно экспортированы!")

    def _toggle(self):
        if self.engine.is_empty(): return
        self.is_running = not self.is_running
        self.btn_start.config(text="⏸ Стоп" if self.is_running else "▶ Старт")

    def _reset(self):
        self.is_running = False
        self.engine = ContinuousWeatherEngine()
        self._fill_matrix_entries()
        self.ax1.clear(); self.ax2.clear(); self.canvas.draw()

    def _run_batch(self):
        try:
            for _ in range(int(self.days_entry.get())): self.engine.step()
            self._refresh()
        except: pass

    def _loop(self):
        if self.is_running: self.engine.step(); self._refresh()
        self.root.after(100, self._loop)

    def _setup_plots(self):
        self.fig = Figure(figsize=(9, 8)); self.canvas = FigureCanvasTkAgg(self.fig, self.root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.ax1 = self.fig.add_subplot(211); self.ax2 = self.fig.add_subplot(212)

    def _refresh(self):
        if not self.engine.daily_chronology: return
        self.ax1.clear(); self.ax2.clear()
        
        limit = int(self.days_entry.get() or 65)
        history = self.engine.daily_chronology
        view_data = history[-limit:]
        
        # 1. Хронология дня
        for i, day_events in enumerate(view_data):
            bottom = 0
            day_idx = len(history) - len(view_data) + i + 1
            for state, duration in day_events:
                self.ax1.bar(day_idx, duration, bottom=bottom, color=self.colors[state], width=0.8)
                bottom += duration
        self.ax1.set_title("Детальная хронология погоды")
        self.ax1.set_xlabel("Номер дня")
        self.ax1.set_ylabel("Часы суток (0-24)")
        self.ax1.set_ylim(0, 24)
        self.ax1.set_title("Хронология погоды (часы)"); self.ax1.set_ylim(0, 24)

        # 2. Сходимость
        conv = np.array(self.engine.convergence_history)
        theo = self.engine.get_stationary_distribution()
        x_axis = np.arange(1, len(conv) + 1)
        
        for i, state_name in enumerate(['Ясно', 'Облачно', 'Пасмурно']):
            color = self.colors[i+1]
            # Факт
            self.ax2.plot(x_axis, conv[:, i], color=color, label=f"Факт: {state_name}")
            # Теория (пунктир)
            self.ax2.axhline(y=theo[i], color=color, linestyle='--', alpha=0.6)

        self.ax2.set_title("Сходимость к стационарному распределению")
        self.ax2.set_ylabel("Доля времени"); self.ax2.set_xlabel("Дни")
        self.ax2.legend(loc='upper right', fontsize='x-small')
        
        self.fig.tight_layout(); self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk(); app = WeatherApp(root); root.mainloop()