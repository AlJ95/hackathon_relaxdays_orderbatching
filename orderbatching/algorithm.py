
from datastructures import Wave


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

