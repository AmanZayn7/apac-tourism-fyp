import json

from stis.config import ROOT


def test_all_nine_corrected_notebooks_have_successful_executed_evidence():
    original = {p.name for p in (ROOT / "legacy/notebooks").glob("*.ipynb")}
    corrected = {p.name for p in (ROOT / "notebooks").glob("*.ipynb")}
    assert len(original) == 9
    assert original == corrected
    for path in (ROOT / "notebooks").glob("*.ipynb"):
        notebook = json.loads(path.read_text())
        code = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
        assert all(cell["execution_count"] is not None for cell in code), path.name
        outputs = [output for cell in code for output in cell["outputs"]]
        assert all(output["output_type"] != "error" for output in outputs), path.name
        text = "".join("".join(output.get("text", [])) for output in outputs)
        assert "PASS: all seven forecasts and validation MAEs match" in text, path.name
        assert "PASS: feature causality" in text, path.name
        assert any("image/png" in output.get("data", {}) for output in outputs), path.name
        assert sum(cell["cell_type"] == "markdown" for cell in notebook["cells"]) >= 7
