
from collections import defaultdict, OrderedDict


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

    orders = {}
    dist = OrderedDict()

    def __init__(self, order_id: int, articles: list, max_warehouses=16):
        self.order_id = order_id
        self.articles = articles
        self.volume_per_warehouse = defaultdict(lambda: 0)
        for article in self.articles:
            self.volume_per_warehouse[article.warehouse_id] += article.volume
        self.warehouse_ids = self.volume_per_warehouse.keys()
        self.warehouse_bits = [(1 if i in self.warehouse_ids else 0) for i in range(max_warehouses)]
        Order.orders[self.order_id] = self

    def __repr__(self):
        return (
            f'<Order order_id={self.order_id} '
            f'articles=[{", ".join([str(article) for article in self.articles])}]>'
        )

    @staticmethod
    def get_first_order():
        order = OrderedDict([(Order.orders[key].order_id, len(Order.orders[key].warehouse_ids))
                             for key in Order.orders])

        for key in reversed(sorted(order, key=order.get)):
            order.move_to_end(key)

        return Order.orders.pop(next(iter(order)))

    @staticmethod
    def calc_distance(order):
        for order_id in Order.orders:
            if order_id != order.order_id:
                Order.dist[order_id] = sum([
                    (int(x) - y) % 11 for x, y in zip(Order.orders[order_id].warehouse_bits, order.warehouse_bits)
                ])

        for key in sorted(Order.dist, key=Order.dist.get):
            Order.dist.move_to_end(key)

    @staticmethod
    def get_wave():
        order = Order.get_first_order()
        Order.calc_distance(order)
        return [Order.orders[Order.dist.popitem(False)[0]] for _ in range(240)]


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
