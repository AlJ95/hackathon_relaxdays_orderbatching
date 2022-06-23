import json


def get_location(data, article_id):
    article = [article for article in data if article["article_id"] == article_id][-1]
    return article["Warehouse"], article["Aisle"]


def get_weight():
    pass


if __name__ == "__main__":
    with open("data/instance.json") as file:
        data = json.load(file)

    article_locations = data["ArticleLocations"]
    orders = data["Orders"]
    articles = data["Articles"]


