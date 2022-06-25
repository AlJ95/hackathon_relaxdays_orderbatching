
import gmpy2


class WaveLimitExceeded(Exception):
    pass


class BatchLimitExceeded(Exception):
    pass


class Article:
    """
    This class is used to represent an article. For every article it holds its article_id, volume, warehouse_id and
    aisle_id.
    """

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
    """
    This class is used to represent an order. For every order it holds its order_id, articles, warehouse_ids occuring
    in this order and a warehouse_bit_vector_repr (see get_warehouse_bit_vector_repr). Furthermore it has the class
    attribute all_warehouse_ids to save all the existing warehouse_ids of a specific problem instance.
    """

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

    def get_warehouse_bit_vector_repr(self) -> gmpy2.mpz:
        """
        Creates a bitvector with 1s for each warehouse which has to visited in this order. This binary
        representation is then converted to an integer and saved in a gmpy2.mpz.

        :return: gmpy2.mpz representation of the bitvector
        """
        if self.warehouse_bit_vector_repr is None:
            bit_list = [(1 if i in self.warehouse_ids else 0) for i in Order.all_warehouse_ids]
            self.warehouse_bit_vector_repr = gmpy2.mpz(int(''.join([str(i) for i in bit_list]), 2))
        return self.warehouse_bit_vector_repr

    @classmethod
    def cast_all_warehouse_ids_attr(cls):
        """
        After all orders are instantiated, all_warehouse_ids (set) holds all existing warehouse_ids. This set
        is then casted to a list so that a specific order is preserved when iterating over all_warehouse_ids.
        (Iterating over sets is arbitrary.)
        """
        cls.all_warehouse_ids = list(cls.all_warehouse_ids)


class Wave:
    """
    This class is used to represent a wave. For every wave it holds its unique wave_id, article_amount, wave_size,
    orders (set Order instances) and batch_ids. The class attribute id_counter is used to ensure a unique id for every
    new instance.
    """

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
        """
        Adds an order to the wave and raises WaveLimitExceeded if this order does not fit into the wave. It also
        keeps track of total articles in this wave.

        :param order: order to add to the wave
        """
        order_article_amount = len(order.articles)
        if self.article_amount + order_article_amount <= self.wave_size:
            self.article_amount += order_article_amount
            self.orders.add(order)
        else:
            raise WaveLimitExceeded

    def get_solution_dict(self) -> dict:
        """
        :return: a dict which holds a representation of the wave corresponding to the specified solution format
        """
        return {
            "WaveId": self.wave_id,
            "BatchIds": self.batch_ids,
            "OrderIds": sorted([self.orders.pop().order_id for _ in range(len(self.orders))]),
            "WaveSize": self.article_amount
        }


class Batch:
    """
    This class is used to represent a batch. For every batch it holds its batch_id, max_batch_volume, volume and
    items ((article, order_id) tuples). The class attribute id_counter is used to ensure a unique id for every new
    instance.
    """

    id_counter = 0

    def __init__(self, max_batch_volume=10_000):
        self.batch_id = Batch.id_counter
        Batch.id_counter += 1
        self.max_batch_volume = max_batch_volume
        self.volume = 0
        self.items = []

    def __repr__(self):
        return (
            f'<Batch batch_id={self.batch_id} volume={self.volume} '
            f'items=[{", ".join([str(i) for i in self.items])}]>'
        )

    def add(self, article: Article, order_id: int):
        """
        Adds an (article, order_id)-tuple to the batch and raises BatchLimitExceeded if this article does not fit into
        the batch. It also keeps track of total volume of this batch.

        :param article: article to add to the batch
        :param order_id: order_id from which the article is from
        """
        article_volume = article.volume
        if self.volume + article_volume <= self.max_batch_volume:
            self.volume += article_volume
            self.items.append((article.article_id, order_id))
        else:
            raise BatchLimitExceeded

    def get_solution_dict(self) -> dict:
        """
        :return: a dict which holds a representation of the batch corresponding to the specified solution format
        """
        item_list = list(self.items)
        item_list.sort(key=lambda item: (item[0], item[1]))
        item_list = [{"OrderId": item[1], "ArticleId": item[0]} for item in item_list]
        return {
            "BatchId": self.batch_id,
            "Items": item_list,
            "BatchVolume": self.volume
        }
