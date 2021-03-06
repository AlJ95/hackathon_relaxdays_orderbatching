"""
This files was for verifying our solution.

It verified the given solution in data/solution0.json for the input data/instance0.json correctly.
"""
import json
import os

from datastructures import Article


WAVE_LIMIT = 250
BATCH_WEIGHT_LIMIT = 10000


def check_solution(solution: dict, articles: dict, orders: list):
    """
    Checks if solution is correct:

    1) Batch-Weight < 10,000
    2) |Wave| < 250

    :param articles: Articles dict in data["Articles"]
    :param solution: a dict, containing a list of waves and a list of batches
    :param orders: list of order dicts with keys 'OrderId' & 'ArticleIds'
    """

    waves = solution["Waves"]
    batches = solution["Batches"]

    assert all([check_wave_size(wave["BatchIds"], wave["WaveSize"], batches) for wave in waves]), "WaveSize's incorrect"
    assert check_max_wave_items(waves), "Wave limit is violated."
    assert all([check_batch_volume(batch, articles) for batch in batches]), "Batch Volumes are incorrect"
    assert check_max_batch_weight(batches), "Batch limit is violated."
    assert check_unique_order_ids(waves), "OrderIds are in different waves."
    assert check_all_articles_are_processed(batches, orders)

    tour_cost = calc_tour_cost(solution=solution, articles=articles)
    rest_cost = calc_rest_cost(solution=solution)
    print(f"Tour Cost: {tour_cost}\n"
          f"Rest Cost: {rest_cost}\n"
          f"Total Cost: {tour_cost + rest_cost}")


def check_wave_size(batch_ids: list, wave_size: int, batches: list) -> bool:
    """
    Checks if wave size is calculated correctly
    """
    batches = [order for batch in batches for order in batch["Items"] if batch["BatchId"] in batch_ids]
    return len(batches) == wave_size


def check_batch_volume(batch: dict, articles: dict) -> bool:
    """
    Check if batch volumes are calculated correctly in the solution dict
    """
    article_ids = [item["ArticleId"] for item in batch["Items"]]
    articles = [articles[article_id] for article_id in article_ids]
    return sum([article.volume for article in articles]) == batch["BatchVolume"]


def check_max_wave_items(waves: list) -> bool:
    """
    Check if all waves have items less than or equal to the maximum allowed.
    """
    return all([wave["WaveSize"] <= WAVE_LIMIT for wave in waves])


def check_max_batch_weight(batches: list) -> bool:
    """
    Check if all batches have weight/ volume less than or equal to the maximum allowed.
    """
    return all([batch["BatchVolume"] <= BATCH_WEIGHT_LIMIT for batch in batches])


def check_unique_order_ids(waves: dict) -> bool:
    """
    Checks if OrderIds are unique
    """
    order_ids = [order_id for wave in waves for order_id in wave["OrderIds"]]
    return len(order_ids) == len(set(order_ids))


def check_all_orders_processed(waves: dict, orders: list) -> bool:
    """
    Checks if all orders are processed
    """
    return len(set(orders)) == len(set([order_id for wave in waves for order_id in wave["OrderIds"]]))


def check_all_articles_are_processed(batches: dict, orders: list) -> bool:
    """
    Checks if all articles of all orders are processed
    """
    return (len([article for batch in batches for article in batch["Items"]]) ==
            len([article for order in orders for article in order["ArticleIds"]]))


def calc_tour_cost(solution: dict, articles: dict) -> int:
    """
    Calculate tour costs based on
    https://gitlab-hackathon.relaxdays.cloud/aufgaben/hackathon-summer-2022/-/blob/master/orderbatching.md
    """
    article_batches = [[articles[item["ArticleId"]] for item in batch["Items"]] for batch in solution["Batches"]]
    return sum(
        [len(set(article.warehouse_id for article in batch)) * 10 +
         len(set((article.warehouse_id, article.aisle_id) for article in batch)) * 5
         for batch in article_batches]
               )


def calc_rest_cost(solution: dict) -> int:
    """
    Calculate rest costs based on
    https://gitlab-hackathon.relaxdays.cloud/aufgaben/hackathon-summer-2022/-/blob/master/orderbatching.md
    """
    return len(solution["Waves"]) * 10 + len(solution["Batches"]) * 5


def calc_total_cost(solution: dict, articles: dict) -> int:
    """
    Calculate total costs based on
    https://gitlab-hackathon.relaxdays.cloud/aufgaben/hackathon-summer-2022/-/blob/master/orderbatching.md
    """
    return calc_tour_cost(solution, articles) + calc_rest_cost(solution)


if __name__ == "__main__":
    solution_path = f"{os.path.dirname(__file__)}/data/solution0.json"
    instance_path = f"{os.path.dirname(__file__)}/data/instance0.json"

    with open(solution_path) as file:
        result = json.load(file)

    with open(instance_path) as file:
        data = json.load(file)

    articles_id_mapping = {}

    for art in data['Articles']:
        articles_id_mapping[art['ArticleId']] = Article(
            article_id=art['ArticleId'], volume=art['Volume']
        )

    for article_location in data['ArticleLocations']:
        article_dict = articles_id_mapping[article_location['ArticleId']]
        article_dict.warehouse_id = article_location['Warehouse']
        article_dict.aisle_id = article_location['Aisle']

    check_solution(result, articles_id_mapping, data["Orders"])
