import json
import sys
from datastructures import Article, Order
from algorithm import distribute_orders
from test_solution import check_solution
import os

# TODO: Docker
# TODO: order_to_batches cleanup
# TODO: Readmes für Unterordner


def main(argv):

    # check if main.py is called with the required arguments
    try:
        instance_path = os.path.join("instances", argv[1])
        solution_path = os.path.join("solution", argv[2])
    except IndexError:
        raise ValueError('instance_path and/or solution_path is missing.')

    # check if the solution directory exists before importing the problem instance and calculating a solution
    solution_dir, _ = os.path.split(solution_path)
    if solution_dir and not os.path.isdir(solution_dir):
        raise FileNotFoundError(f'Solution dir {solution_dir} does not exist.')

    # load the problem instance
    with open(instance_path) as file:
        data = json.load(file)

    # articles_id_mapping: dict with key: article_id and value: Article instance
    # orders: set of all Order instances
    articles_id_mapping, orders = {}, set()

    # create Article instances from data and save it to articles_id_mapping
    for article in data['Articles']:
        articles_id_mapping[article['ArticleId']] = Article(
            article_id=article['ArticleId'], volume=article['Volume']
        )

    # get article locations from data and save locations in Article instances from articles_id_mapping
    for article_location in data['ArticleLocations']:
        article = articles_id_mapping[article_location['ArticleId']]
        article.warehouse_id = article_location['Warehouse']
        article.aisle_id = article_location['Aisle']

    # create Order instances from data and save it to orders
    for order in data['Orders']:
        articles = [articles_id_mapping[article_id] for article_id in order['ArticleIds']]
        orders.add(Order(
            order_id=order['OrderId'], articles=articles
        ))

    # cast Order.all_warehouse_ids to a list after all orders are instantiated (see Order.cast_all_warehouse_ids_attr
    # documentation)
    Order.cast_all_warehouse_ids_attr()

    # calculate the solution dict
    solution = distribute_orders(orders, articles_id_mapping)

    # Solution test function which checks logical correctness and calculates costs.
    # check_solution(solution, articles_id_mapping, data["Orders"])

    # save solution dict to solution_path
    if os.path.exists(solution_path):
        os.remove(solution_path)

    with open(solution_path, 'x') as file:
        json.dump(solution, file)


if __name__ == "__main__":
    main(argv=sys.argv)
