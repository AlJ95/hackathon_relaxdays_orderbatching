import json

if __name__ == "__main__":
    with open("instance.json") as file:
        data = json.load(file)

    article_locations = data["ArticleLocations"]
    orders = data["Orders"]
    articles = data["Articles"]


