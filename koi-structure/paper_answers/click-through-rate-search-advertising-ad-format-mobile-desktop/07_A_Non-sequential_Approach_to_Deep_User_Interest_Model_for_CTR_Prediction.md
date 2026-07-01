# A Non-sequential Approach to Deep User Interest Model for CTR Prediction

- Rank: 7
- Question: click-through rate search advertising ad format mobile desktop
- Score: 0.730
- ArXiv: https://arxiv.org/abs/2104.06312
- ArXiv ID: 2104.06312
- Source report: selected_results
- Matched terms: advertising, format, rate
- Full text extracted: no
- Extracted text chars: 0
- HTML cache: not available
- PDF cache: not available
- Text cache: not available

## Answer Generation

- Source: abstract_heuristic
- Backend: abstract_heuristic

## Abstract

Click-Through Rate (CTR) prediction plays an important role in many industrial applications, and recently a lot of attention is paid to the deep interest models which use attention mechanism to capture user interests from historical behaviors. However, most current models are based on sequential models which truncate the behavior sequences by a fixed length, thus have difficulties in handling very long behavior sequences. Another big problem is that sequences with the same length can be quite different in terms of time, carrying completely different meanings. In this paper, we propose a non-sequential approach to tackle the above problems. Specifically, we first represent the behavior data in a sparse key-vector format, where the vector contains rich behavior info such as time, count and category. Next, we enhance the Deep Interest Network to take such rich information into account by a novel attention network. The sparse representation makes it practical to handle large scale long behavior sequences. Finally, we introduce a multidimensional partition framework to mine behavior interactions. The framework can partition data into custom designed time buckets to capture the interactions among information aggregated in different time buckets. Similarly, it can also partition the data into different categories and capture the interactions among them. Experiments are conducted on two public datasets: one is an advertising dataset and the other is a production recommender dataset. Our models outperform other state-of-the-art models on both datasets.

## Direct Answer

Click-Through Rate (CTR) prediction plays an important role in many industrial applications, and recently a lot of attention is paid to the deep interest models which use attention mechanism to capture user interests from historical behaviors. However, most current models are based on sequential models which truncate the behavior sequences by a fixed length, thus have difficulties in handling very long behavior sequences.

## Detailed Answer

Click-Through Rate (CTR) prediction plays an important role in many industrial applications, and recently a lot of attention is paid to the deep interest models which use attention mechanism to capture user interests from historical behaviors. However, most current models are based on sequential models which truncate the behavior sequences by a fixed length, thus have difficulties in handling very long behavior sequences. Another big problem is that sequences with the same length can be quite different in terms of time, carrying completely different meanings. In this paper, we propose a non-sequential approach to tackle the above problems. Specifically, we first represent the behavior data in a sparse key-vector format, where the vector contains rich behavior info such as time, count and category. Next, we enhance the Deep Interest Network to take such rich information into account by a novel attention network. The sparse representation makes it practical to handle large scale long behavior sequences. Finally, we introduce a multidimensional partition framework to mine behavior interactions. The framework can partition data into custom designed time buckets to capture the interactions among information aggregated in different time buckets. Similarly, it can also partition the data into different categories and capture the interactions among them. Experiments are conducted on two public datasets: one is an advertising dataset and the other is a production recommender dataset. Our models outperform other state-of-the-art models on both datasets.

## Evidence From The Paper

- "Click-Through Rate (CTR) prediction plays an important role in many industrial applications, and recently a lot of attention is paid to the deep interest models which use attention mechanism to capture user interests from historical behaviors."
- "However, most current models are based on sequential models which truncate the behavior sequences by a fixed length, thus have difficulties in handling very long behavior sequences."
- "Another big problem is that sequences with the same length can be quite different in terms of time, carrying completely different meanings."
- "In this paper, we propose a non-sequential approach to tackle the above problems."

## Limitations / Caution

Эвристический ответ по абстракту без LLM-агента.
