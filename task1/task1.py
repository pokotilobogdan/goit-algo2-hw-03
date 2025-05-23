import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
from colorama import Fore


# Функція для пошуку збільшуючого шляху (BFS)
def bfs(capacity_matrix, flow_matrix, source, sink, parent):
    visited = [False] * len(capacity_matrix)
    queue = deque([source])
    visited[source] = True

    while queue:
        current_node = queue.popleft()
        
        for neighbor in range(len(capacity_matrix)):
            # Перевірка, чи є залишкова пропускна здатність у каналі
            if not visited[neighbor] and capacity_matrix[current_node][neighbor] - flow_matrix[current_node][neighbor] > 0:
                parent[neighbor] = current_node
                visited[neighbor] = True
                if neighbor == sink:
                    return True
                queue.append(neighbor)
    
    return False

# Основна функція для обчислення максимального потоку
def edmonds_karp(capacity_matrix, source, sink):
    num_nodes = len(capacity_matrix)
    flow_matrix = [[0] * num_nodes for _ in range(num_nodes)]  # Ініціалізуємо матрицю потоку нулем
    parent = [-1] * num_nodes
    max_flow = 0

    # Поки є збільшуючий шлях, додаємо потік
    while bfs(capacity_matrix, flow_matrix, source, sink, parent):
        # Знаходимо мінімальну пропускну здатність уздовж знайденого шляху (вузьке місце)
        path_flow = float('Inf')
        current_node = sink

        while current_node != source:
            previous_node = parent[current_node]
            path_flow = min(path_flow, capacity_matrix[previous_node][current_node] - flow_matrix[previous_node][current_node])
            current_node = previous_node
        
        # Оновлюємо потік уздовж шляху, враховуючи зворотний потік
        current_node = sink
        while current_node != source:
            previous_node = parent[current_node]
            flow_matrix[previous_node][current_node] += path_flow
            flow_matrix[current_node][previous_node] -= path_flow
            current_node = previous_node
        
        # Збільшуємо максимальний потік
        max_flow += path_flow

    return max_flow


if __name__ == "__main__":

    # Створення графа
    G = nx.DiGraph()

    # Маємо задачу з декількома джерелами та декількома приймачами. Це еквівалентно задачі з одним джерелом та одним приймачем,
    # якщо нове джерело під'єднати до старих джерел та старі приймачі приєднати до нового приймача дугами прохідністю 'inf'

    edges = [('Start', 'Terminal 1', float('inf')), ('Start', 'Terminal 2', float('inf'))] + \
        [
        ('Terminal 1', 'Warehouse 1', 25), ('Terminal 1', 'Warehouse 2', 20), ('Terminal 1', 'Warehouse 3', 15),
        ('Terminal 2', 'Warehouse 4', 30), ('Terminal 2', 'Warehouse 2', 10), ('Terminal 2', 'Warehouse 3', 15),
        ('Warehouse 1', 'Market 1', 15), ('Warehouse 1', 'Market 2', 10), ('Warehouse 1', 'Market 3', 20),
        ('Warehouse 2', 'Market 4', 15), ('Warehouse 2', 'Market 5', 10), ('Warehouse 2', 'Market 6', 25), 
        ('Warehouse 3', 'Market 7', 20), ('Warehouse 3', 'Market 8', 15), ('Warehouse 3', 'Market 9', 10), 
        ('Warehouse 4', 'Market 10', 20), ('Warehouse 4', 'Market 11', 10), ('Warehouse 4', 'Market 12', 15), ('Warehouse 4', 'Market 13', 5), ('Warehouse 4', 'Market 14', 10), 
        ] + \
        [(f'Market {i}', 'Finish', float('inf')) for i in range(1, 14+1)]

    G.add_weighted_edges_from(edges)



    ### Це якщо захочеться намалювати граф

    G.nodes['Start']['subset'] = 0
    for node in ['Terminal 1', 'Terminal 2']:
        G.nodes[node]['subset'] = 1
    for node in ['Warehouse 1', 'Warehouse 2', 'Warehouse 3', 'Warehouse 4']:
        G.nodes[node]['subset'] = 2
    for node in [f'Market {i}' for i in range(1, 14+1)]:
        G.nodes[node]['subset'] = 3
    G.nodes['Finish']['subset'] = 4

    # Node positions
    pos = nx.multipartite_layout(G, subset_key='subset')

    nx.draw(G, pos=pos, with_labels=False)

    # Shift labels to the right of each node
    label_pos = {node: (x, y + 0.1) for node, (x, y) in pos.items()}

    # Draw labels at the shifted positions
    nx.draw_networkx_labels(G, label_pos)



    capacity_matrix = nx.adjacency_matrix(G).toarray()
    print()
    print(Fore.YELLOW + "Capacity Matrix:" + Fore.RESET)
    print(capacity_matrix)
    
    # Зручна штука, котра перетворює іменовані вершини на цілі числа, при цьому зберігаючи ім'я вершин в окремому атрибуті
    G = nx.convert_node_labels_to_integers(G, label_attribute='name')


    print()
    print(Fore.YELLOW + "Nodes:" + Fore.RESET)
    for node, attrs in G.nodes(data=True):
        print(node, attrs)

    print()
    print(Fore.GREEN, "Max flow:", edmonds_karp(capacity_matrix, source=0, sink=len(capacity_matrix)-1), Fore.RESET)

    text = Fore.BLUE + '''
Відповідь 115 є доволі логічною, бо можна поглянути хоча б на два значення в схемі:
    - максимально можлива потужність подачі товарів = 115
    - максимально можливий прийом товарів = 200
Вже з цих двох значень можна сказати, що потік в схемі не може бути більший за 115.

Далі, дивимось на те, чи може потік стопоритись на якомусь зі складів:
    - Склад 1: приймає максимум 25 / віддає максимум 45
    - Склад 2: 30/50
    - Склад 3: 30/45
    - Склад 4: 30/60
Тобто склади не переповнюються, і там не відбувається блокування потоку.
А більше в даній схемі потоки ніде й не можуть блокуватись. Це означає, що джерела працюють на максимальну потужність.

Конкретно сказати, як розподіляється потік після кожного зі складів не можна. Кожна з доступних комбінацій все ще є розв'язком задачі.
    ''' + Fore.RESET
        
    print(text)

    plt.show()