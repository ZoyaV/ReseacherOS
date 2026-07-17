# SPADE: Towards Scalable Path Planning Architecture on Actionable Multi-Domain 3D Scene Graphs

- Rank: 5
- Question: scene graph robot planning
- Score: 0.820
- ArXiv: https://arxiv.org/abs/2505.19098
- ArXiv ID: 2505.19098
- Source report: selected_results
- Matched terms: graph, planning, robot, scene
- Full text extracted: no
- Extracted text chars: 0
- HTML cache: not available
- PDF cache: not available
- Text cache: not available

## Answer Generation

- Source: abstract_heuristic
- Backend: abstract_heuristic

## Abstract

In this work, we introduce SPADE, a path planning framework designed for autonomous navigation in dynamic environments using 3D scene graphs. SPADE combines hierarchical path planning with local geometric awareness to enable collision-free movement in dynamic scenes. The framework bifurcates the planning problem into two: (a) solving the sparse abstract global layer plan and (b) iterative path refinement across denser lower local layers in step with local geometric scene navigation. To ensure efficient extraction of a feasible route in a dense multi-task domain scene graphs, the framework enforces informed sampling of traversable edges prior to path-planning. This removes extraneous information not relevant to path-planning and reduces the overall planning complexity over a graph. Existing approaches address the problem of path planning over scene graphs by decoupling hierarchical and geometric path evaluation processes. Specifically, this results in an inefficient replanning over the entire scene graph when encountering path obstructions blocking the original route. In contrast, SPADE prioritizes local layer planning coupled with local geometric scene navigation, enabling navigation through dynamic scenes while maintaining efficiency in computing a traversable route. We validate SPADE through extensive simulation experiments and real-world deployment on a quadrupedal robot, demonstrating its efficacy in handling complex and dynamic scenarios.

## Direct Answer

In this work, we introduce SPADE, a path planning framework designed for autonomous navigation in dynamic environments using 3D scene graphs. SPADE combines hierarchical path planning with local geometric awareness to enable collision-free movement in dynamic scenes.

## Detailed Answer

In this work, we introduce SPADE, a path planning framework designed for autonomous navigation in dynamic environments using 3D scene graphs. SPADE combines hierarchical path planning with local geometric awareness to enable collision-free movement in dynamic scenes. The framework bifurcates the planning problem into two: (a) solving the sparse abstract global layer plan and (b) iterative path refinement across denser lower local layers in step with local geometric scene navigation. To ensure efficient extraction of a feasible route in a dense multi-task domain scene graphs, the framework enforces informed sampling of traversable edges prior to path-planning. This removes extraneous information not relevant to path-planning and reduces the overall planning complexity over a graph. Existing approaches address the problem of path planning over scene graphs by decoupling hierarchical and geometric path evaluation processes. Specifically, this results in an inefficient replanning over the entire scene graph when encountering path obstructions blocking the original route. In contrast, SPADE prioritizes local layer planning coupled with local geometric scene navigation, enabling navigation through dynamic scenes while maintaining efficiency in computing a traversable route. We validate SPADE through extensive simulation experiments and real-world deployment on a quadrupedal robot, demonstrating its efficacy in handling complex and dynamic scenarios.

## Evidence From The Paper

- "In this work, we introduce SPADE, a path planning framework designed for autonomous navigation in dynamic environments using 3D scene graphs."
- "SPADE combines hierarchical path planning with local geometric awareness to enable collision-free movement in dynamic scenes."
- "The framework bifurcates the planning problem into two: (a) solving the sparse abstract global layer plan and (b) iterative path refinement across denser lower local layers in step with local geometric scene navigation."
- "To ensure efficient extraction of a feasible route in a dense multi-task domain scene graphs, the framework enforces informed sampling of traversable edges prior to path-planning."

## Limitations / Caution

Эвристический ответ по абстракту без LLM-агента.
