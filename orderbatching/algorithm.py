import gmpy2
from collections import OrderedDict
from datastructures import Wave, WaveLimitExceeded


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
        while True:
            try:
                order_id = dist.popitem(False)[0]
                wave.add(orders.pop(order_id))
                order_ids.pop(order_id)
            except (WaveLimitExceeded, KeyError):
                break

        waves.append(wave)

    return waves
