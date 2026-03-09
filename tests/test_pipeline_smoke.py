from __future__ import annotations

from pathlib import Path

from ai_safety_lab import pipeline as pipeline_module
from ai_safety_lab.settings import load_app_config
from tests.helpers import sample_case_file, sample_final_output, sample_judge_output


class FakeJudge:
    judge_id = "judge1"

    def __init__(self, backend: str, model: str):
        self.backend = backend
        self.model = model

    def evaluate(self, case_file):
        return sample_judge_output(self.judge_id)


class FakeJudge2(FakeJudge):
    judge_id = "judge2"


class FakeJudge3(FakeJudge):
    judge_id = "judge3"


class FakeUltimateJudge:
    def __init__(self, backend: str, model: str):
        self.backend = backend
        self.model = model

    def evaluate(self, judge_outputs):
        return sample_final_output()


def test_pipeline_creates_expected_artifacts(tmp_path: Path, monkeypatch) -> None:
    config = load_app_config()
    config.default_output_dir = str(tmp_path)

    monkeypatch.setattr(pipeline_module, "Judge1", FakeJudge)
    monkeypatch.setattr(pipeline_module, "Judge2", FakeJudge2)
    monkeypatch.setattr(pipeline_module, "Judge3", FakeJudge3)
    monkeypatch.setattr(pipeline_module, "UltimateJudge", FakeUltimateJudge)

    result = pipeline_module.evaluate_case(sample_case_file(), config)

    assert result.case_file_path.exists()
    assert result.final_judge_path.exists()
    assert result.report_pdf_path.exists()
    assert result.run_metadata_path.exists()
    assert all(path.exists() for path in result.judge_output_paths.values())
