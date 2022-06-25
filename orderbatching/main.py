import json
import sys
from datastructures import Article, Order
from algorithm import distribute_orders
import os

# TODO: Docker
# TODO: Kommentare
# TODO: order_to_batches cleanup
# TODO: Readmes für Unterordner


def main(argv):

    try:
        instance_path = argv[1]
        solution_path = argv[2]
    except IndexError:
        raise ValueError('instance_path and/or solution_path is missing.')

    solution_dir, _ = os.path.split(solution_path)
    if solution_dir and not os.path.isdir(solution_dir):
        raise FileNotFoundError(f'Solution dir {solution_dir} does not exist.')

    with open(instance_path) as file:
        data = json.load(file)

    articles_id_mapping, orders = {}, set()

    for article in data['Articles']:
        articles_id_mapping[article['ArticleId']] = Article(
            article_id=article['ArticleId'], volume=article['Volume']
        )

    for article_location in data['ArticleLocations']:
        article = articles_id_mapping[article_location['ArticleId']]
        article.warehouse_id = article_location['Warehouse']
        article.aisle_id = article_location['Aisle']

    for order in data['Orders']:
        articles = [articles_id_mapping[article_id] for article_id in order['ArticleIds']]
        orders.add(Order(
            order_id=order['OrderId'], articles=articles
        ))

    Order.cast_all_warehouse_ids_attr()

    solution = distribute_orders(orders, articles_id_mapping)

    with open(solution_path, 'x') as file:
        json.dump(solution, file)


if __name__ == "__main__":
    main(argv=sys.argv)
