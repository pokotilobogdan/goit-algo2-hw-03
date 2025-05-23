from BTrees.OOBTree import OOBTree
from timeit import timeit
import csv
from random import randint


def add_item_to_tree(tree: OOBTree, filepath: str):
    with open(filepath) as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        for row in reader:
            tree.update({int(row[0]): {headers[1]: row[1], headers[2]: row[2], headers[3]: float(row[3])}})     # Не сильно паримось

def add_item_to_dict(d: dict, filepath: str):
    with open(filepath) as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        for row in reader:
            d.update({int(row[0]): {headers[1]: row[1], headers[2]: row[2], headers[3]: float(row[3])}})        # Тут також

# Для зручності, нашим діапазонним запитом буде сумарна вартість продуктів від продукта А до продукта В
def range_query_tree(tree: OOBTree, a: int, b: int):
    sum = 0
    for _, value in tree.items(a, b):     # Тут від a до b включно
        sum += value['Price']
    return sum

def range_query_dict(d: dict, a: int, b: int):
    sum = 0
    for key in range(a, b+1):
        sum += d[key]['Price']
    return sum


if __name__ == '__main__':

    # Створення порожніх OOBTree та словника
    tree = OOBTree()
    d = dict()

    csv_path = 'generated_items_data.csv'

    # Заповнюємо все даними з csv-таблиці
    add_item_to_tree(tree, csv_path)
    add_item_to_dict(d, csv_path)

    # Швиденька перевірка, що при діапазонному запиті сумарна вартість виходить однаковою:
    print(range_query_tree(tree, 1, 3))     # 803.4799999999999
    print(range_query_dict(d, 1, 3))        # 803.4799999999999

    # Тепер можна порівнювати швидкодійність BTree та словника
    
    sum_time_tree = 0
    sum_time_dict = 0
    
    min_key = tree.minKey()     # 1
    max_key = tree.maxKey()     # 100000

    for _ in range(100):
        ar, br = randint(min_key, max_key), randint(min_key, max_key)
        a, b = min(ar,br), max(ar,br)
        sum_time_tree += timeit(stmt=f'{range_query_tree(tree, a, b)}', number=1)
        sum_time_dict += timeit(stmt=f'{range_query_dict(d, a, b)}', number=1)

    print()
    print('Total range_query time for OOBTree:', sum_time_tree, 'seconds')   # 3.9999838918447495e-05
    print('Total range_query time for Dict:', sum_time_dict, 'seconds')   # 5.120015703141689e-05

    # BTree дійсно впоралось швидше за рахунок впорядкованої структури даних
    