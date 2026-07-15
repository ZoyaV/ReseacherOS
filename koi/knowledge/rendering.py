"""Deterministic Markdown rendering for project knowledge artifacts."""

from __future__ import annotations

from koi.core.models import NodeType, Project
from koi.knowledge.model import (
    KnowledgeDocument,
    VERDICT_MARK,
    methods_under,
    shorten,
    statistics,
)


GENERATED_DOC = "hypotheses.md"


def render_hypotheses(project: Project, report_index: dict) -> str:
    nodes = project.nodes
    causes, supported, refuted, insights = statistics(project)
    lines = [
        "# Гипотезы и результаты",
        "",
        f"Автовыжимка по {len(causes)} гипотезам (подтверждено: {supported}, "
        f"опровергнуто: {refuted}, открыто: {len(causes) - supported - refuted}; "
        f"инсайтов: {insights}). Источник — project.md и research.json, "
        "пересобирается при каждом сохранении проекта; не править руками.",
        "",
    ]
    for cause in causes:
        mark = VERDICT_MARK.get(cause.verdict, cause.verdict.value)
        lines += [
            f"## {cause.title}",
            "",
            f"Вердикт: {mark}  ·  узел `{cause.id}`",
            "",
        ]
        if cause.description:
            lines += [cause.description, ""]
        had_insights = False
        for method in methods_under(nodes, cause.id):
            for question in method.research_questions:
                had_insights = True
                source = f"метод `{method.id}`"
                if question.card_id:
                    source += f", карточка `{question.card_id}`"
                    report = report_index.get(question.card_id)
                    if report:
                        source += f" → [отчёт](../reports/{report})"
                narrative = question.narrative or question.answer or "—"
                lines += [
                    f"- {question.question}",
                    f"  - {narrative}  _(уверенность: {question.certainty.value}, "
                    f"важность: {question.importance}/5; {source})_",
                ]
        if not had_insights:
            lines.append("- _инсайтов пока нет (эксперимент не закрыт)._")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_project_index(
    project: Project,
    report_index: dict,
    documents: list[KnowledgeDocument],
) -> str:
    causes, supported, refuted, insights = statistics(project)
    problem = next(
        (node for node in project.nodes if node.node_type == NodeType.PROBLEM), None
    )
    lines = [
        f"# База знаний: {project.title}",
        "",
        "Оглавление базы знаний проекта: краткие сводки и ссылки, полные документы — ",
        "в [`knowledge/`](knowledge/), журнал пополнений — в ",
        "[KNOWLEDGE_LOG.md](KNOWLEDGE_LOG.md). Генерируется автоматически при каждом ",
        "сохранении проекта (`koi/knowledge/`) — не править руками.",
        "",
        f"Проект: `{project.id}` · гипотез: {len(causes)} "
        f"(✔ {supported} · ✗ {refuted} · … {len(causes) - supported - refuted}) "
        f"· инсайтов: {insights} · документов: {len(documents)}",
        "",
    ]
    if problem:
        lines += [
            "## Проблема",
            "",
            f"**{problem.title}.** {shorten(problem.description, 400)}",
            "",
        ]
    lines += ["## Документы", ""]
    if not documents:
        lines += [
            "_Документов пока нет — положите .md в `knowledge/` "
            "(см. конвенцию в docs/research-workflow.md)._",
            "",
        ]
    for document in documents:
        entry = f"- [{document.title}](knowledge/{document.name})"
        if document.summary:
            entry += f" — {document.summary}"
        lines.append(entry)
    lines.append("")
    lines += ["## Гипотезы — статус", ""]
    if not causes:
        lines += ["_Гипотез пока нет._", ""]
    for cause in causes:
        mark = VERDICT_MARK.get(cause.verdict, cause.verdict.value)
        questions = [
            question
            for method in methods_under(project.nodes, cause.id)
            for question in method.research_questions
        ]
        entry = f"- {mark} — [{cause.title}](knowledge/{GENERATED_DOC})"
        if questions:
            entry += f" · инсайтов: {len(questions)}"
        report = next(
            (
                report_index[question.card_id]
                for question in questions
                if question.card_id and question.card_id in report_index
            ),
            None,
        )
        if report:
            entry += f" · [отчёт](reports/{report})"
        lines.append(entry)
        if questions:
            top = max(questions, key=lambda question: question.importance)
            text = top.narrative or top.answer
            if text:
                lines.append(f"  - итог: {shorten(text, 200)}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"
