
class Article:

    article_id_mapping = {}

    def __init__(self, article_id, volume):
        self.article_id = article_id
        self.volume = volume
        self.warehouse_id = None
        self.aisle = None
        self.article_id_mapping[self.article_id] = self


class Order:

    def __init__(self, order_id, articles):
        self.order_id = order_id
        self.articles = articles
        self._weight_per_warehouse = {}
        for article in self.articles:
            try:
                self._weight_per_warehouse[article.warehouse_id] += article.volume
            except KeyError:
                self._weight_per_warehouse[article.warehouse_id] = article.volume

    def get_warehouse_weight(self, warehouse_id):
        return self._weight_per_warehouse[warehouse_id]
