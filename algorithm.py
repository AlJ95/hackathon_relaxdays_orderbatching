import time

import gmpy2
from collections import OrderedDict

from typing import List

from datastructures import Wave, WaveLimitExceeded, Batch, BatchLimitExceeded
from test_solution import check_solution


def orders_to_waves(order_set: set) -> list:
    waves = []

    orders = OrderedDict()
    for _ in range(len(order_set)):
        o = order_set.pop()
        orders.update({o.order_id: o})

    order_ids = OrderedDict([(orders[key].order_id, len(orders[key].warehouse_ids))
                             for key in orders])

    for key in reversed(sorted(order_ids, key=order_ids.get)):
        order_ids.move_to_end(key)

    while len(orders) > 0:
        dist = OrderedDict()

        start_order = orders.popitem(False)

        for order_id in orders:
            if order_id != start_order[1].order_id:
                bit_vec1, bit_vec2 = orders[order_id].get_warehouse_bit_vector_repr(), \
                                     start_order[1].get_warehouse_bit_vector_repr()
                dist[order_id] = gmpy2.popcount(bit_vec1 & ~bit_vec2) + gmpy2.popcount(bit_vec1 & ~bit_vec2) * 10

        for key in sorted(dist, key=dist.get):
            dist.move_to_end(key)

        wave = Wave()
        wave.add(start_order[1])
        while True:
            try:
                order_id, order_dist = dist.popitem(False)
                order = orders.pop(order_id)
                wave.add(order)
                order_ids.pop(order_id)
            except WaveLimitExceeded:
                orders.update({order_id: order})
                dist.update({order_id: order_dist})
                dist.move_to_end(order_id, last=False)
                break
            except KeyError:
                break

        waves.append(wave)

    return waves


def articles_to_batch(wave: Wave, articles_id_mapping: dict) -> List[Batch]:
    batches = []

    articles_location_mapping = OrderedDict()
    for order in wave.orders:
        for article in order.articles:
            try:
                articles_location_mapping[article.warehouse_id].append((article.article_id, order.order_id))
            except KeyError:
                articles_location_mapping[article.warehouse_id] = [(article.article_id, order.order_id)]
    for key in sorted(articles_location_mapping, key=lambda x: len(articles_location_mapping.get(x)), reverse=True):
        articles_location_mapping.move_to_end(key)
    for warehouse_id, article_list in articles_location_mapping.items():
        aisle_article = OrderedDict()
        for article_id, order_id in article_list:
            article = articles_id_mapping[article_id]
            try:
                aisle_article[article.aisle_id].append((article, order_id))
            except KeyError:
                aisle_article[article.aisle_id] = [(article, order_id)]
        articles_location_mapping[warehouse_id] = aisle_article
        for key in sorted(articles_location_mapping[warehouse_id], key=lambda x: len(articles_location_mapping[warehouse_id].get(x)), reverse=True):
            articles_location_mapping[warehouse_id].move_to_end(key)

    while articles_location_mapping:
        _, warehouse = articles_location_mapping.popitem(False)
        while warehouse:
            _, aisle = warehouse.popitem(False)
            aisle.sort(key=lambda x: x[0].volume, reverse=True)
            batch = Batch()
            while True:
                try:
                    article, order_id = aisle.pop(0)
                    batch.add(article, order_id)
                except BatchLimitExceeded:
                    batches.append(batch)
                    batch = Batch()
                    batch.add(article, order_id)
                except IndexError:
                    aisle_ids_to_pop = []
                    for aisle_id, aisle in warehouse.items():
                        aisle_volume = sum([article[0].volume for article in aisle])
                        if batch.volume + aisle_volume <= batch.max_batch_volume:
                            for article, order_id in aisle:
                                batch.add(article, order_id)
                            aisle_ids_to_pop.append(aisle_id)
                    for aisle_id in aisle_ids_to_pop:
                        warehouse.pop(aisle_id)
                    batches.append(batch)
                    break

    return batches


def distribute_orders(order_set: set, articles_id_mapping: dict):
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

    check_solution(solution, articles_id_mapping)

    print("\n####################################")

    return solution
