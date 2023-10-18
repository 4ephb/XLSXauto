# import random
#
# random.seed(42)
#
# for _ in range(15):
#     number1 = random.random() * 0.02 + 0.8911111111111111
#     number2 = random.uniform(0.8911111111111111, 0.9111111111111111)
#     print(f'{round(number1, 2)}\t\t{round(number2, 2)}')

# import random
#
# l = 2
# m = 3
# n = 4
#
# # Задаем quantity, gross_weight, price_per_kg
# price_per_kg = 8.02  # ($/КГ)
# # quantity = 90
# # gross_weight = 69
# quantity = random.randrange(0, 1000, 100)  # (КОЛ-ВО)
# gross_weight = random.randint(1, 101)  # (БР)
#
# # Рассчитываем net_weight
# random.seed(42)
# min_coeff = 0.89111  # 11111111111
# max_coeff = 0.91111  # 11111111111
# coeff = round(random.uniform(min_coeff, max_coeff), 5)
# net_weight = gross_weight * coeff  # (НТ)
# # net_weight = round(net_weight, n)
#
# # Рассчитываем price
# price = price_per_kg * net_weight  # (ЦЕНА)
# price = round(price, l)
#
# # Рассчитываем new_price
# new_price = round(price / quantity, l) * quantity  # (новая ЦЕНА)
# new_price = round(new_price, l)
#
# # Рассчитываем new_net_weight
# new_net_weight = new_price / price_per_kg
# new_net_weight = round(new_net_weight, l)
#
# # Рассчитываем weight_per_unit
# weight_per_unit = net_weight / quantity  # (ВЕС ШТ)
#
# # Рассчитываем new_weight_per_unit
# new_weight_per_unit = new_net_weight / quantity
#
# # Рассчитываем price_per_unit
# price_per_unit = price / quantity
#
# # Рассчитываем new_price_per_unit
# new_price_per_unit = new_price / quantity
#
# # Результаты ДО
# print(f'$/КГ: {price_per_kg}')
# print(f'КОЛ-ВО: {quantity}')
# print(f'БР: {gross_weight}')
# print(f'НТ = {gross_weight} * {coeff} = {round(net_weight, 2)}   ==>   {new_net_weight}')
# print(f'ВЕС ШТ = {round(net_weight, 2)} / {quantity} = {round(weight_per_unit, 3)}   ==>   {round(new_weight_per_unit, 3)}')
# print(f'ЦЕНА = {round(net_weight, 2)} * {price_per_kg} = {round(price, 2)}   ==>   {round(new_price, 2)}')
# print(f'$/ШТ = {round(price, 2)} / {quantity} = {round(price_per_unit, l)}   ==>   {round(new_price_per_unit, l)}')
#
#
# # Обновление веса нетто и повторный расчет
# def recalculate_net_weight():
#     global net_weight, price, new_price
#
#     price_kg = round(price / net_weight, n)
#     new_price_kg = round(new_price / net_weight, n)
#
#     if round(price_kg, n) > round(new_price_kg, n):
#         net_weight -= 0.001
#         # print(f'{round(price, l)} > {round(new_price, l)}')
#         # print(f'{round(price_kg, l)} > {round(new_price_kg, l)}')
#     elif round(price_kg, n) < round(new_price_kg, n):
#         net_weight += 0.001
#         # print(f'{round(price, l)} < {round(new_price, l)}')
#         # print(f'{round(price_kg, l)} < {round(new_price_kg, l)}')
#     else:
#         print(f'\nГотово!')
#         print(f'{round(price, 2)}')
#         print(f'{new_price_kg}')
#
#     net_weight = round(net_weight, n)
#
#     price = price_per_kg * net_weight  # (ЦЕНА)
#     price = round(price, l)
#
#     new_price = round(price / quantity, l) * quantity  # (новая ЦЕНА)
#     new_price = round(new_price, l)
#
#
# # Перерасчёт, пока price не станет равен new_price
# num_iterations = 0
# while round(price / net_weight, n) != round(new_price / net_weight, n):
#     recalculate_net_weight()
#     num_iterations += 1
#
# print(f'\nПовторений: {num_iterations}\n')
#
# # price = new_price  # (ЦЕНА)
# weight_per_unit = net_weight / quantity  # (ВЕС ШТ)
#
# # Округление
# gross_weight = round(gross_weight, 2)
# net_weight = round(net_weight, 2)
# weight_per_unit = round(weight_per_unit, 3)
# price = round(price, 2)
# price_per_unit = round(price_per_unit, 2)
#
# # Результаты ПОСЛЕ
# print(f'$/КГ: {price_per_kg}')
# print(f'КОЛ-ВО: {quantity}')
# print(f'БР: {gross_weight}')
# print(f'НТ: {net_weight}')
# print(f'ВЕС ШТ: {weight_per_unit}')
# print(f'ЦЕНА: {price}')
# print(f'$/ШТ: {price_per_unit}')

import random

# Задаем quantity, gross_weight, price_per_kg
price_per_kg = 8.02  # ($/КГ)
# quantity = 500  # (КОЛ-ВО)
# gross_weight = 23  # (БР)
quantity = random.randrange(0, 1000, 100)  # (КОЛ-ВО)
gross_weight = random.randint(1, 101)  # (БР)

# Рассчитываем предварительный net_weight
random.seed(42)
min_coeff = 0.8911  # 111111111111
max_coeff = 0.9111  # 111111111111
coeff = round(random.uniform(min_coeff, max_coeff), 4)
net_weight = gross_weight * coeff  # (НТ)

# Рассчитываем price
price = price_per_kg * net_weight  # (ЦЕНА)
price = round(price / quantity, 2) * quantity  # новая (ЦЕНА)

# Рассчитываем итоговый net_weight
net_weight = price / price_per_kg  # (НТ)

# Рассчитываем итоговый coeff
coeff = net_weight / gross_weight

# Рассчитываем weight_per_unit
weight_per_unit = net_weight / quantity  # (ВЕС ШТ)

# Рассчитываем price_per_unit
price_per_unit = price / quantity

# Округление
gross_weight = round(gross_weight, 2)
net_weight = round(net_weight, 2)
weight_per_unit = round(weight_per_unit, 3)
price = round(price, 2)
price_per_unit = round(price_per_unit, 2)
coeff = round(coeff, 4)

# Результаты
print(f'$/КГ: {price_per_kg}')
print(f'КОЛ-ВО: {quantity}')
print(f'БР: {gross_weight}')
print(f'НТ =\t\t{gross_weight} * {coeff}\t\t= {net_weight}')
print(f'ВЕС ШТ =\t{net_weight} / {quantity}\t\t= {weight_per_unit}')
print(f'ЦЕНА =\t\t{net_weight} * {price_per_kg}\t= {price}')
print(f'$/ШТ =\t\t{price} / {quantity}\t\t= {price_per_unit}')
