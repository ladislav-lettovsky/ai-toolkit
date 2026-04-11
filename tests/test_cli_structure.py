from ai_cli.commands.templates import TEMPLATES


def test_templates_contains_agent_and_rag() -> None:
    assert "agent" in TEMPLATES
    assert "rag" in TEMPLATES


def test_template_descriptions_are_nonempty() -> None:
    for name, description in TEMPLATES.items():
        assert name.strip()
        assert description.strip()
