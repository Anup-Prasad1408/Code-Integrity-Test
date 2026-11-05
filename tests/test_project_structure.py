from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_entrypoint_exists():
    assert (ROOT / "app.py").is_file()


def test_required_project_directories_exist():
    expected = [
        "engines",
        "analyzers",
        "parsers",
        "models",
        "utils",
        "datasets",
        "tests",
    ]
    for directory in expected:
        assert (ROOT / directory).is_dir()


def test_no_real_environment_file_is_included():
    assert not (ROOT / ".env").exists()
    assert (ROOT / ".env.example").is_file()
