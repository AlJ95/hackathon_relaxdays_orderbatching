import json
import sys
from datastructures import Article, Order
from algorithm import orders_to_waves


def main(argv):
    """
    instance_path = argv[1] if argv and argv[1] is not None else "data/instance.json"
    solution_path = argv[2] if argv and argv[2] is not None else "data/solution0.json"

    solution_dir, _ = os.path.split(solution_path)
    if not os.path.isdir(solution_dir):
        raise FileNotFoundError(f'Solution dir {solution_dir} does not exist.')
    """

    with open('data/instance.json') as file:
        data = json.load(file)

    articles_id_mapping, orders = {}, []

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
        orders.append(Order(
            order_id=order['OrderId'], articles=articles
        ))

    print(orders_to_waves(orders))


if __name__ == "__main__":
    main(argv=sys.argv)
