# import random
#
# random.seed(42)
#
# for _ in range(15):
#     number1 = random.random() * 0.02 + 0.8911111111111111
#     number2 = random.uniform(0.8911111111111111, 0.9111111111111111)
#     print(f'{round(number1, 2)}\t\t{round(number2, 2)}')

import random


l = 2
m = 3
n = 4
# Задаем quantity, gross_weight, price_per_kg
quantity = random.randrange(0, 100, 10)  # (КОЛ-ВО)
# quantity = 70
gross_weight = random.randint(1, 101)  # (БР)
# gross_weight = 40
price_per_kg = 8.02  # ($/КГ)

# Рассчитываем net_weight
random.seed(42)
min_coeff = 0.8911111111111111
max_coeff = 0.9111111111111111
coeff = random.uniform(min_coeff, max_coeff)
net_weight = gross_weight * coeff  # (НТ)
net_weight = round(net_weight, n)

# Рассчитываем price
price = price_per_kg * net_weight  # (ЦЕНА)
price = round(price, n)

# Рассчитываем new_price
new_price = round(price / quantity, 2) * quantity  # (новая ЦЕНА)
new_price = round(new_price, n)

# Рассчитываем weight_per_unit
weight_per_unit = net_weight / quantity  # (ВЕС ШТ)

# Результаты ДО
print(f'КОЛ-ВО: {quantity}')
print(f'БР: {round(gross_weight, 2)}')
print(f'НТ: {round(net_weight, 2)}')
print(f'ВЕС ШТ: {round(weight_per_unit, 3)}')
print(f'$/КГ: {price_per_kg}')
print(f'ЦЕНА: {round(price, 2)}')
print(f'new_ЦЕНА: {round(new_price, 2)}\n')


# Обновление веса нетто и повторный расчет
def recalculate_net_weight():
    global net_weight, price, new_price

    net_weight = round(net_weight, n)

    price = price_per_kg * net_weight  # (ЦЕНА)
    price = round(price, n)

    new_price = round(price / quantity, 2) * quantity  # (новая ЦЕНА)
    new_price = round(new_price, n)

    weight_per_kg = round(price / net_weight, m)
    new_weight_per_kg = round(new_price / net_weight, m)

    if round(weight_per_kg, m) > round(new_weight_per_kg, m):
        net_weight -= 0.001111111
        print(f'{round(price, l)} > {round(new_price, l)}')
        print(f'{round(weight_per_kg, m)} > {round(new_weight_per_kg, m)}')
    elif round(weight_per_kg, m) < round(new_weight_per_kg, m):
        net_weight += 0.001111111
        print(f'{round(price, l)} < {round(new_price, l)}')
        print(f'{round(weight_per_kg, m)} < {round(new_weight_per_kg, m)}')
    else:
        print(f'\nГотово!')
        print(f'{round(price, 2)}')
        print(f'{new_weight_per_kg}')



# Перерасчёт, пока price не станет равен new_price
num_iterations = 0
while round(price / net_weight, m) != round(new_price / net_weight, m):
    recalculate_net_weight()
    num_iterations += 1

# price = new_price  # (ЦЕНА)
weight_per_unit = net_weight / quantity  # (ВЕС ШТ)

# Округление
gross_weight = round(gross_weight, 2)
net_weight = round(net_weight, 2)
weight_per_unit = round(weight_per_unit, 3)
price = round(price, 2)

# Результаты ПОСЛЕ
print(f'\nПовторений: {num_iterations}\n')
print(f'КОЛ-ВО: {quantity}')
print(f'БР: {gross_weight}')
print(f'НТ: {net_weight}')
print(f'ВЕС ШТ: {weight_per_unit}')
print(f'$/КГ: {price_per_kg}')
print(f'ЦЕНА: {price}')
