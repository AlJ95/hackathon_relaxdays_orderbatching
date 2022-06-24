
from collections import defaultdict


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

    def __init__(self, order_id: int, articles: list):
        self.order_id = order_id
        self.articles = articles
        self.volume_per_warehouse = defaultdict(lambda: 0)
        for article in self.articles:
            self.volume_per_warehouse[article.warehouse_id] += article.volume
        self.warehouse_ids = self.volume_per_warehouse.keys()

    def __lt__(self, other):
        # self < other
        # to determine which order is best to pick as a first item for a wave
        if len(self.warehouse_ids) < len(other.warehouse_ids):
            return True
        elif len(self.warehouse_ids) == len(other.warehouse_ids):
            if sum(self.volume_per_warehouse.values()) > sum(other.volume_per_warehouse.values()):
                return True
            else:
                return False
        else:
            return False

    def __repr__(self):
        return (
            f'<Order order_id={self.order_id} '
            f'articles=[{", ".join([str(article) for article in self.articles])}]>'
        )


class Wave:

    id_counter = 0

    def __init__(self, wave_size=250, batch_volume=10_000):
        self.wave_id = Wave.id_counter
        Wave.id_counter += 1
        self.article_amount = 0
        self.wave_size = wave_size
        self.batch_volume = batch_volume
        self.orders = []
        self.volume_per_warehouse = defaultdict(lambda: 0)

    def __repr__(self):
        return (
            f'<Wave wave_id={self.wave_id} article_amount={self.article_amount} '
            f'order_ids=[{", ".join([str(order.order_id) for order in self.orders])}]>'
        )

    def append(self, order: Order):
        if self.fits(order):
            self.article_amount += len(order.articles)
            for warehouse_id, volume in order.volume_per_warehouse.items():
                self.volume_per_warehouse[warehouse_id] += volume
            self.orders.append(order)
        else:
            raise WaveLimitExceeded

    def fits(self, order: Order) -> bool:
        order_article_amount = len(order.articles)
        if self.article_amount + order_article_amount > self.wave_size:
            return False
        else:
            return True

    def score(self, order: Order) -> float:
        score = 0
        for warehouse_id, volume in order.volume_per_warehouse.items():
            difference = self.batch_volume - ((self.volume_per_warehouse[warehouse_id] + volume) % self.batch_volume)
            difference = 0 if difference == self.batch_volume else difference
            score += difference
        score = score / (len(order.volume_per_warehouse) * self.batch_volume)
        assert 0.0 <= score <= 1.0
        return score
