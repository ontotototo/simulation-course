import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.stats import poisson
import math
import random
from collections import Counter

class PoissonSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа 8: Пуассоновский поток")
        self.root.geometry("1500x600") 
        self.root.resizable(False, False)

        self.left_frame = tk.Frame(root, bg="#f0f0f0")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.setup_graph()

        self.right_frame = tk.Frame(root, bg="#f0f0f0")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        self.setup_inputs()
        self.setup_logs()

    def setup_inputs(self):
        input_frame = tk.LabelFrame(self.right_frame, text="Параметры", bg="#f0f0f0")
        input_frame.pack(fill=tk.X, pady=5)

        params = [
            ("λ (интенсивность):", "5.0"),
            ("T (длина интервала):", "1.0"),
            ("Время моделирования:", "1000.0") 
        ]
        self.entries = {}
        for i, (label, default) in enumerate(params):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, padx=5, pady=4, sticky="w")
            entry = ttk.Entry(input_frame, width=12)
            entry.insert(0, default)
            entry.grid(row=i, column=1, padx=5, pady=4)
            self.entries[label] = entry

        self.run_btn = ttk.Button(input_frame, text="Запустить", command=self.run_simulation)
        self.run_btn.grid(row=3, column=0, columnspan=2, pady=12, sticky="ew")

    def setup_logs(self):
        log_frame = tk.LabelFrame(self.right_frame, text="Результаты", bg="#f0f0f0")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = tk.Text(log_frame, wrap=tk.WORD, state=tk.DISABLED, 
                                font=("Consolas", 10), bg="#ffffff")
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def setup_graph(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.fig.suptitle("Распределение числа заявок на интервале T", fontsize=12)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.left_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def run_simulation(self):
        try:
            lam = float(self.entries["λ (интенсивность):"].get())
            T = float(self.entries["T (длина интервала):"].get())
            T_sim = float(self.entries["Время моделирования:"].get())

            if lam <= 0 or T <= 0 or T_sim <= T:
                messagebox.showwarning("Внимание", "Проверьте параметры )")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите числа")
            return

        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self.log(f"Параметры: λ={lam}, T={T}, T_sim={T_sim}")
        self.log("Генерация потока...")

        events = []
        t = 0.0
        while t < T_sim:
            alpha = random.random()
            dt = -math.log(alpha) / lam
            t += dt
            if t < T_sim:
                events.append(t)

        total_events = len(events)
        self.log(f"Всего сгенерировано заявок: {total_events}")

        num_inters = int(T_sim // T)
        counts = np.zeros(num_inters, dtype=int)
        
        for ev_time in events:
            idx = int(ev_time // T) # опр в какой интервал попала заявка
            if idx < num_inters:
                counts[idx] += 1

        if num_inters == 0:
            self.log("Ошибка: Время моделирования слишком мало для выбранного T.")
            return

        mean_emp = np.mean(counts)
        var_emp = np.var(counts, ddof=1)
        
        self.log("-" * 30)
        self.log("Статистическая обработка:")
        self.log(f"   Количество интервалов (N): {num_inters}")
        self.log(f"   Среднее E[k]:   {mean_emp:.4f}")
        self.log(f"   Дисперсия D[k]: {var_emp:.4f}")
        self.log("-" * 30)

        self.plot_distribution(counts, lam, T)
        self.canvas.draw()
        self.log("Готово.")

    def plot_distribution(self, counts, lam, T):
        self.ax.clear()
        if len(counts) == 0: return
        
        max_k = int(np.max(counts))
        k_vals = np.arange(0, max_k + 2)

        freq = Counter(counts)
        total = len(counts)
        emp_probs = [freq.get(k, 0) / total for k in k_vals]

        theo_probs = [poisson.pmf(k, lam * T) for k in k_vals]

        self.ax.bar(k_vals, emp_probs, width=0.6, alpha=0.7, label='Эмпирическое', color='#4A90E2')
        self.ax.plot(k_vals, theo_probs, 'o-', color='#E74C3C', linewidth=2, label='Теория (Poisson)')
        
        self.ax.set_xlabel('Число заявок k')
        self.ax.set_ylabel('Вероятность P(k)')
        self.ax.legend(loc='best')
        self.ax.grid(True, alpha=0.3)
        self.fig.tight_layout()

if __name__ == "__main__":
    root = tk.Tk()
    app = PoissonSimulatorApp(root)
    root.mainloop()