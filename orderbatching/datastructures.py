
class Article:

    def __init__(self, article_id: int, volume: int):
        self.article_id = article_id
        self.volume = volume
        self.warehouse_id = None
        self.aisle_id = None

    def __repr__(self):
        return (
            f'<Article article_id={self.article_id} volume={self.volume} '
            f'warehouse_id={self.warehouse_id} aisle_id={self.aisle_id}>'
        )


class Order:

    def __init__(self, order_id: int, articles: list):
        self.order_id = order_id
        self.articles = articles
        self._weight_per_warehouse = {}
        for article in self.articles:
            try:
                self._weight_per_warehouse[article.warehouse_id] += article.volume
            except KeyError:
                self._weight_per_warehouse[article.warehouse_id] = article.volume

    def __repr__(self):
        return (
            f'<Order order_id={self.order_id} '
            f'articles=[{" ,".join([str(article) for article in self.articles])}]>'
        )

    def get_warehouse_weight(self, warehouse_id: int) -> int:
        return self._weight_per_warehouse.get(warehouse_id, 0)
