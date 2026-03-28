import random
import math

SEED = 4567
random.seed(SEED)

x0_init = SEED if SEED % 2 != 0 else SEED + 1
x0 = x0_init
m = 2**63
a = 2**32 + 3
N = 10 ** 5

my_data = []
library_data = [random.random() for _ in range(N)]

M1 = 0
M2 = 0

for i in range(N):
    x0 = (x0 * a) % m
    my_data.append(x0/m)
    M1 += x0/m
    M2 += library_data[i]

M1 = M1/N
M2 = M2/N
D1 = D2 = 0
for i in range(N):
    D1 += (my_data[i] - M1) ** 2
    D2 += (library_data[i] - M2) ** 2

D1 = D1/N
D2 = D2/N

teor_mean = 1/2
teor_var = 1/12

print("РЕЗУЛЬТАТЫ ГЕНЕРАЦИИ")
print("Метод", "Среднее", "Дисперсия")
print("Теоретические результаты:", teor_mean, teor_var)
print("Мультипликативный конгруэнтный генератор:", M1, D1)
print("Встроенный генератор:", M2, D2)

print("")
print("СРАВНЕНИЕ С ТЕОРЕТИЧЕСКИМИ ЗНАЧЕНИЯМИ")

diff_mean_LCG = abs(M1 - teor_mean)
diff_var_LCG = abs(D1 - teor_var)
diff_mean_LIB = abs(M2 - teor_mean)
diff_var_LIB = abs(D2 - teor_var)

print("Параметр", "LCG", "Встроенный")
print("Откл. среднее:", diff_mean_LCG, diff_mean_LIB)
print("Откл. дисперсия:", diff_var_LCG, diff_var_LIB)