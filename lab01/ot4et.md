# Лабораторная работа №1: Моделирование полёта тела в атмосфере

**Студент:** Онтоев Виктор  
**Группа:** 932302

---

## Задание
Реализовать приложение для моделирования полёта тела с учётом сопротивления воздуха. Исследовать влияние шага моделирования на точность результатов.


## Физическая модель
Используется метод Эйлера для численного интегрирования уравнений движения.

**Учитываемые силы:**
1. Сила тяжести: $F_g = m \cdot g$
2. Сила сопротивления воздуха: $F_d = \frac{1}{2} \rho v^2 C_d A$

**Константы:**
- `g = 9.81` м/с² (ускорение свободного падения)
- `rho = 1.225` кг/м³ (плотность воздуха)
- `Cd = 0.47` (коэффициент сопротивления сферы)

## Код программы
```python
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Моделирование полета")
        self.geometry("1200x700")
        
        self.g, self.rho, self.Cd = 9.81, 1.225, 0.47
        self.results, self.colors = [], ['blue', 'red', 'green', 'orange', 'purple']
        
        ctrl = ttk.Frame(self, padding=10)
        ctrl.pack(side=tk.LEFT, fill=tk.Y)
        
        params = [('v0, м/с:', '100'), ('Угол, °:', '45'), ('h0, м:', '0'), 
                  ('Масса, кг:', '1.0'), ('Диаметр, м:', '0.1'), ('Шаг dt, с:', '0.01')]
        self.entries = {}
        for i, (label, default) in enumerate(params):
            ttk.Label(ctrl, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            self.entries[label] = ttk.Entry(ctrl, width=12)
            self.entries[label].grid(row=i, column=1, pady=2)
            self.entries[label].insert(0, default)
        
        ttk.Button(ctrl, text="Запустить", command=self.run).grid(row=6, column=0, columnspan=2, pady=5, sticky=tk.EW)
        ttk.Button(ctrl, text="Серия (1, 0.1...)", command=self.run_series).grid(row=7, column=0, columnspan=2, pady=5, sticky=tk.EW)
        ttk.Button(ctrl, text="Очистить", command=self.clear).grid(row=8, column=0, columnspan=2, pady=5, sticky=tk.EW)

        self.fig, self.ax = plt.subplots(figsize=(7, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.ax.set(xlabel='Дальность, м', ylabel='Высота, м', title='Траектория')
        self.ax.grid(True) 
        
        tbl = ttk.Frame(self, padding=5)
        tbl.pack(side=tk.RIGHT, fill=tk.BOTH)
        cols = ('dt', 'range', 'height', 'velocity')
        self.tree = ttk.Treeview(tbl, columns=cols, show='headings', height=15)
        for c, w in zip(cols, [70, 90, 90, 90]):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack()
        ttk.Button(tbl, text="В консоль", command=self.export).pack(pady=5)
    
    def simulate(self, v0, angle, h0, m, d, dt):
        theta = np.radians(angle)
        x, y = 0, h0
        vx, vy = v0 * np.cos(theta), v0 * np.sin(theta)
        A = np.pi * (d/2)**2
        xs, ys, t = [x], [y], 0
        max_h = y
        
        while y >= 0 and t < 1000:
            v = np.sqrt(vx**2 + vy**2)
            Fd = 0.5 * self.rho * v**2 * self.Cd * A if v > 0 else 0
            ax = -Fd * vx / (m * v) if v > 0 else 0
            ay = -self.g - Fd * vy / (m * v) if v > 0 else -self.g
            vx, vy = vx + ax*dt, vy + ay*dt
            x, y = x + vx*dt, y + vy*dt
            t += dt
            max_h = max(max_h, y)
            xs.append(x)
            ys.append(y)
        
        return {'x': xs, 'y': ys, 'range': x, 'max_height': max_h, 
                'final_velocity': np.sqrt(vx**2 + vy**2), 'dt': dt}
    
    def get_params(self):
        return [float(self.entries[f'{l}'].get()) for l in 
                ['v0, м/с:', 'Угол, °:', 'h0, м:', 'Масса, кг:', 'Диаметр, м:', 'Шаг dt, с:']]
    
    def run(self):
        try:
            v0, angle, h0, m, d, dt = self.get_params()
            r = self.simulate(v0, angle, h0, m, d, dt)
            self.results.append(r)
            c = self.colors[len(self.results) % len(self.colors)]
            self.ax.plot(r['x'], r['y'], c=c, label=f'dt={dt:.4f}', linewidth=1.5)
            self.ax.legend(fontsize=7)
            self.canvas.draw()
            self.tree.insert('', tk.END, values=(f"{dt:.4f}", f"{r['range']:.2f}", 
                                                  f"{r['max_height']:.2f}", f"{r['final_velocity']:.2f}"))
            print(f"dt={dt:.4f}: Дальность={r['range']:.2f}м, H={r['max_height']:.2f}м, V={r['final_velocity']:.2f}м/с")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def run_series(self):
        self.clear()
        try:
            v0, angle, h0, m, d, _ = self.get_params()
            print(f"\n{'Шаг':<10}{'Дальность':<15}{'Высота':<15}{'Скорость':<15}")
            print("-" * 55)
            for dt in [1, 0.1, 0.01, 0.001, 0.0001]:
                r = self.simulate(v0, angle, h0, m, d, dt)
                self.results.append(r)
                c = self.colors[len(self.results) % len(self.colors)]
                self.ax.plot(r['x'], r['y'], c=c, label=f'dt={dt}', linewidth=1.2, alpha=0.7)
                self.tree.insert('', tk.END, values=(f"{dt}", f"{r['range']:.2f}", 
                                                      f"{r['max_height']:.2f}", f"{r['final_velocity']:.2f}"))
                print(f"{dt:<10.4f}{r['range']:<15.2f}{r['max_height']:<15.2f}{r['final_velocity']:<15.2f}")
            self.ax.legend(fontsize=7)
            self.canvas.draw()
            messagebox.showinfo("серия готова")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def clear(self):
        self.ax.clear()
        self.ax.set(xlabel='Дальность, м', ylabel='Высота, м', title='Траектория')
        self.ax.grid(True)  
        self.canvas.draw()
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.results = []
    
    def export(self):
        if not self.results:
            messagebox.showinfo("Инфо", "Нет результатов")
            return
        print(f"\n{'='*60}\n{'РЕЗУЛЬТАТЫ':^60}\n{'='*60}")
        print(f"{'Шаг':<10}{'Дальность':<15}{'Высота':<15}{'Скорость':<15}")
        for r in self.results:
            print(f"{r['dt']:<10.4f}{r['range']:<15.2f}{r['max_height']:<15.2f}{r['final_velocity']:<15.2f}")
        print(f"{'='*60}\nВывод: При уменьшении шага точность растёт. Оптимально: 0.001-0.01 с")

if __name__ == "__main__":
    App().mainloop()
```

Скриншот с несколькими траекториями:

<img width="666" height="719" alt="image" src="https://github.com/ontotototo/simulation-course/blob/main/lab01/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-02-21%20%D0%B2%2001.36.07.png" />

---
Заполненная таблица

|Шаг моделирования, с|1|0.1|0.01|0.001|0.0001|
|-|-|-|-|-|-|
| Дальность полёта, м | 124.94 | 160.31 | 162.59 | 162.88 | 162.90 |
| Максимальная высота, м | 30.33 | 48.06 | 49.87 | 50.05 | 50.07 |
| Скорость в конечной точке, м/с | 29.65 | 35.25 | 35.48 | 35.52 | 35.52 |  
---
### Выводы

1. В ходе лабораторной было реализовано численное моделирование полёта тела в атмосфере. Использован метод Эйлера для интегрирования уравнений движения.

2. На заполненной таблице видно, как существенно отличаются между друг другом только первый и второй шаг(там уже почти достигнут точный результат). Далее результаты выходят практически те же самые. Тем не менее из разницы между первым и вторым измерениями можно сделать вывод, что шаг времени напрямую влияет на точность полученных результатов.

3. При больших шагах (dt ≥ 0.1 с) наблюдается значительная погрешность расчёта из-за накопления ошибки метода Эйлера, имеющего первый порядок точности O(dt). При шаге dt ≤ 0.01 с погрешность становится менее 1%, что приемлемо для учебных расчётов.

4. Для данной задачи оптимальный шаг моделирования составляет dt = 0.001–0.01 с — это обеспечивает баланс между точностью и быстродействием. Для более высокой точности можно использовать методы высших порядков, к примеру Рунге-Кутта 4.





