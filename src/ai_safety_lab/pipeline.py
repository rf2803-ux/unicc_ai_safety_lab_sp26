from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_safety_lab.final_judge import UltimateJudge
from ai_safety_lab.judges import Judge1, Judge2, Judge3
from ai_safety_lab.reporting.make_report_pdf import generate_report_pdf
from ai_safety_lab.schemas import CaseFile, FinalJudgeOutput, JudgeOutput
from ai_safety_lab.settings import AppConfig
from ai_safety_lab.utils.files import ensure_directory
from ai_safety_lab.utils.json_io import write_json
from ai_safety_lab.utils.timestamps import utc_timestamp_for_path


@dataclass
class RunResult:
    run_dir: Path
    case_file_path: Path
    judge_output_paths: dict[str, Path]
    final_judge_path: Path
    report_pdf_path: Path
    run_metadata_path: Path
    judge_outputs: list[JudgeOutput]
    final_output: FinalJudgeOutput


def evaluate_case(case_file: CaseFile, settings: AppConfig) -> RunResult:
    run_dir = ensure_directory(Path(settings.default_output_dir) / utc_timestamp_for_path())
    case_file_path = run_dir / "case_file.json"
    write_json(case_file_path, case_file.model_dump(mode="json"))

    judge_specs = [
        ("judge1", Judge1, settings.providers["judge1"]),
        ("judge2", Judge2, settings.providers["judge2"]),
        ("judge3", Judge3, settings.providers["judge3"]),
    ]
    judge_outputs: list[JudgeOutput] = []
    judge_output_paths: dict[str, Path] = {}
    for judge_id, judge_cls, provider in judge_specs:
        judge = judge_cls(backend=provider.backend, model=provider.model)
        output = judge.evaluate(case_file)
        judge_outputs.append(output)
        output_path = run_dir / f"{judge_id}.json"
        write_json(output_path, output.model_dump(mode="json"))
        judge_output_paths[judge_id] = output_path

    ultimate_provider = settings.providers["ultimate_judge"]
    ultimate_judge = UltimateJudge(backend=ultimate_provider.backend, model=ultimate_provider.model)
    final_output = ultimate_judge.evaluate(judge_outputs)
    final_judge_path = run_dir / "final_judge.json"
    write_json(final_judge_path, final_output.model_dump(mode="json"))

    report_pdf_path = run_dir / "report.pdf"
    generate_report_pdf(
        output_path=report_pdf_path,
        case_file=case_file,
        judge_outputs=judge_outputs,
        final_output=final_output,
        settings=settings,
    )

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
        "input_case_id": case_file.case_id,
        "input_target_model": case_file.target_model,
    }
    run_metadata_path = run_dir / "run_metadata.json"
    write_json(run_metadata_path, metadata)

    return RunResult(
        run_dir=run_dir,
        case_file_path=case_file_path,
        judge_output_paths=judge_output_paths,
        final_judge_path=final_judge_path,
        report_pdf_path=report_pdf_path,
        run_metadata_path=run_metadata_path,
        judge_outputs=judge_outputs,
        final_output=final_output,
    )
