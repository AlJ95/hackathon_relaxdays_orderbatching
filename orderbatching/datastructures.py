
import numpy as np


class WaveLimitExceeded(Exception):
    pass


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

    all_warehouse_ids = set()

    def __init__(self, order_id: int, articles: list):
        self.order_id = order_id
        self.articles = articles
        self.warehouse_ids = set([article.warehouse_id for article in self.articles])
        Order.all_warehouse_ids.update(self.warehouse_ids)
        self.warehouse_bits = None

    def __repr__(self):
        return (
            f'<Order order_id={self.order_id} '
            f'articles=[{", ".join([str(article) for article in self.articles])}]>'
        )

    def get_warehouse_bits(self):
        if self.warehouse_bits is None:
            self.warehouse_bits = np.array([(1 if i in self.warehouse_ids else 0) for i in Order.all_warehouse_ids])
        return self.warehouse_bits

    @classmethod
    def cast_all_warehouse_ids_attr(cls):
        # to preserve order when iterating over all_warehouse_ids
        cls.all_warehouse_ids = list(cls.all_warehouse_ids)


class Wave:

    id_counter = 0

    def __init__(self, wave_size=250):
        self.wave_id = Wave.id_counter
        Wave.id_counter += 1
        self.article_amount = 0
        self.wave_size = wave_size
        self.orders = set()

    def __repr__(self):
        return (
            f'<Wave wave_id={self.wave_id} article_amount={self.article_amount} '
            f'order_ids=[{", ".join([str(order.order_id) for order in self.orders])}]>'
        )

    def append(self, order: Order):
        order_article_amount = len(order.articles)
        if self.article_amount + order_article_amount <= self.wave_size:
            self.article_amount += order_article_amount
            self.orders.add(order)
        else:
            raise WaveLimitExceeded
