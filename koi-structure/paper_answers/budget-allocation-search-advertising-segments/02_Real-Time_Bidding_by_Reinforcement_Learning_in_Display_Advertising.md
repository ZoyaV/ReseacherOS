# Real-Time Bidding by Reinforcement Learning in Display Advertising

- Rank: 2
- Question: budget allocation search advertising segments
- Score: 0.970
- ArXiv: https://arxiv.org/abs/1701.02490
- ArXiv ID: 1701.02490
- Source report: selected_results
- Matched terms: advertising, budget
- Full text extracted: no
- Extracted text chars: 0
- HTML cache: not available
- PDF cache: not available
- Text cache: not available

## Answer Generation

- Source: abstract_heuristic
- Backend: abstract_heuristic

## Abstract

The majority of online display ads are served through real-time bidding (RTB) --- each ad display impression is auctioned off in real-time when it is just being generated from a user visit. To place an ad automatically and optimally, it is critical for advertisers to devise a learning algorithm to cleverly bid an ad impression in real-time. Most previous works consider the bid decision as a static optimization problem of either treating the value of each impression independently or setting a bid price to each segment of ad volume. However, the bidding for a given ad campaign would repeatedly happen during its life span before the budget runs out. As such, each bid is strategically correlated by the constrained budget and the overall effectiveness of the campaign (e.g., the rewards from generated clicks), which is only observed after the campaign has completed. Thus, it is of great interest to devise an optimal bidding strategy sequentially so that the campaign budget can be dynamically allocated across all the available impressions on the basis of both the immediate and future rewards. In this paper, we formulate the bid decision process as a reinforcement learning problem, where the state space is represented by the auction information and the campaign's real-time parameters, while an action is the bid price to set. By modeling the state transition via auction competition, we build a Markov Decision Process framework for learning the optimal bidding policy to optimize the advertising performance in the dynamic real-time bidding environment. Furthermore, the scalability problem from the large real-world auction volume and campaign budget is well handled by state value approximation using neural networks.

## Direct Answer

The majority of online display ads are served through real-time bidding (RTB) --- each ad display impression is auctioned off in real-time when it is just being generated from a user visit. To place an ad automatically and optimally, it is critical for advertisers to devise a learning algorithm to cleverly bid an ad impression in real-time.

## Detailed Answer

The majority of online display ads are served through real-time bidding (RTB) --- each ad display impression is auctioned off in real-time when it is just being generated from a user visit. To place an ad automatically and optimally, it is critical for advertisers to devise a learning algorithm to cleverly bid an ad impression in real-time. Most previous works consider the bid decision as a static optimization problem of either treating the value of each impression independently or setting a bid price to each segment of ad volume. However, the bidding for a given ad campaign would repeatedly happen during its life span before the budget runs out. As such, each bid is strategically correlated by the constrained budget and the overall effectiveness of the campaign (e.g., the rewards from generated clicks), which is only observed after the campaign has completed. Thus, it is of great interest to devise an optimal bidding strategy sequentially so that the campaign budget can be dynamically allocated across all the available impressions on the basis of both the immediate and future rewards. In this paper, we formulate the bid decision process as a reinforcement learning problem, where the state space is represented by the auction information and the campaign's real-time parameters, while an action is the bid price to set. By modeling the state transition via auction competition, we build a Markov Decision Process framework for learning the optimal bidding policy to optimize the advertising performance in the dynamic real-time bidding environment. Furthermore, the scalability problem from the large real-world auction volume and campaign budget is well handled by state value approximation using neural networks.

## Evidence From The Paper

- "The majority of online display ads are served through real-time bidding (RTB) --- each ad display impression is auctioned off in real-time when it is just being generated from a user visit."
- "To place an ad automatically and optimally, it is critical for advertisers to devise a learning algorithm to cleverly bid an ad impression in real-time."
- "Most previous works consider the bid decision as a static optimization problem of either treating the value of each impression independently or setting a bid price to each segment of ad volume."
- "However, the bidding for a given ad campaign would repeatedly happen during its life span before the budget runs out."

## Limitations / Caution

Эвристический ответ по абстракту без LLM-агента.
