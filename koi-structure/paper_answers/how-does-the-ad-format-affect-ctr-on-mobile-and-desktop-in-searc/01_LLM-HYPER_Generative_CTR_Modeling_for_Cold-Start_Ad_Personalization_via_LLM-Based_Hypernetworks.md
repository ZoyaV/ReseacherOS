# LLM-HYPER: Generative CTR Modeling for Cold-Start Ad Personalization via LLM-Based Hypernetworks

- Rank: 1
- Question: How does the ad format affect CTR on mobile and desktop in search ads?
- Score: 1.000
- ArXiv: https://arxiv.org/abs/2604.12096
- ArXiv ID: 2604.12096
- Source report: selected_results
- Matched terms: ad, ads, ctr
- Full text extracted: no
- Extracted text chars: 0
- HTML cache: not available
- PDF cache: not available
- Text cache: not available

## Answer Generation

- Source: abstract_heuristic
- Backend: abstract_heuristic

## Abstract

On online advertising platforms, newly introduced promotional ads face the cold-start problem, as they lack sufficient user feedback for model training. In this work, we propose LLM-HYPER, a novel framework that treats large language models (LLMs) as hypernetworks to directly generate the parameters of the click-through rate (CTR) estimator in a training-free manner. LLM-HYPER uses few-shot Chain-of-Thought prompting over multimodal ad content (text and images) to infer feature-wise model weights for a linear CTR predictor. By retrieving semantically similar past campaigns via CLIP embeddings and formatting them into prompt-based demonstrations, the LLM learns to reason about customer intent, feature influence, and content relevance. To ensure numerical stability and serviceability, we introduce normalization and calibration techniques that align the generated weights with production-ready CTR distributions. Extensive offline experiments show that LLM-HYPER significantly outperforms cold-start baselines in NDCG$@10$ by 55.9\%. Our real-world online A/B test on one of the top e-commerce platforms in the U.S. demonstrates the strong performance of LLM-HYPER, which drastically reduces the cold-start period and achieves competitive performance. LLM-HYPER has been successfully deployed in production.

## Direct Answer

On online advertising platforms, newly introduced promotional ads face the cold-start problem, as they lack sufficient user feedback for model training. In this work, we propose LLM-HYPER, a novel framework that treats large language models (LLMs) as hypernetworks to directly generate the parameters of the click-through rate (CTR) estimator in a training-free manner.

## Detailed Answer

On online advertising platforms, newly introduced promotional ads face the cold-start problem, as they lack sufficient user feedback for model training. In this work, we propose LLM-HYPER, a novel framework that treats large language models (LLMs) as hypernetworks to directly generate the parameters of the click-through rate (CTR) estimator in a training-free manner. LLM-HYPER uses few-shot Chain-of-Thought prompting over multimodal ad content (text and images) to infer feature-wise model weights for a linear CTR predictor. By retrieving semantically similar past campaigns via CLIP embeddings and formatting them into prompt-based demonstrations, the LLM learns to reason about customer intent, feature influence, and content relevance. To ensure numerical stability and serviceability, we introduce normalization and calibration techniques that align the generated weights with production-ready CTR distributions. Extensive offline experiments show that LLM-HYPER significantly outperforms cold-start baselines in NDCG$@10$ by 55.9\%. Our real-world online A/B test on one of the top e-commerce platforms in the U.S. demonstrates the strong performance of LLM-HYPER, which drastically reduces the cold-start period and achieves competitive performance. LLM-HYPER has been successfully deployed in production.

## Evidence From The Paper

- "On online advertising platforms, newly introduced promotional ads face the cold-start problem, as they lack sufficient user feedback for model training."
- "In this work, we propose LLM-HYPER, a novel framework that treats large language models (LLMs) as hypernetworks to directly generate the parameters of the click-through rate (CTR) estimator in a training-free manner."
- "LLM-HYPER uses few-shot Chain-of-Thought prompting over multimodal ad content (text and images) to infer feature-wise model weights for a linear CTR predictor."
- "By retrieving semantically similar past campaigns via CLIP embeddings and formatting them into prompt-based demonstrations, the LLM learns to reason about customer intent, feature influence, and content relevance."

## Limitations / Caution

Эвристический ответ по абстракту без LLM-агента.
