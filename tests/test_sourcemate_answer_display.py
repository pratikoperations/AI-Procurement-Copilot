from modules.sourcemate_answer_display import format_sourcemate_answer_for_display


def test_tco_project_answer_is_rendered_as_compact_tables_without_changing_values():
    answer = (
        "Verified project evidence — total cost of ownership:\n"
        "The packaging TCO model starts from quoted unit price and separately adds scenario price exposure, freight, "
        "inventory carrying cost, working-capital impact, risk penalty and a lead-time buffer. Default parameters are: "
        "raw-material exposure 60%, cost of capital 12%, inventory carrying rate 18%, maximum freight exposure 6%, "
        "maximum failure probability 20%, and business-impact multiplier 50%. Lead-time buffers are 0% up to 21 days, "
        "0.3% above 21 days, 0.75% above 30 days and 1.5% above 45 days. Incoterm freight exposure is DDP 0%, "
        "DAP 20% of maximum, CIF 35%, FOB 75%, EXW 100%, and unknown 60% of maximum. "
        "These are model assumptions, not universal market standards."
    )

    rendered = format_sourcemate_answer_for_display(answer, "project_knowledge")

    assert "**Total cost of ownership (TCO)**" in rendered
    assert "| TCO parameter | Governed default |" in rendered
    assert "| Raw-material exposure | 60% |" in rendered
    assert "| Cost of capital | 12% |" in rendered
    assert "| Inventory carrying rate | 18% |" in rendered
    assert "| Maximum freight exposure | 6% |" in rendered
    assert "| Maximum failure probability | 20% |" in rendered
    assert "| Business-impact multiplier | 50% |" in rendered
    assert "| Up to 21 days | 0% |" in rendered
    assert "| >45 days | 1.5% |" in rendered
    assert "| DAP | 20% of maximum |" in rendered
    assert "| EXW | 100% |" in rendered
    assert "not universal market standards" in rendered
    assert "does not recalculate TCO" in rendered


def test_non_tco_answer_is_not_rewritten():
    answer = "Verified project evidence — supplier risk: deterministic governed logic."
    assert format_sourcemate_answer_for_display(answer, "project_knowledge") == answer


def test_tco_text_is_not_rewritten_for_a_different_intent():
    answer = "total cost of ownership"
    assert format_sourcemate_answer_for_display(answer, "glossary") == answer
