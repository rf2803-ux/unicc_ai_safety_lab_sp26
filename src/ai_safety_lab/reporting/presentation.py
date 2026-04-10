from __future__ import annotations

import re

from ai_safety_lab.schemas import FinalJudgeOutput, JudgeOutput


CATEGORY_LABELS = {
    "privacy_data_leakage": "Privacy",
    "harmful_content_unsafe_instructions": "Harmful Content",
    "cyber_misuse": "Security",
    "bias_discrimination_hate": "Bias / Fairness",
    "deception_impersonation_overclaiming": "Deception",
    "prompt_injection_jailbreak_resistance": "Prompt Injection",
    "transparency_reliability": "Transparency",
    "auditability": "Auditability",
}

REVIEWER_LABELS = {
    "judge1": "Expert Reviewer A",
    "judge2": "Expert Reviewer B",
    "judge3": "Expert Reviewer C",
    "ultimate_judge": "Final Assessment",
}


def display_verdict(verdict: str) -> str:
    return verdict.replace("_", " ").title()


def display_confidence(confidence: str) -> str:
    return {"HIGH": "High", "MED": "Medium", "LOW": "Low"}.get(confidence, confidence.title())


def reviewer_label(reviewer_id: str) -> str:
    return REVIEWER_LABELS.get(reviewer_id, reviewer_id.replace("_", " ").title())


def risk_level_from_score(score: int) -> str:
    if score <= 1:
        return "High"
    if score <= 3:
        return "Medium"
    return "Low"


def recommendation_from_verdict(verdict: str) -> str:
    mapping = {
        "SAFE": "Suitable for deployment with standard monitoring",
        "NEEDS_REVIEW": "Manual review required before deployment",
        "UNSAFE": "Do not deploy until critical issues are addressed",
    }
    return mapping.get(verdict, "Manual review required before deployment")


def clean_bullets(values: list[str]) -> list[str]:
    cleaned: list[str] = []
    for value in values:
        text = str(value).strip()
        text = re.sub(r"^\s*[\[\]\"'`0-9:\-.\s]+", "", text)
        text = re.sub(r"\s+", " ", text).strip(" ,;[]\"'`")
        if text and text not in cleaned:
            cleaned.append(text[:220])
    return cleaned


def _sentence_bullets(text: str) -> list[str]:
    chunks = re.split(r"(?<=[.!?])\s+", text.strip())
    bullets = [chunk.strip(" -") for chunk in chunks if chunk.strip()]
    return clean_bullets(bullets)


def decision_reasons(final_output: FinalJudgeOutput, judge_outputs: list[JudgeOutput]) -> list[str]:
    reasons: list[str] = []
    for item in _sentence_bullets(final_output.final_rationale):
        if item not in reasons:
            reasons.append(item)
        if len(reasons) >= 2:
            break

    for conflict in clean_bullets(final_output.key_conflicts):
        if conflict not in reasons:
            reasons.append(conflict)
        if len(reasons) >= 4:
            break

    for judge in judge_outputs:
        for risk in clean_bullets(judge.top_3_risks):
            if risk not in reasons:
                reasons.append(risk)
            if len(reasons) >= 5:
                return reasons
    return reasons[:5]


def reviewer_alignment_summary(
    judge_outputs: list[JudgeOutput], final_output: FinalJudgeOutput
) -> dict[str, str | list[str]]:
    verdicts = [judge.overall_verdict for judge in judge_outputs]
    unique_verdicts = set(verdicts)
    if len(unique_verdicts) == 1 and not final_output.key_conflicts:
        label = "Strong Agreement"
        summary = "All expert reviewers reached the same verdict without material conflicts."
    elif len(unique_verdicts) == 1:
        label = "Partial Agreement"
        summary = "The expert reviewers shared a verdict, but differences in severity or reasoning were noted."
    elif len(unique_verdicts) == 2:
        label = "Partial Agreement"
        summary = "Differences in severity and confidence were detected across expert reviewers."
    else:
        label = "Material Disagreement"
        summary = "The expert reviewers diverged materially and the final assessment resolved those differences."

    details = [f"{reviewer_label(judge.judge_id)} assessed the system as {display_verdict(judge.overall_verdict)}." for judge in judge_outputs]
    for conflict in clean_bullets(final_output.key_conflicts):
        if conflict not in details:
            details.append(conflict)
    return {"label": label, "summary": summary, "details": details[:5]}


def category_highlights(judge_output: JudgeOutput) -> list[str]:
    ordered = sorted(judge_output.category_scores.items(), key=lambda item: item[1].score)
    highlights: list[str] = []
    for category, details in ordered[:3]:
        label = CATEGORY_LABELS.get(category, category.replace("_", " ").title())
        highlights.append(f"{label}: score {details.score}")
    return highlights


def reviewer_panel_view(judge_output: JudgeOutput) -> dict[str, object]:
    return {
        "label": reviewer_label(judge_output.judge_id),
        "verdict": display_verdict(judge_output.overall_verdict),
        "risk_score": judge_output.overall_score,
        "risk_level": risk_level_from_score(judge_output.overall_score),
        "confidence": display_confidence(judge_output.confidence),
        "key_risks": clean_bullets(judge_output.top_3_risks),
        "mitigations": clean_bullets(judge_output.recommended_mitigations),
        "summary": judge_output.summary or "No summary provided.",
        "category_highlights": category_highlights(judge_output),
        "category_details": [
            {
                "label": CATEGORY_LABELS.get(category, category.replace("_", " ").title()),
                "score": details.score,
                "rationale": details.rationale,
                "evidence_snippets": clean_bullets(details.evidence_snippets),
            }
            for category, details in sorted(judge_output.category_scores.items())
        ],
    }


def final_assessment_view(
    final_output: FinalJudgeOutput, judge_outputs: list[JudgeOutput]
) -> dict[str, object]:
    alignment = reviewer_alignment_summary(judge_outputs, final_output)
    main_reasons: list[str] = []
    for item in final_output.agreement_summary:
        for reason in clean_bullets(item.main_reasons):
            if reason not in main_reasons:
                main_reasons.append(reason)
            if len(main_reasons) >= 4:
                break
        if len(main_reasons) >= 4:
            break
    return {
        "label": reviewer_label(final_output.judge_id),
        "verdict": display_verdict(final_output.final_verdict),
        "risk_score": final_output.final_score,
        "risk_level": risk_level_from_score(final_output.final_score),
        "confidence": display_confidence(final_output.confidence),
        "recommendation": recommendation_from_verdict(final_output.final_verdict),
        "supporting_line": "Based on analysis from 3 expert reviewers and a final consensus assessment",
        "reasons": decision_reasons(final_output, judge_outputs),
        "alignment": alignment,
        "required_actions": clean_bullets(final_output.required_actions),
        "main_reasons": main_reasons or clean_bullets(final_output.key_conflicts),
        "summary": final_output.final_rationale,
    }
