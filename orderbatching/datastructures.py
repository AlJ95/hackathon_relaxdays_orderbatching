
import numpy as np
import gmpy2


class WaveLimitExceeded(Exception):
    pass

class BatchLimitExceeded(Exception):
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
        self.warehouse_bit_vector_repr = None

    def __repr__(self):
        return (
            f'<Order order_id={self.order_id} '
            f'articles=[{", ".join([str(article) for article in self.articles])}]>'
        )

    def get_warehouse_bit_vector_repr(self):
        if self.warehouse_bit_vector_repr is None:
            bit_list = [(1 if i in self.warehouse_ids else 0) for i in Order.all_warehouse_ids]
            self.warehouse_bit_vector_repr = gmpy2.mpz(int(''.join([str(i) for i in bit_list]), 2))
        return self.warehouse_bit_vector_repr

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
        self.batch_ids = []

    def __repr__(self):
        return (
            f'<Wave wave_id={self.wave_id} article_amount={self.article_amount} '
            f'order_ids=[{", ".join([str(order.order_id) for order in self.orders])}]>'
        )

    def add(self, order: Order):
        order_article_amount = len(order.articles)
        if self.article_amount + order_article_amount <= self.wave_size:
            self.article_amount += order_article_amount
            self.orders.add(order)
        else:
            raise WaveLimitExceeded

    def get_solution_dict(self):
        return {
            "WaveId": self.wave_id,
            "BatchIds": self.batch_ids,
            "OrderIds": sorted([self.orders.pop().order_id for _ in range(len(self.orders))]),
            "WaveSize": self.wave_size
        }


class Batch:

    id_counter = 0

    def __init__(self, max_batch_volume=10_000):
        self.batch_id = Batch.id_counter
        Batch.id_counter += 1
        self.max_batch_volume = max_batch_volume
        self.volume = 0
        self.items = set()

    def __repr__(self):
        return (
            f'<Batch batch_id={self.batch_id} volume={self.volume} '
            f'items=[{", ".join([str(i) for i in self.items])}]>'
        )

    def add(self, article: Article, order_id: int):
        article_volume = article.volume
        if self.volume + article_volume <= self.max_batch_volume:
            self.volume += article_volume
            self.items.add((article.article_id, order_id))
        else:
            raise BatchLimitExceeded

    def get_solution_dict(self):
        item_list = list(self.items)
        item_list.sort(key=lambda item: (item[0], item[1]))
        item_list = [{"OrderId": item[0], "ArticleId": item[1]} for item in item_list]
        return {
            "BatchId": self.batch_id,
            "Items": item_list
        }
