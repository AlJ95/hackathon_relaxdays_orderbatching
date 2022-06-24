import time

import gmpy2
from collections import OrderedDict

from typing import List

from datastructures import Wave, WaveLimitExceeded, Batch, BatchLimitExceeded, Article
from solution_checker import check_solution


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
        wave.add(start_order[1].order_id)
        while True:
            try:
                order_id = dist.popitem(False)[0]
                wave.add(orders.pop(order_id))
                order_ids.pop(order_id)
            except (WaveLimitExceeded, KeyError):
                break

        waves.append(wave)

    return waves


def orders_to_batch(wave: Wave) -> List[Batch]:
    batches = []

    orders = OrderedDict()
    for _ in range(len(wave.orders)):
        o = wave.orders.pop()
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
                dist[order_id] = gmpy2.popcount(bit_vec1 & ~bit_vec2) + gmpy2.popcount(bit_vec1 & ~bit_vec2) * 5

        for key in sorted(dist, key=dist.get):
            dist.move_to_end(key)

        batch = Batch()
        batch.add(start_order[1].order_id)
        while True:
            try:
                order_id = dist.popitem(False)[0]
                order = orders.pop(order_id)
                for article in order.articles:
                    batch.add(article, order.order_id)
                order_ids.pop(order_id)
            except (BatchLimitExceeded, KeyError):
                break

        wave.batch_ids.append(batch.batch_id)
        batches.append(batch)

    return batches


def distribute_orders(order_set: set, articles: dict):
    t0 = time.time()
    waves = orders_to_waves(order_set=order_set)

    batches = []
    for wave in waves:
        res = orders_to_batch(wave)
        for batch in res:
            batches.append(batch)

    solution = {
        "Waves": [wave.get_solution_dict() for wave in waves],
        "Batches": [batch.get_solution_dict() for batch in batches]
    }

    print("####################################\n")
    print("Statistics:\n")
    print(f"Average Number of Articles per Wave: {sum([wave.wave_size for wave in waves])/len(waves): 3.1f}")
    print(f"Average Weight of per Batch: {sum([batch.volume for batch in batches]) / len(batches): 4.0f}")
    print(f"{time.time() - t0: 3.0f} seconds needed for {len(order_set)} orders.\n")

    check_solution(solution, articles)

    print("\n####################################")

    return solution
