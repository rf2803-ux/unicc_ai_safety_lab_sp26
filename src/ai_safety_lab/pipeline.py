from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import re

from ai_safety_lab.adapters import system_case_from_case_file
from ai_safety_lab.clients import ProviderResponseError
from ai_safety_lab.final_judge import UltimateJudge
from ai_safety_lab.judges import Judge1, Judge2, Judge3
from ai_safety_lab.reporting.make_report_pdf import generate_report_pdf
from ai_safety_lab.schemas import CaseFile, FinalJudgeOutput, JudgeOutput, SystemCase
from ai_safety_lab.settings import AppConfig
from ai_safety_lab.utils.files import ensure_directory
from ai_safety_lab.utils.json_io import write_json
from ai_safety_lab.utils.timestamps import utc_timestamp_for_path


@dataclass
class RunResult:
    run_dir: Path
    system_case_path: Path
    extra_artifact_paths: dict[str, Path]
    judge_output_paths: dict[str, Path]
    final_judge_path: Path
    report_pdf_path: Path
    report_download_name: str
    run_metadata_path: Path
    execution_trace_path: Path
    judge_outputs: list[JudgeOutput]
    final_output: FinalJudgeOutput


def _safe_report_stem(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", value.strip())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or "system"


def _report_filename(system_case: SystemCase) -> str:
    system_name = _safe_report_stem(system_case.title or system_case.case_id)
    report_date = system_case.created_at.date().isoformat()
    return f"reportEVALUATION_{system_name}_{report_date}.pdf"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_execution_trace(path: Path, trace: dict[str, Any]) -> None:
    write_json(path, trace)


def evaluate_system_case(
    system_case: SystemCase,
    settings: AppConfig,
    *,
    extra_artifacts: dict[str, Any] | None = None,
) -> RunResult:
    run_dir = ensure_directory(Path(settings.default_output_dir) / utc_timestamp_for_path())
    system_case_path = run_dir / "system_case.json"
    write_json(system_case_path, system_case.model_dump(mode="json"))
    extra_artifact_paths: dict[str, Path] = {}
    execution_trace_path = run_dir / "execution_trace.json"
    execution_trace: dict[str, Any] = {
        "run_id": run_dir.name,
        "started_at": _utc_now(),
        "status": "running",
        "input": {
            "case_id": system_case.case_id,
            "target_type": system_case.target_type,
            "target_label": system_case.title,
            "source_url": system_case.source_url,
        },
        "stages": [],
    }
    _write_execution_trace(execution_trace_path, execution_trace)

    for artifact_name, artifact_data in (extra_artifacts or {}).items():
        artifact_path = run_dir / f"{artifact_name}.json"
        write_json(artifact_path, artifact_data)
        extra_artifact_paths[artifact_name] = artifact_path

    judge_specs = [
        ("judge1", Judge1, settings.providers["judge1"]),
        ("judge2", Judge2, settings.providers["judge2"]),
        ("judge3", Judge3, settings.providers["judge3"]),
    ]
    judge_outputs: list[JudgeOutput] = []
    judge_output_paths: dict[str, Path] = {}
    for judge_id, judge_cls, provider in judge_specs:
        stage_entry = {
            "stage": judge_id,
            "type": "expert_reviewer",
            "backend": provider.backend,
            "model": provider.model,
            "started_at": _utc_now(),
            "status": "running",
        }
        execution_trace["stages"].append(stage_entry)
        _write_execution_trace(execution_trace_path, execution_trace)
        judge = judge_cls(backend=provider.backend, model=provider.model)
        try:
            output = judge.evaluate(system_case)
        except ProviderResponseError as exc:
            stage_entry["status"] = "failed"
            stage_entry["finished_at"] = _utc_now()
            stage_entry["error"] = str(exc)
            execution_trace["status"] = "failed"
            execution_trace["failed_stage"] = judge_id
            execution_trace["finished_at"] = _utc_now()
            _write_execution_trace(execution_trace_path, execution_trace)
            raise ProviderResponseError(
                f"{judge_id} ({provider.backend}/{provider.model}) failed: {exc}"
            ) from exc
        except Exception as exc:
            stage_entry["status"] = "failed"
            stage_entry["finished_at"] = _utc_now()
            stage_entry["error"] = str(exc)
            execution_trace["status"] = "failed"
            execution_trace["failed_stage"] = judge_id
            execution_trace["finished_at"] = _utc_now()
            _write_execution_trace(execution_trace_path, execution_trace)
            raise
        stage_entry["status"] = "completed"
        stage_entry["finished_at"] = _utc_now()
        judge_outputs.append(output)
        output_path = run_dir / f"{judge_id}.json"
        write_json(output_path, output.model_dump(mode="json"))
        judge_output_paths[judge_id] = output_path
        stage_entry["artifact"] = output_path.name
        _write_execution_trace(execution_trace_path, execution_trace)

    ultimate_provider = settings.providers["ultimate_judge"]
    final_stage = {
        "stage": "ultimate_judge",
        "type": "arbitration",
        "backend": ultimate_provider.backend,
        "model": ultimate_provider.model,
        "started_at": _utc_now(),
        "status": "running",
    }
    execution_trace["stages"].append(final_stage)
    _write_execution_trace(execution_trace_path, execution_trace)
    ultimate_judge = UltimateJudge(backend=ultimate_provider.backend, model=ultimate_provider.model)
    try:
        final_output = ultimate_judge.evaluate(judge_outputs)
    except ProviderResponseError as exc:
        final_stage["status"] = "failed"
        final_stage["finished_at"] = _utc_now()
        final_stage["error"] = str(exc)
        execution_trace["status"] = "failed"
        execution_trace["failed_stage"] = "ultimate_judge"
        execution_trace["finished_at"] = _utc_now()
        _write_execution_trace(execution_trace_path, execution_trace)
        raise ProviderResponseError(
            f"ultimate_judge ({ultimate_provider.backend}/{ultimate_provider.model}) failed: {exc}"
        ) from exc
    except Exception as exc:
        final_stage["status"] = "failed"
        final_stage["finished_at"] = _utc_now()
        final_stage["error"] = str(exc)
        execution_trace["status"] = "failed"
        execution_trace["failed_stage"] = "ultimate_judge"
        execution_trace["finished_at"] = _utc_now()
        _write_execution_trace(execution_trace_path, execution_trace)
        raise
    final_stage["status"] = "completed"
    final_stage["finished_at"] = _utc_now()
    final_judge_path = run_dir / "final_judge.json"
    write_json(final_judge_path, final_output.model_dump(mode="json"))
    final_stage["artifact"] = final_judge_path.name
    _write_execution_trace(execution_trace_path, execution_trace)

    report_download_name = _report_filename(system_case)
    report_pdf_path = run_dir / report_download_name
    report_stage = {
        "stage": "report_generation",
        "type": "reporting",
        "artifact": report_download_name,
        "started_at": _utc_now(),
        "status": "running",
    }
    execution_trace["stages"].append(report_stage)
    _write_execution_trace(execution_trace_path, execution_trace)
    try:
        generate_report_pdf(
            output_path=report_pdf_path,
            system_case=system_case,
            judge_outputs=judge_outputs,
            final_output=final_output,
            settings=settings,
        )
    except Exception as exc:
        report_stage["status"] = "failed"
        report_stage["finished_at"] = _utc_now()
        report_stage["error"] = str(exc)
        execution_trace["status"] = "failed"
        execution_trace["failed_stage"] = "report_generation"
        execution_trace["finished_at"] = _utc_now()
        _write_execution_trace(execution_trace_path, execution_trace)
        raise
    report_stage["status"] = "completed"
    report_stage["finished_at"] = _utc_now()
    _write_execution_trace(execution_trace_path, execution_trace)

    primary_model = system_case.capability_profile.model_backends[0] if system_case.capability_profile.model_backends else "unknown"

    metadata = {
        "run_id": run_dir.name,
        "timestamp": run_dir.name,
        "app_version": "0.1.0",
        "config_snapshot": settings.model_dump(mode="json"),
        "judge_backends": {
            **{name: provider.backend for name, _, provider in judge_specs},
            "ultimate_judge": ultimate_provider.backend,
        },
        "models": {
            **{name: provider.model for name, _, provider in judge_specs},
            "ultimate_judge": ultimate_provider.model,
        },
        "input_case_id": system_case.case_id,
        "input_target_type": system_case.target_type,
        "input_target_label": system_case.title,
        "input_target_model": primary_model,
        "source_url": system_case.source_url,
    }
    run_metadata_path = run_dir / "run_metadata.json"
    write_json(run_metadata_path, metadata)
    run_summary_path = run_dir / "run_summary.json"
    write_json(
        run_summary_path,
        {
            "run_id": run_dir.name,
            "status": "completed",
            "input_target_type": system_case.target_type,
            "input_target_label": system_case.title,
            "source_url": system_case.source_url,
            "judge_stages": [
                {
                    "stage": stage["stage"],
                    "status": stage["status"],
                    "backend": stage.get("backend"),
                    "model": stage.get("model"),
                }
                for stage in execution_trace["stages"]
                if stage["type"] in {"expert_reviewer", "arbitration"}
            ],
            "report_artifact": report_download_name,
            "final_verdict": final_output.final_verdict,
            "final_score": final_output.final_score,
        },
    )
    extra_artifact_paths["execution_trace"] = execution_trace_path
    extra_artifact_paths["run_summary"] = run_summary_path
    execution_trace["status"] = "completed"
    execution_trace["finished_at"] = _utc_now()
    _write_execution_trace(execution_trace_path, execution_trace)

    return RunResult(
        run_dir=run_dir,
        system_case_path=system_case_path,
        extra_artifact_paths=extra_artifact_paths,
        judge_output_paths=judge_output_paths,
        final_judge_path=final_judge_path,
        report_pdf_path=report_pdf_path,
        report_download_name=report_download_name,
        run_metadata_path=run_metadata_path,
        execution_trace_path=execution_trace_path,
        judge_outputs=judge_outputs,
        final_output=final_output,
    )


def evaluate_case(case_file: CaseFile, settings: AppConfig) -> RunResult:
    return evaluate_system_case(system_case_from_case_file(case_file), settings)
