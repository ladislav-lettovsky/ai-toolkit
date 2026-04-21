from click.testing import CliRunner

from ai_cli.commands.templates import TEMPLATES
from ai_cli.main import cli


def test_templates_contains_agent_and_rag() -> None:
    assert "agent" in TEMPLATES
    assert "rag" in TEMPLATES


def test_template_descriptions_are_nonempty() -> None:
    for name, description in TEMPLATES.items():
        assert name.strip()
        assert description.strip()


def test_cli_group_has_all_commands() -> None:
    expected = {"clean", "doctor", "eval", "inspect", "list", "new", "run", "templates", "upgrade"}
    actual = set(cli.commands.keys())
    assert expected == actual, f"Missing commands: {expected - actual}, Extra: {actual - expected}"


def test_list_handles_missing_directory(tmp_path, monkeypatch) -> None:
    """list should not crash when ~/projects/ai does not exist."""
    import ai_cli.constants

    monkeypatch.setattr(ai_cli.constants, "PROJECTS_ROOT", tmp_path / "nonexistent")

    # Re-import to pick up the monkeypatched constant
    import ai_cli.commands.list as list_mod

    monkeypatch.setattr(list_mod, "PROJECTS_ROOT", tmp_path / "nonexistent")

    runner = CliRunner()
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "No projects directory found" in result.output
