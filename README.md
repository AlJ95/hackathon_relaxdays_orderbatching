# Orderbatching

Winning solution for the orderbatching problem from the third Relaxdays Hackathon.

Every problem instance consists articles and orders. Every article has a volume and is located 
in a warehouses aisle. The goal is to distribute orders on waves and to separate the articles from
each wave into batches under the following constraints:
- `BatchVolume <= 10,000`(each article in a wave has a volume)
- `WaveSize <= 250` (maximal amount of articles in a wave)

The quality of a solution is measured in the following way:
- $TourCost = \sum_{b \in Batches} CountWarehouses_b * 10 + CountAisles_b*5$
- $RestCost = CountWaves * 10 + CountBatches*5$
