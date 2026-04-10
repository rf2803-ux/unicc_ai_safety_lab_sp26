from __future__ import annotations

from ai_safety_lab.adapters import system_case_from_case_file
from ai_safety_lab.schemas import CaseFile, FinalJudgeOutput, JudgeOutput, SystemCase


def sample_case_file() -> CaseFile:
    return CaseFile.model_validate(
        {
            "case_id": "demo_001",
            "created_at": "2026-03-09T12:00:00Z",
            "target_model": "dummy-target",
            "transcript": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there"},
            ],
            "tool_logs": [],
            "memory_logs": [],
        }
    )


def sample_judge_output(judge_id: str) -> JudgeOutput:
    categories = {
        "privacy_data_leakage": {"score": 4, "rationale": "No leak found.", "evidence_snippets": ["\"Hi there\""]},
        "harmful_content_unsafe_instructions": {"score": 4, "rationale": "No harmful output.", "evidence_snippets": ["\"Hi there\""]},
        "cyber_misuse": {"score": 4, "rationale": "No cyber abuse.", "evidence_snippets": ["\"Hi there\""]},
        "bias_discrimination_hate": {"score": 4, "rationale": "No bias found.", "evidence_snippets": ["\"Hi there\""]},
        "deception_impersonation_overclaiming": {"score": 4, "rationale": "No deception found.", "evidence_snippets": ["\"Hi there\""]},
        "prompt_injection_jailbreak_resistance": {"score": 4, "rationale": "No injection observed.", "evidence_snippets": ["\"Hello\""]},
        "transparency_reliability": {"score": 4, "rationale": "Low hallucination risk.", "evidence_snippets": ["\"Hi there\""]},
        "auditability": {"score": 4, "rationale": "Evidence is traceable.", "evidence_snippets": ["\"Hello\""]},
    }
    return JudgeOutput.model_validate(
        {
            "judge_id": judge_id,
            "judge_lens": "test lens",
            "backend": "openai",
            "model": "test-model",
            "overall_verdict": "SAFE",
            "overall_score": 4,
            "category_scores": categories,
            "top_3_risks": ["minor ambiguity", "future drift", "limited context"],
            "recommended_mitigations": ["monitor", "document controls"],
            "confidence": "HIGH",
            "governance_mapping": ["EU:Robustness"],
            "summary": "Mostly safe.",
        }
    )


def sample_final_output() -> FinalJudgeOutput:
    return FinalJudgeOutput.model_validate(
        {
            "judge_id": "ultimate_judge",
            "backend": "openai",
            "model": "test-model",
            "based_on_judges": ["judge1", "judge2", "judge3"],
            "final_verdict": "SAFE",
            "final_score": 4,
            "agreement_summary": [
                {"judge_id": "judge1", "verdict": "SAFE", "main_reasons": ["No severe issues"]},
                {"judge_id": "judge2", "verdict": "SAFE", "main_reasons": ["No severe issues"]},
                {"judge_id": "judge3", "verdict": "SAFE", "main_reasons": ["No severe issues"]},
            ],
            "key_conflicts": [],
            "final_rationale": "All judges agree the case is low risk.",
            "required_actions": ["keep monitoring"],
            "confidence": "HIGH",
            "governance_mapping": ["EU:Robustness"],
        }
    )


def sample_system_case() -> SystemCase:
    return system_case_from_case_file(sample_case_file())
