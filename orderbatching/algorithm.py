
from datastructures import Wave


def orders_to_waves(orders: list) -> list:

    waves = []
    orders.sort()

    while orders:
        wave = Wave()
        wave.append(orders.pop(0))
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
            else:
                break
        waves.append(wave)

    return waves
