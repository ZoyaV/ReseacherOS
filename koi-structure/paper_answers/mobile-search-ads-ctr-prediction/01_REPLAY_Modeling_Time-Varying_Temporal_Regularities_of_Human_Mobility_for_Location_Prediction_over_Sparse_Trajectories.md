# REPLAY: Modeling Time-Varying Temporal Regularities of Human Mobility for Location Prediction over Sparse Trajectories

- Rank: 1
- Question: mobile search ads CTR prediction
- Score: 1.000
- ArXiv: https://arxiv.org/abs/2402.16310
- ArXiv ID: 2402.16310
- Source report: selected_results
- Matched terms: prediction, search
- Full text extracted: no
- Extracted text chars: 0
- HTML cache: not available
- PDF cache: not available
- Text cache: not available

## Answer Generation

- Source: abstract_heuristic
- Backend: abstract_heuristic

## Abstract

Location prediction forecasts a user's location based on historical user mobility traces. To tackle the intrinsic sparsity issue of real-world user mobility traces, spatiotemporal contexts have been shown as significantly useful. Existing solutions mostly incorporate spatiotemporal distances between locations in mobility traces, either by feeding them as additional inputs to Recurrent Neural Networks (RNNs) or by using them to search for informative past hidden states for prediction. However, such distance-based methods fail to capture the time-varying temporal regularities of human mobility, where human mobility is often more regular in the morning than in other periods, for example; this suggests the usefulness of the actual timestamps besides the temporal distances. Against this background, we propose REPLAY, a general RNN architecture learning to capture the time-varying temporal regularities for location prediction. Specifically, REPLAY not only resorts to the spatiotemporal distances in sparse trajectories to search for the informative past hidden states, but also accommodates the time-varying temporal regularities by incorporating smoothed timestamp embeddings using Gaussian weighted averaging with timestamp-specific learnable bandwidths, which can flexibly adapt to the temporal regularities of different strengths across different timestamps. Our extensive evaluation compares REPLAY against a sizable collection of state-of-the-art techniques on two real-world datasets. Results show that REPLAY consistently and significantly outperforms state-of-the-art methods by 7.7\%-10.5\% in the location prediction task, and the bandwidths reveal interesting patterns of the time-varying temporal regularities.

## Direct Answer

Location prediction forecasts a user's location based on historical user mobility traces. To tackle the intrinsic sparsity issue of real-world user mobility traces, spatiotemporal contexts have been shown as significantly useful.

## Detailed Answer

Location prediction forecasts a user's location based on historical user mobility traces. To tackle the intrinsic sparsity issue of real-world user mobility traces, spatiotemporal contexts have been shown as significantly useful. Existing solutions mostly incorporate spatiotemporal distances between locations in mobility traces, either by feeding them as additional inputs to Recurrent Neural Networks (RNNs) or by using them to search for informative past hidden states for prediction. However, such distance-based methods fail to capture the time-varying temporal regularities of human mobility, where human mobility is often more regular in the morning than in other periods, for example; this suggests the usefulness of the actual timestamps besides the temporal distances. Against this background, we propose REPLAY, a general RNN architecture learning to capture the time-varying temporal regularities for location prediction. Specifically, REPLAY not only resorts to the spatiotemporal distances in sparse trajectories to search for the informative past hidden states, but also accommodates the time-varying temporal regularities by incorporating smoothed timestamp embeddings using Gaussian weighted averaging with timestamp-specific learnable bandwidths, which can flexibly adapt to the temporal regularities of different strengths across different timestamps. Our extensive evaluation compares REPLAY against a sizable collection of state-of-the-art techniques on two real-world datasets. Results show that REPLAY consistently and significantly outperforms state-of-the-art methods by 7.7\%-10.5\% in the location prediction task, and the bandwidths reveal interesting patterns of the time-varying temporal regularities.

## Evidence From The Paper

- "Location prediction forecasts a user's location based on historical user mobility traces."
- "To tackle the intrinsic sparsity issue of real-world user mobility traces, spatiotemporal contexts have been shown as significantly useful."
- "Existing solutions mostly incorporate spatiotemporal distances between locations in mobility traces, either by feeding them as additional inputs to Recurrent Neural Networks (RNNs) or by using them to search for informative past hidden states for prediction."
- "However, such distance-based methods fail to capture the time-varying temporal regularities of human mobility, where human mobility is often more regular in the morning than in other periods, for example; this suggests the usefulness of the actual timestamps besides the temporal distances."

## Limitations / Caution

Эвристический ответ по абстракту без LLM-агента.
