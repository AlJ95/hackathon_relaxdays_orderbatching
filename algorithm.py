import time

import gmpy2
from collections import OrderedDict

from typing import List

from datastructures import Wave, WaveLimitExceeded, Batch, BatchLimitExceeded


def orders_to_waves(order_set: set) -> list:
    """
    Greedy Algorithm to link each order to a wave:
        Description:
            We want to start with the orders, which have to visit the most warehouses, because we can not optimize them.
            So we take this order A and add more orders based on the following cost-function:
                Order A visits warehouse 1 and order B visits warehouse 1                       -> 0
                Order A does not visit warehouse 1 and order B does also not visit warehouse 1  -> 0
                Order A visits warehouse 1 and order B does not need to visit warehouse 1       -> 1
                Order A does not visit warehouse 1 and order b visits warehouse 1               -> 10
            This Metric helps us to determine which orders are expensive to add

        Orders to add:
            Add all orders to a wave with minimal cost till this wave contains 250 articles.

    :param order_set: Set of orders (-> This makes the algorithm non-deterministic, because sets pop items arbitrary )
    :return: List of waves
    """
    waves = []

    # Transform set of orders to OrderedDict
    orders = OrderedDict()
    for _ in range(len(order_set)):
        o = order_set.pop()
        orders.update({o.order_id: o})

    # Extract all order_ids and its number of warehouse
    order_ids = OrderedDict([(orders[key].order_id, len(orders[key].warehouse_ids))
                             for key in orders])

    # Sort all orders based on the number of warehouse that it has to visit
    for key in reversed(sorted(order_ids, key=order_ids.get)):
        order_ids.move_to_end(key)

    # As long there are orders
    while len(orders) > 0:
        dist = OrderedDict()

        # Start with order with the most visiting warehouses
        start_order = orders.popitem(False)

        # Iterate through all orders
        # Generate a distance for all orders in respect to the start order
        for order_id in orders:
            if order_id != start_order[1].order_id:
                # This is a logical bitwise operation which does the same as described in the __doc__ of this function
                bit_vec_start = start_order[1].get_warehouse_bit_vector_repr()
                bit_vec_new = orders[order_id].get_warehouse_bit_vector_repr()
                dist[order_id] = gmpy2.popcount(bit_vec_start & ~bit_vec_new) + gmpy2.popcount(bit_vec_new & ~bit_vec_start) * 10

        # Sort by distance
        for key in sorted(dist, key=dist.get):
            dist.move_to_end(key)

        # Start filling waves with orders
        wave = Wave()
        wave.add(start_order[1])

        # As long as the batch article limit is not exceeded,
        # add articles from the next order in dist to the batch
        while True:
            try:
                order_id, order_dist = dist.popitem(False)
                order = orders.pop(order_id)
                wave.add(order)
                order_ids.pop(order_id)

            # If wave is full, start new one and add the last item, which could not be added to the batch
            except WaveLimitExceeded:
                orders.update({order_id: order})
                dist.update({order_id: order_dist})
                dist.move_to_end(order_id, last=False)
                break

            # If it raises KeyError, all orders are linked to a wave
            except KeyError:
                break

        waves.append(wave)

    return waves


def transform_article_dict(wave: Wave, articles_id_mapping: dict):
    """
    Here we will transform the articles dict which is structured as following:

    articles_id_mapping.items():
        (0, <Article article_id=0 volume=360 warehouse_id=1 aisle_id=0>)
        (1, <Article article_id=1 volume=420 warehouse_id=0 aisle_id=1>)
        (2, <Article article_id=2 volume=70 warehouse_id=0 aisle_id=3>)
        (3, <Article article_id=3 volume=490 warehouse_id=0 aisle_id=3>)
        (4, <Article article_id=4 volume=360 warehouse_id=1 aisle_id=1>)
        ...

    resulting articles_location_mapping after mapping to WAREHOUSES:
        (0, [(38, 9), (114, 9), (2, 9), (113, 4), (38, 4), ...]) -> Warehouse 0
        (1, [(65, 4), (50, 4), (43, 4), (112, 5), (56, 5), ...]) -> Warehouse 1

    resulting articles_location_mapping after mapping to AISLES that are mapped to WAREHOUSES:
        (0, OrderedDict([                                                                       -> Warehouse 1
            (3, [(<Article article_id=120 volume=250 warehouse_id=0 aisle_id=3>, 2),            -> Warehouse 1 Aisle 3
                 (<Article article_id=130 volume=310 warehouse_id=0 aisle_id=3>, 2), ...]),
            (1, [(<Article article_id=34 volume=110 warehouse_id=0 aisle_id=1>, 2),             -> Warehouse 1 Aisle 1
                 (<Article article_id=99 volume=420 warehouse_id=0 aisle_id=1>, 8), ...]),
                              ...
        (1, OrderedDict([                                                                       -> Warehouse 2
        (2, [(<Article article_id=77 volume=360 warehouse_id=1 aisle_id=2>, 2),                 -> Warehouse 2 Aisle 2
                ...] ...]

    Finally we will sort those OrderedDicts (Warehouses) and their containing OrderedDicts (Aisles) as following:
        1) First warehouse is the one with most articles that got ordered.
        2) First aisle in each warehouse is the one with most articles that got ordered

    :param wave: a Wave object that holds order_ids
    :param articles_id_mapping: the initial article_id_mapping dict
    :return: OrderedDict[OrderedDict[(Article, int)]] as WarehouseDict[AislesDict[(Article Object, OrderId)]]
    """

    # Assign every article in every order to the warehouse, which it is located
    # This is like a transformation of the given dict.
    # Instead of a list of articles and its attributes (e.g. warehouse),
    #   we transform it into a OrderedDict of warehouses with its articles
    articles_location_mapping = OrderedDict()
    for order in wave.orders:
        for article in order.articles:
            try:
                articles_location_mapping[article.warehouse_id].append((article.article_id, order.order_id))
            except KeyError:
                articles_location_mapping[article.warehouse_id] = [(article.article_id, order.order_id)]

    # We sort this OrderedDict based on the number of articles in all orders
    for key in sorted(articles_location_mapping, key=lambda x: len(articles_location_mapping.get(x)), reverse=True):
        articles_location_mapping.move_to_end(key)

    # Now we want to get the first warehouses of this OrderedDict
    # That means we prioritize warehouses with many articles
    for warehouse_id, article_list in articles_location_mapping.items():

        # We now do the previous steps for aisles too
        aisle_article = OrderedDict()
        for article_id, order_id in article_list:
            article = articles_id_mapping[article_id]
            try:
                aisle_article[article.aisle_id].append((article, order_id))
            except KeyError:
                aisle_article[article.aisle_id] = [(article, order_id)]

        # swap list of articles with OrderedDicts of aisles
        articles_location_mapping[warehouse_id] = aisle_article

        # We sort this OrderedDict based on the number of articles in all orders
        for key in sorted(articles_location_mapping[warehouse_id],
                          key=lambda x: len(articles_location_mapping[warehouse_id].get(x)), reverse=True):
            articles_location_mapping[warehouse_id].move_to_end(key)

    return articles_location_mapping


def articles_to_batch(wave: Wave, articles_id_mapping: dict) -> List[Batch]:
    batches = []

    # Transform Dict of articles into dict of warehouses and its aisles
    articles_location_mapping = transform_article_dict(wave, articles_id_mapping)

    # While there are warehouses with orders left
    while articles_location_mapping:

        # Get first warehouse and delete it from dict
        _, warehouse = articles_location_mapping.popitem(False)

        # While there are aisles withing this warehouse left
        while warehouse:

            # Get first aisle and delete it from dict
            _, aisle = warehouse.popitem(False)

            # Sort aisle by volume (descending)
            aisle.sort(key=lambda x: x[0].volume, reverse=True)

            # Start batch filling
            batch = Batch()

            # As long as the batch volume is not exceeded,
            # add articles from that aisle to the batch
            while True:
                try:
                    article, order_id = aisle.pop(0)
                    batch.add(article, order_id)

                # If Batch is too full for the last article,
                # close the batch, append it to all other batches and start a new batch with the last article,
                # which did not fit into the full one.
                except BatchLimitExceeded:
                    batches.append(batch)
                    batch = Batch()
                    batch.add(article, order_id)

                # If it raises IndexError, then the aisles is empty.
                # Then we try to fill this batch only with FULL aisles, because:
                # 1x more aisles costs 5 cost-points. 1x more batch costs also 5 cost-points
                # Aisles splitting produces more costs than just doing an aisle per batch.
                # Filling a full aisle, reduces costs.
                except IndexError:
                    aisle_ids_to_pop = []
                    for aisle_id, aisle in warehouse.items():

                        # Check if full aisle fits into batch
                        aisle_volume = sum([article[0].volume for article in aisle])
                        if batch.volume + aisle_volume <= batch.max_batch_volume:
                            for article, order_id in aisle:
                                batch.add(article, order_id)
                            aisle_ids_to_pop.append(aisle_id)

                    # Remove all aisles which were added to the batch
                    for aisle_id in aisle_ids_to_pop:
                        warehouse.pop(aisle_id)

                    batches.append(batch)
                    break

    return batches


def distribute_orders(order_set: set, articles_id_mapping: dict):
    """
    Main function to distribute all orders into waves and batches.

    :param order_set:
    :param articles_id_mapping:
    :return:
    """
    t0 = time.time()
    order_count = len(order_set)

    waves = orders_to_waves(order_set=order_set)

    batches = []
    for wave in waves:
        res = articles_to_batch(wave, articles_id_mapping)
        batches += res
        wave.batch_ids = [batch.batch_id for batch in res]

    solution = {
        "Waves": [wave.get_solution_dict() for wave in waves],
        "Batches": [batch.get_solution_dict() for batch in batches]
    }

    print("####################################\n")
    print("Statistics:\n")
    if waves:
        print(f"Average Number of Articles per Wave: {sum([wave.wave_size for wave in waves])/len(waves): 3.1f}")
        print(f"Average Weight of per Batch: {sum([batch.volume for batch in batches]) / len(batches): 4.0f}")

    print(f"Number of Waves: {len(waves)}")
    print(f"Number of Batches: {len(batches)}")
    print(f"{time.time() - t0: 3.0f} seconds needed for {order_count} orders.\n")

    print("\n####################################")

    return solution
