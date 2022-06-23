from typing import List

from datastructures import Article

WAVE_LIMIT = 250
BATCH_WEIGHT_LIMIT = 10000


def check_solution(solution: dict, articles: dict) -> bool:
    """
    Checks if solution is correct:

    1) Batch-Weight < 10,000
    2) |Wave| < 250

    :param articles: Articles dict in data["Articles"]
    :param solution: a dict, containing a list of waves and a list of batches
    :return: True if conditions are
    """

    waves = solution["Waves"]
    batches = solution["Batches"]

    assert all([check_wave_size(wave["BatchIds"], wave["WaveSize"], batches) for wave in waves]), "WaveSize's incorrect"
    assert check_max_wave_items(waves), "Wave limit is violated."
    assert all([check_batch_volume(batch, articles) for batch in batches]), "Batch Volumes are incorrect"
    assert check_max_batch_weight(waves), "Batch limit is violated."
    assert check_unique_order_ids(waves), "OrderIds are in different waves."

    return True


def check_wave_size(batch_ids: list, wave_size: int, batches: dict) -> bool:
    """
    Checks if wave size is calculated correctly
    :param wave_size:
    :param batch_ids:
    :param batches: batch dict
    :return:
    """
    return sum([len(batches[batch_id]["Items"]) for batch_id in batch_ids]) == wave_size


def check_batch_volume(batch: dict, articles: dict) -> bool:
    return sum([articles[article["ArticleId"]]["Volume"] for article in batch["Items"]]) == batch["BatchVolume"]


def check_max_wave_items(waves: list) -> bool:
    return all([wave["WaveSize"] < WAVE_LIMIT for wave in waves])


def check_max_batch_weight(waves: list) -> bool:
    return all([wave["WaveSize"] < WAVE_LIMIT for wave in waves])


def check_unique_order_ids(waves: dict) -> bool:
    order_ids = [order_id for wave in waves for order_id in wave["OrderIds"]]
    return len(order_ids) == len(set(order_ids))


def calc_tour_cost(solution: dict, articles: dict) -> int:
    article_batches = [[articles[item["ArticleId"]] for item in batch["Items"]] for batch in solution["Batches"]]
    return sum(
        [len(set(article.warehouse_id for article in batch)) * 10 +
         len(set(article.aisle_id for article in batch)) * 5
         for batch in article_batches]
               )


def calc_rest_cost(solution: dict) -> int:
    return len(solution["Waves"]) * 10 + len(solution["Batches"]) * 5


def calc_total_cost(solution: dict, articles: dict) -> int:
    return calc_tour_cost(solution, articles) + calc_rest_cost(solution)
