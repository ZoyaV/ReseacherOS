# Boost CTR Prediction for New Advertisements via Modeling Visual Content

- Rank: 6
- Question: What CTR prediction models are used for search advertising?
- Score: 0.790
- ArXiv: https://arxiv.org/abs/2209.11727
- ArXiv ID: 2209.11727
- Source report: selected_results
- Matched terms: ad, advertising, ctr, prediction, rate
- Full text extracted: no
- Extracted text chars: 0
- HTML cache: not available
- PDF cache: not available
- Text cache: not available

## Answer Generation

- Source: abstract_heuristic
- Backend: abstract_heuristic

## Abstract

Existing advertisements click-through rate (CTR) prediction models are mainly dependent on behavior ID features, which are learned based on the historical user-ad interactions. Nevertheless, behavior ID features relying on historical user behaviors are not feasible to describe new ads without previous interactions with users. To overcome the limitations of behavior ID features in modeling new ads, we exploit the visual content in ads to boost the performance of CTR prediction models. Specifically, we map each ad into a set of visual IDs based on its visual content. These visual IDs are further used for generating the visual embedding for enhancing CTR prediction models. We formulate the learning of visual IDs into a supervised quantization problem. Due to a lack of class labels for commercial images in advertisements, we exploit image textual descriptions as the supervision to optimize the image extractor for generating effective visual IDs. Meanwhile, since the hard quantization is non-differentiable, we soften the quantization operation to make it support the end-to-end network training. After mapping each image into visual IDs, we learn the embedding for each visual ID based on the historical user-ad interactions accumulated in the past. Since the visual ID embedding depends only on the visual content, it generalizes well to new ads. Meanwhile, the visual ID embedding complements the ad behavior ID embedding. Thus, it can considerably boost the performance of the CTR prediction models previously relying on behavior ID features for both new ads and ads that have accumulated rich user behaviors. After incorporating the visual ID embedding in the CTR prediction model of Baidu online advertising, the average CTR of ads improves by 1.46%, and the total charge increases by 1.10%.

## Direct Answer

Existing advertisements click-through rate (CTR) prediction models are mainly dependent on behavior ID features, which are learned based on the historical user-ad interactions. Nevertheless, behavior ID features relying on historical user behaviors are not feasible to describe new ads without previous interactions with users.

## Detailed Answer

Existing advertisements click-through rate (CTR) prediction models are mainly dependent on behavior ID features, which are learned based on the historical user-ad interactions. Nevertheless, behavior ID features relying on historical user behaviors are not feasible to describe new ads without previous interactions with users. To overcome the limitations of behavior ID features in modeling new ads, we exploit the visual content in ads to boost the performance of CTR prediction models. Specifically, we map each ad into a set of visual IDs based on its visual content. These visual IDs are further used for generating the visual embedding for enhancing CTR prediction models. We formulate the learning of visual IDs into a supervised quantization problem. Due to a lack of class labels for commercial images in advertisements, we exploit image textual descriptions as the supervision to optimize the image extractor for generating effective visual IDs. Meanwhile, since the hard quantization is non-differentiable, we soften the quantization operation to make it support the end-to-end network training. After mapping each image into visual IDs, we learn the embedding for each visual ID based on the historical user-ad interactions accumulated in the past. Since the visual ID embedding depends only on the visual content, it generalizes well to new ads. Meanwhile, the visual ID embedding complements the ad behavior ID embedding. Thus, it can considerably boost the performance of the CTR prediction models previously relying on behavior ID features for both new ads and ads that have accumulated rich user behaviors. After incorporating the visual ID embedding in the CTR prediction model of Baidu online advertising, the average CTR of ads improves by 1.46%, and the total charge increases by 1.10%.

## Evidence From The Paper

- "Existing advertisements click-through rate (CTR) prediction models are mainly dependent on behavior ID features, which are learned based on the historical user-ad interactions."
- "Nevertheless, behavior ID features relying on historical user behaviors are not feasible to describe new ads without previous interactions with users."
- "To overcome the limitations of behavior ID features in modeling new ads, we exploit the visual content in ads to boost the performance of CTR prediction models."
- "Specifically, we map each ad into a set of visual IDs based on its visual content."

## Limitations / Caution

Эвристический ответ по абстракту без LLM-агента.
