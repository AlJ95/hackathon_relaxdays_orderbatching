import time
from collections import OrderedDict
import numpy as np
from datastructures import Wave, WaveLimitExceeded


def orders_to_waves(order_set: set) -> list:
    waves = []

    ts = [0, 0, 0, 0, 0, 0]
    t0 = time.time()

    orders = OrderedDict()
    for _ in range(len(order_set)):
        o = order_set.pop()
        orders.update({o.order_id: o})

    ts[0] += time.time() - t0
    t0 = time.time()

    order_ids = OrderedDict([(orders[key].order_id, len(orders[key].warehouse_ids))
                             for key in orders])

    ts[1] += time.time() - t0
    t0 = time.time()

    for key in reversed(sorted(order_ids, key=order_ids.get)):
        order_ids.move_to_end(key)

    ts[2] += time.time() - t0
    t0 = time.time()

    fast = True

    while len(orders) > 0:
        dist = OrderedDict()

        start_order = orders.popitem(False)

        for order_id in orders:
            if not all([wh_id in start_order[1].warehouse_ids for wh_id in orders[order_id].warehouse_ids]) and fast:
                continue
            if order_id != start_order[1].order_id:
                dist[order_id] = sum([
                    (x - y) % 11 for x, y in zip(orders[order_id].get_warehouse_bits(),
                                                 start_order[1].get_warehouse_bits())
                ])

        ts[3] += time.time() - t0
        t0 = time.time()

        for key in sorted(dist, key=dist.get):
            dist.move_to_end(key)

        ts[4] += time.time() - t0
        t0 = time.time()

        wave = Wave()
        while True:
            try:
                order_id = dist.popitem(False)[0]
                wave.append(orders.pop(order_id))
                order_ids.pop(order_id)
            except KeyError:
                if fast:
                    fast = False
                else:
                    break
            except WaveLimitExceeded:
                break

        ts[5] += time.time() - t0
        t0 = time.time()

        waves.append(wave)
        print(len(orders))
        # print(ts)
    return waves, ts
