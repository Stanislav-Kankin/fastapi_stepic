import matplotlib.pyplot as plt


def generate_cost_graph(
        total_paper_costs, total_logistics_costs,
        total_operations_costs, total_license_costs):
    # Данные для графика
    current_kdp_costs = (
        total_paper_costs + total_logistics_costs + total_operations_costs
        )
    kedo_costs = total_license_costs

    # Создание графика
    plt.figure(figsize=(8, 5))  # Уменьшили размер графика
    plt.bar(
        ['Текущий КДП', 'КЭДО от HRlink'],
        [current_kdp_costs, kedo_costs], color=['green', 'blue']
        )
    plt.xlabel('Категории расходов')
    plt.ylabel('Стоимость (руб.)')
    plt.title('Сравнение текущих расходов на КДП и КЭДО от HRlink')
    plt.grid(True)

    # Сохранение графика в файл
    graph_path = 'static/cost_graph.png'
    plt.savefig(graph_path, bbox_inches='tight')  # Убрали лишние отступы
    plt.close()

    return graph_path
