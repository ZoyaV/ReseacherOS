# Simulating User Agents for Embodied Conversational-AI

- Rank: 1
- Question: large language models embodied agents
- Score: 0.910
- ArXiv: https://arxiv.org/abs/2410.23535
- ArXiv ID: 2410.23535
- Source report: selected_results
- Matched terms: agents, embodied, language, large
- Full text extracted: no
- Extracted text chars: 0
- HTML cache: not available
- PDF cache: not available
- Text cache: not available

## Answer Generation

- Source: abstract_heuristic
- Backend: abstract_heuristic

## Abstract

Embodied agents designed to assist users with tasks must engage in natural language interactions, interpret instructions, execute actions, and communicate effectively to resolve issues. However, collecting large-scale, diverse datasets of situated human-robot dialogues to train and evaluate such agents is expensive, labor-intensive, and time-consuming. To address this challenge, we propose building a large language model (LLM)-based user agent that can simulate user behavior during interactions with an embodied agent in a virtual environment. Given a user goal (e.g., make breakfast), at each time step, the user agent may observe" the robot actions or speak" to either intervene with the robot or answer questions. Such a user agent assists in improving the scalability and efficiency of embodied dialogues dataset generation and is critical for enhancing and evaluating the robot's interaction and task completion ability, as well as for research in reinforcement learning using AI feedback. We evaluate our user agent's ability to generate human-like behaviors by comparing its simulated dialogues with the TEACh dataset. We perform three experiments: zero-shot prompting to predict dialogue acts, few-shot prompting, and fine-tuning on the TEACh training subset. Results show the LLM-based user agent achieves an F-measure of 42% with zero-shot prompting and 43.4% with few-shot prompting in mimicking human speaking behavior. Through fine-tuning, performance in deciding when to speak remained stable, while deciding what to say improved from 51.1% to 62.5%. These findings showcase the feasibility of the proposed approach for assessing and enhancing the effectiveness of robot task completion through natural language communication.

## Direct Answer

Embodied agents designed to assist users with tasks must engage in natural language interactions, interpret instructions, execute actions, and communicate effectively to resolve issues. However, collecting large-scale, diverse datasets of situated human-robot dialogues to train and evaluate such agents is expensive, labor-intensive, and time-consuming.

## Detailed Answer

Embodied agents designed to assist users with tasks must engage in natural language interactions, interpret instructions, execute actions, and communicate effectively to resolve issues. However, collecting large-scale, diverse datasets of situated human-robot dialogues to train and evaluate such agents is expensive, labor-intensive, and time-consuming. To address this challenge, we propose building a large language model (LLM)-based user agent that can simulate user behavior during interactions with an embodied agent in a virtual environment. Given a user goal (e.g., make breakfast), at each time step, the user agent may observe" the robot actions or speak" to either intervene with the robot or answer questions. Such a user agent assists in improving the scalability and efficiency of embodied dialogues dataset generation and is critical for enhancing and evaluating the robot's interaction and task completion ability, as well as for research in reinforcement learning using AI feedback. We evaluate our user agent's ability to generate human-like behaviors by comparing its simulated dialogues with the TEACh dataset. We perform three experiments: zero-shot prompting to predict dialogue acts, few-shot prompting, and fine-tuning on the TEACh training subset. Results show the LLM-based user agent achieves an F-measure of 42% with zero-shot prompting and 43.4% with few-shot prompting in mimicking human speaking behavior. Through fine-tuning, performance in deciding when to speak remained stable, while deciding what to say improved from 51.1% to 62.5%. These findings showcase the feasibility of the proposed approach for assessing and enhancing the effectiveness of robot task completion through natural language communication.

## Evidence From The Paper

- "Embodied agents designed to assist users with tasks must engage in natural language interactions, interpret instructions, execute actions, and communicate effectively to resolve issues."
- "However, collecting large-scale, diverse datasets of situated human-robot dialogues to train and evaluate such agents is expensive, labor-intensive, and time-consuming."
- "To address this challenge, we propose building a large language model (LLM)-based user agent that can simulate user behavior during interactions with an embodied agent in a virtual environment."
- "Given a user goal (e.g., make breakfast), at each time step, the user agent may observe" the robot actions or speak" to either intervene with the robot or answer questions."

## Limitations / Caution

Эвристический ответ по абстракту без LLM-агента.
