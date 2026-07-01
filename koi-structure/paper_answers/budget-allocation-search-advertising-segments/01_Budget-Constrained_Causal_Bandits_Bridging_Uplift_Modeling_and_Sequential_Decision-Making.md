# Budget-Constrained Causal Bandits: Bridging Uplift Modeling and Sequential Decision-Making

- Rank: 1
- Question: budget allocation search advertising segments
- Score: 0.850
- ArXiv: https://arxiv.org/abs/2604.26169
- ArXiv ID: 2604.26169
- Source report: selected_results
- Matched terms: advertising, allocation, budget, segments
- Full text extracted: no
- Extracted text chars: 0
- HTML cache: not available
- PDF cache: not available
- Text cache: not available

## Answer Generation

- Source: abstract_heuristic
- Backend: abstract_heuristic

## Abstract

Treatment allocation under budget constraints is a central challenge in digital advertising: advertisers must decide which users to show ads to while spending a limited budget wisely. The standard approach follows a two-stage offline pipeline - first collect historical data to estimate heterogeneous treatment effects (HTE), then solve a constrained optimization to allocate the budget. This works well with abundant data, but fails in cold-start settings such as new campaigns, new markets, or new customer segments where little historical data exists. We propose Budget-Constrained Causal Bandits (BCCB), an online framework that learns which users respond to ads while simultaneously spending the budget, making treatment decisions one user at a time. BCCB unifies three components into a single sequential process: learning individual-level ad effectiveness, exploring users whose response is uncertain, and pacing the budget over time. We evaluated on the Criteo Uplift dataset, a large-scale advertising dataset from a real randomized controlled trial. Our key finding is a data-efficiency crossover: offline methods require approximately 10,000 historical observations to produce reliable results, while BCCB operates effectively from the very first user. Furthermore, BCCB exhibits 3-5x lower performance variance between runs, making it more practical for real campaign planning. Among purely online methods, BCCB consistently outperforms standard Thompson Sampling, budgeted Thompson Sampling, and greedy HTE estimation across all budget levels tested.

## Direct Answer

Treatment allocation under budget constraints is a central challenge in digital advertising: advertisers must decide which users to show ads to while spending a limited budget wisely. The standard approach follows a two-stage offline pipeline - first collect historical data to estimate heterogeneous treatment effects (HTE), then solve a constrained optimization to allocate the budget.

## Detailed Answer

Treatment allocation under budget constraints is a central challenge in digital advertising: advertisers must decide which users to show ads to while spending a limited budget wisely. The standard approach follows a two-stage offline pipeline - first collect historical data to estimate heterogeneous treatment effects (HTE), then solve a constrained optimization to allocate the budget. This works well with abundant data, but fails in cold-start settings such as new campaigns, new markets, or new customer segments where little historical data exists. We propose Budget-Constrained Causal Bandits (BCCB), an online framework that learns which users respond to ads while simultaneously spending the budget, making treatment decisions one user at a time. BCCB unifies three components into a single sequential process: learning individual-level ad effectiveness, exploring users whose response is uncertain, and pacing the budget over time. We evaluated on the Criteo Uplift dataset, a large-scale advertising dataset from a real randomized controlled trial. Our key finding is a data-efficiency crossover: offline methods require approximately 10,000 historical observations to produce reliable results, while BCCB operates effectively from the very first user. Furthermore, BCCB exhibits 3-5x lower performance variance between runs, making it more practical for real campaign planning. Among purely online methods, BCCB consistently outperforms standard Thompson Sampling, budgeted Thompson Sampling, and greedy HTE estimation across all budget levels tested.

## Evidence From The Paper

- "Treatment allocation under budget constraints is a central challenge in digital advertising: advertisers must decide which users to show ads to while spending a limited budget wisely."
- "The standard approach follows a two-stage offline pipeline - first collect historical data to estimate heterogeneous treatment effects (HTE), then solve a constrained optimization to allocate the budget."
- "This works well with abundant data, but fails in cold-start settings such as new campaigns, new markets, or new customer segments where little historical data exists."
- "We propose Budget-Constrained Causal Bandits (BCCB), an online framework that learns which users respond to ads while simultaneously spending the budget, making treatment decisions one user at a time."

## Limitations / Caution

Эвристический ответ по абстракту без LLM-агента.
