from collections import OrderedDict

from datastructures import Wave, WaveLimitExceeded


def orders_to_waves(order_set: set) -> list:
    waves = []

    orders = OrderedDict()
    for _ in range(len(order_set)):
        o = order_set.pop()
        orders.update({o.order_id: o})

    while len(orders) > 0:
        dist = OrderedDict()

        order_ids = OrderedDict([(orders[key].order_id, len(orders[key].warehouse_ids))
                                 for key in orders])

        for key in reversed(sorted(order_ids, key=order_ids.get)):
            order_ids.move_to_end(key)

        start_order = orders.popitem(False)

        for order_id in orders:
            if order_id != start_order[1].order_id:
                dist[order_id] = sum([
                    (int(x) - y) % 11 for x, y in zip(orders[order_id].warehouse_bits, start_order[1].warehouse_bits)
                ])

        for key in sorted(dist, key=dist.get):
            dist.move_to_end(key)

        wave = Wave()
        while True:
            try:
                wave.append(orders.pop(dist.popitem(False)[0]))
            except (WaveLimitExceeded, KeyError):
                break

        waves.append(wave)

    return waves
