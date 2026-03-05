### Отчет по лабораторной "Метод конечных разностей для уравнения теплопроводности"

**Задание:**  
Реализовать моделирование изменения температуры в пластине на основе одномерного уравнения теплопроводности с использованием метода конечных разностей.
Выполнить моделирование с различными шагами по времени и по пространству.  
Заполнить таблицу значений температуры в центральной точке пластины после 2 секунд модельного времени.

Код программы:
```python
import tkinter as tk
from tkinter import messagebox
import numpy as np
import time

def solve():
    try:
        rho, c, lam = 7800, 460, 50

        L = float(ent_L.get())
        T_init = float(ent_Ti.get())
        T_left = float(ent_Tl.get())
        T_right = float(ent_Tr.get())
        t_limit = float(ent_time.get())
        dt = float(ent_dt.get())
        dx = float(ent_dx.get())

        start = time.time()

        nx = int(round(L / dx)) + 1
        nt = int(t_limit / dt)
        T = np.full(nx, T_init)
        T[0], T[-1] = T_left, T_right

        A = lam / (dx ** 2)
        C = lam / (dx ** 2)
        B = 2 * A + (rho * c) / dt
        

        for _ in range(nt):
            alpha = np.zeros(nx)
            beta = np.zeros(nx)

            alpha[1] = 0
            beta[1] = T_left
            for i in range(1, nx - 1):
                F = -(rho * c / dt) * T[i]
                denom = B - C * alpha[i]
                alpha[i + 1] = A / denom
                beta[i + 1] = (C * beta[i] - F) / denom

            T_new = np.zeros(nx)
            T_new[-1] = T_right
            for i in range(nx - 2, 0, -1):
                T_new[i] = alpha[i + 1] * T_new[i + 1] + beta[i + 1]

            T = T_new
            T[0], T[-1] = T_left, T_right

        res_t.config(text=f"Температура в центре: {T[nx // 2]:.4f} ⁰С")
        res_s.config(text=f"Время расчета: {time.time() - start:.4f} сек")
    except:
        messagebox.showerror("Ошибка", "Проверьте числа в полях")

root = tk.Tk()

def make_row(label):
    f = tk.Frame(root)
    f.pack(fill="x", padx=10, pady=2)
    tk.Label(f, text=label, width=20).pack(side="left")
    e = tk.Entry(f)
    e.pack(side="right")
    return e

ent_L = make_row("Толщина L, м:")
ent_L.insert(0, "0.11")
ent_Ti = make_row("Нач. т., С:")
ent_Ti.insert(0, "20")
ent_Tl = make_row("Т. слева, С:")
ent_Tl.insert(0, "100")
ent_Tr = make_row("Т. справа, С:")
ent_Tr.insert(0, "100")
ent_time = make_row("Общее время, с:")
ent_time.insert(0, "2.0")
ent_dt = make_row("Шаг dt, с:")
ent_dt.insert(0, "0.01")
ent_dx = make_row("Шаг dx, м:")
ent_dx.insert(0, "0.01")

tk.Button(root, text="Расчет", command=solve).pack(pady=10)
res_t = tk.Label(root, text="Температура: -")
res_t.pack()
res_s = tk.Label(root, text="Время: -")
res_s.pack()

root.mainloop()
```
Значения при 2 секундах:

| Шаг по времени, с \ Шаг по пространству, м | 0.1     | 0.01    | 0.001 | 0.0001 |
|-------------------------------------------|---------|---------|-------|--------|
| 0.1 | 100     | 20.0011 | 20    | 20     |
| 0.01 | 100     | 20.0008 | 20    | 20     |
| 0.001 | 100     | 20.0007 | 20    | 20     |
| 0.0001 | 20.0007 | 20      | 20    | 20     |

Вводные параметры (Сталь):
    Начальная температура 20 °C
    Температура на границах 100 °C
    Толщина материала (L): 0.11 м
    Теплопроводность (λ): 50 Вт/(м·К)
    Удельная теплоемкость: 460 Дж/(кг·К)
    Плотность тела (ρ): 7800 кг/м³

Значения при 15 секундах:

| Шаг по времени, с \ Шаг по пространству, м | 0.1 | 0.01   | 0.001 | 0.0001  |
|-------------------------------------------|-----|--------|-------|---------|
| 0.1 | 100 | 21.99  | 21.18 | 21.17   |
| 0.01 | 100 | 21.97  | 21.15 | 21.14   |
| 0.001 | 100 | 21.96  | 21.14 | 21.14   |
| 0.0001 | 100 | 21.969 | 21.14 | 21.1435 |

### Вывод
11 см пластина стали за 2 секунды не изменится Т в центре, сталь не особо теплопроводный материал.
