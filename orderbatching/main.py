import json
import sys
from datastructures import Article, Order
from algorithm import orders_to_waves
import os


def main(argv):

    instance_path = argv[1] if len(argv) > 1 else f"{os.path.dirname(__file__)}/data/instance4.json"
    solution_path = argv[2] if len(argv) > 2 else f"{os.path.dirname(__file__)}/data/solution4.json"

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

    import time
    start_time = time.time()
    print(Order.get_wave())
    print(time.time() - start_time)

    start_time = time.time()
    print(orders_to_waves(orders))
    print(time.time() - start_time)


if __name__ == "__main__":
    main(argv=sys.argv)
