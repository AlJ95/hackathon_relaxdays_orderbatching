from datastructures import Wave, Order
from collections import OrderedDict


def orders_to_waves(orders: set) -> list:

    waves = []

    while orders:
        wave = Wave()
        while True:
            best_order, best_score = None, float('inf')
            for order in orders:
                if wave.fits(order):
                    score = wave.score(order)
                    if score < best_score:
                        best_order, best_score = order, score
            if best_order:
                wave.append(best_order)
                orders.remove(best_order)
                print(f'wave_id {wave.wave_id}: new order {best_order.order_id}')
            else:
                break
        waves.append(wave)
        print()

    return waves


def orders_to_waves2(order_set: set) -> list:
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

        wave = []
        for _ in range(min(240, len(orders))):
            wave.append(orders.pop(dist.popitem(False)[0]))

        waves.append(wave)

    return waves

