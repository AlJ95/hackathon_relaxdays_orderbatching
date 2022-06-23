import json

from datastructures import Article, Order


if __name__ == "__main__":

    with open("data/instance.json") as file:
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
