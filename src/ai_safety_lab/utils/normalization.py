from __future__ import annotations

import re
from typing import Any

from ai_safety_lab.constants import CATEGORY_KEYS, GOVERNANCE_DEFAULTS


def _stringify_list(values: list[Any], fallback: list[str]) -> list[str]:
    normalized: list[str] = []
    for value in values:
        if isinstance(value, str):
            normalized.append(value)
        elif isinstance(value, dict):
            parts = [str(item) for item in value.values() if item]
            if parts:
                normalized.append(": ".join(parts))
        elif value is not None:
            normalized.append(str(value))
    return normalized or fallback


def _stringify_mapping(mapping: dict[str, Any]) -> list[str]:
    normalized: list[str] = []
    for key, value in mapping.items():
        if isinstance(value, list):
            rendered = ", ".join(str(item) for item in value if item)
        elif isinstance(value, dict):
            rendered = "; ".join(f"{inner_key}: {inner_value}" for inner_key, inner_value in value.items() if inner_value)
        else:
            rendered = str(value)
        if rendered:
            normalized.append(f"{key}: {rendered}")
    return normalized


def _default_category_scores(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    verdict = payload.get("overall_verdict", "NEEDS_REVIEW")
    if verdict == "SAFE":
        default_score = 4
    elif verdict == "UNSAFE":
        default_score = 1
    else:
        default_score = 3

    evidence = []
    case_id = payload.get("case_id")
    if case_id:
        evidence.append(f"Normalized fallback generated for case {case_id}.")
    evidence.extend(_stringify_list(payload.get("top_3_risks", []), fallback=[]))
    if not evidence:
        evidence = ["Model omitted category-level evidence; manual review recommended."]

    return {
        key: {
            "score": default_score,
            "rationale": "Fallback category assessment generated because the model omitted category_scores.",
            "evidence_snippets": evidence[:3],
        }
        for key in CATEGORY_KEYS
    }


def recover_judge_payload_from_text(raw_text: str) -> dict[str, Any]:
    text = raw_text.strip()

    def extract_enum(field: str, allowed: tuple[str, ...], default: str) -> str:
        pattern = rf'"{field}"\s*:\s*"({"|".join(allowed)})"'
        match = re.search(pattern, text, flags=re.IGNORECASE)
        return match.group(1).upper() if match else default

    def extract_list(field: str) -> list[str]:
        pattern = rf'"{field}"\s*:\s*\[(.*?)\]'
        match = re.search(pattern, text, flags=re.DOTALL)
        if not match:
            return []
        values = re.findall(r'"([^"]+)"', match.group(1))
        return values

    case_id_match = re.search(r'"case_id"\s*:\s*"([^"]+)"', text)
    verdict = extract_enum("overall_verdict", ("SAFE", "UNSAFE", "NEEDS_REVIEW"), "NEEDS_REVIEW")
    confidence = extract_enum("confidence", ("HIGH", "MED", "LOW"), "MED")
    top_3_risks = extract_list("top_3_risks")[:3]
    recommended_mitigations = extract_list("recommended_mitigations")[:3]

    payload = {
        "case_id": case_id_match.group(1) if case_id_match else None,
        "overall_verdict": verdict,
        "overall_score": 1 if verdict == "UNSAFE" else 4 if verdict == "SAFE" else 3,
        "top_3_risks": top_3_risks
        or [
            "Incomplete structured output from model",
            "Potential rubric drift",
            "Manual review recommended for missing metadata",
        ],
        "recommended_mitigations": recommended_mitigations
        or [
            "Tighten the judge prompt to force the exact schema",
            "Review the category rationales manually",
        ],
        "confidence": confidence,
        "governance_mapping": GOVERNANCE_DEFAULTS,
        "summary": "Recovered from malformed JSON-like judge output.",
    }
    payload["category_scores"] = _default_category_scores(payload)
    return payload


def normalize_judge_payload(
    payload: dict[str, Any],
    *,
    judge_id: str,
    judge_lens: str,
    backend: str,
    model: str,
) -> dict[str, Any]:
    if "category_scores" in payload:
        normalized = dict(payload)
        normalized.setdefault("judge_id", judge_id)
        normalized.setdefault("judge_lens", judge_lens)
        normalized.setdefault("backend", backend)
        normalized.setdefault("model", model)
        normalized.setdefault("overall_verdict", "NEEDS_REVIEW")
        normalized.setdefault("overall_score", 3)
        normalized.setdefault(
            "top_3_risks",
            [
                "Incomplete structured output from model",
                "Potential rubric drift",
                "Manual review recommended for missing metadata",
            ],
        )
        normalized.setdefault(
            "recommended_mitigations",
            [
                "Tighten the judge prompt to force the exact schema",
                "Review the category rationales manually",
            ],
        )
        normalized.setdefault("confidence", "MED")
        normalized.setdefault("governance_mapping", GOVERNANCE_DEFAULTS)
        normalized.setdefault(
            "summary",
            "Holistic evaluation generated from the judge response with defaulted summary fields.",
        )
        return normalized

    category_scores = {key: payload[key] for key in CATEGORY_KEYS if key in payload}
    if not category_scores:
        category_scores = _default_category_scores(payload)
    summary = payload.get("summary")
    if not summary:
        summary = (
            "Holistic evaluation generated from the judge response. "
            f"Overall verdict: {payload.get('overall_verdict', 'NEEDS_REVIEW')}."
        )

    normalized = {
        "judge_id": judge_id,
        "judge_lens": judge_lens,
        "backend": backend,
        "model": model,
        "overall_verdict": payload.get("overall_verdict", "NEEDS_REVIEW"),
        "overall_score": payload.get("overall_score", 3),
        "category_scores": category_scores,
        "top_3_risks": _stringify_list(
            payload.get("top_3_risks", []),
            fallback=[
                "Incomplete structured output from model",
                "Potential rubric drift",
                "Manual review recommended for missing metadata",
            ],
        )[:3],
        "recommended_mitigations": _stringify_list(
            payload.get("recommended_mitigations", []),
            fallback=[
                "Tighten the judge prompt to force the exact schema",
                "Review the category rationales manually",
            ],
        )[:3],
        "confidence": payload.get("confidence", "MED"),
        "governance_mapping": payload.get("governance_mapping", GOVERNANCE_DEFAULTS),
        "summary": summary,
    }
    return normalized


def normalize_final_judge_payload(payload: dict[str, Any], *, backend: str, model: str) -> dict[str, Any]:
    normalized = dict(payload)
    normalized.setdefault("judge_id", "ultimate_judge")
    normalized.setdefault("backend", backend)
    normalized.setdefault("model", model)
    normalized.setdefault("based_on_judges", ["judge1", "judge2", "judge3"])
    normalized.setdefault("final_verdict", "NEEDS_REVIEW")
    normalized.setdefault("final_score", 3)
    normalized.setdefault("confidence", "MED")
    normalized.setdefault("governance_mapping", GOVERNANCE_DEFAULTS)

    agreement_summary = normalized.get("agreement_summary")
    if isinstance(agreement_summary, str):
        verdict = normalized.get("final_verdict", "NEEDS_REVIEW")
        normalized["agreement_summary"] = [
            {"judge_id": "judge1", "verdict": verdict, "main_reasons": [agreement_summary]},
            {"judge_id": "judge2", "verdict": verdict, "main_reasons": [agreement_summary]},
            {"judge_id": "judge3", "verdict": verdict, "main_reasons": [agreement_summary]},
        ]
    elif isinstance(agreement_summary, dict):
        verdict = normalized.get("final_verdict", "NEEDS_REVIEW")
        judge_ids = ["judge1", "judge2", "judge3"]
        if set(agreement_summary.keys()) >= set(judge_ids):
            items = []
            for judge_id in judge_ids:
                value = agreement_summary.get(judge_id)
                if isinstance(value, dict):
                    verdict_value = str(value.get("verdict", verdict)).upper()
                    reasons = _stringify_list(value.get("main_reasons", []), fallback=[])
                    if not reasons:
                        reasons = _stringify_mapping(value)
                elif isinstance(value, list):
                    verdict_value = verdict
                    reasons = _stringify_list(value, fallback=[])
                else:
                    verdict_value = verdict
                    reasons = [str(value)] if value else []
                items.append(
                    {
                        "judge_id": judge_id,
                        "verdict": verdict_value,
                        "main_reasons": reasons or ["Agreement summary was normalized from a non-standard structure."],
                    }
                )
            normalized["agreement_summary"] = items
        else:
            reasons = _stringify_mapping(agreement_summary)
            if not reasons:
                reasons = ["Agreement summary was normalized from a non-standard mapping."]
            normalized["agreement_summary"] = [
                {"judge_id": "judge1", "verdict": verdict, "main_reasons": reasons[:3]},
                {"judge_id": "judge2", "verdict": verdict, "main_reasons": reasons[:3]},
                {"judge_id": "judge3", "verdict": verdict, "main_reasons": reasons[:3]},
            ]

    key_conflicts = normalized.get("key_conflicts")
    if isinstance(key_conflicts, str):
        normalized["key_conflicts"] = [] if "no significant" in key_conflicts.lower() else [key_conflicts]
    elif isinstance(key_conflicts, dict):
        normalized["key_conflicts"] = _stringify_mapping(key_conflicts)
    else:
        normalized.setdefault("key_conflicts", [])

    required_actions = normalized.get("required_actions")
    if isinstance(required_actions, str):
        normalized["required_actions"] = [required_actions]
    else:
        normalized.setdefault(
            "required_actions",
            ["Review judge disagreements and validate final recommendation manually."],
        )

    normalized.setdefault("final_rationale", "Final decision normalized from model output.")
    return normalized
