"""Presentation-only formatting helpers for SourceMate answers.

These helpers restructure existing deterministic SourceMate answer text for
readability. They do not calculate, infer, retrieve or mutate procurement data.
"""
from __future__ import annotations

import re


_TCO_DEFAULTS = re.compile(
    r"raw-material exposure (?P<raw>[\d.]+%), cost of capital (?P<capital>[\d.]+%), "
    r"inventory carrying rate (?P<inventory>[\d.]+%), maximum freight exposure (?P<freight>[\d.]+%), "
    r"maximum failure probability (?P<failure>[\d.]+%), and business-impact multiplier (?P<impact>[\d.]+%)"
)
_TCO_LEAD_TIME = re.compile(
    r"Lead-time buffers are (?P<up21>[\d.]+%) up to 21 days, (?P<over21>[\d.]+%) above 21 days, "
    r"(?P<over30>[\d.]+%) above 30 days and (?P<over45>[\d.]+%) above 45 days"
)
_TCO_INCOTERM = re.compile(
    r"Incoterm freight exposure is DDP (?P<ddp>[\d.]+%), DAP (?P<dap>[\d.]+%) of maximum, "
    r"CIF (?P<cif>[\d.]+%), FOB (?P<fob>[\d.]+%), EXW (?P<exw>[\d.]+%), and unknown (?P<unknown>[\d.]+%) of maximum"
)


def _table(headers: tuple[str, ...], rows: tuple[tuple[str, ...], ...]) -> str:
    head = "| " + " | ".join(headers) + " |"
    separator = "|" + "|".join("---" for _ in headers) + "|"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([head, separator, *body])


def _format_tco_answer(answer: str) -> str | None:
    defaults = _TCO_DEFAULTS.search(answer)
    lead_time = _TCO_LEAD_TIME.search(answer)
    incoterm = _TCO_INCOTERM.search(answer)
    if not (defaults and lead_time and incoterm):
        return None

    overview = answer.split("Default parameters are:", 1)[0].strip()
    overview = overview.replace("Verified project evidence — total cost of ownership:", "").strip()

    defaults_table = _table(
        ("TCO parameter", "Governed default"),
        (
            ("Raw-material exposure", f"{defaults.group('raw')}%"),
            ("Cost of capital", f"{defaults.group('capital')}%"),
            ("Inventory carrying rate", f"{defaults.group('inventory')}%"),
            ("Maximum freight exposure", f"{defaults.group('freight')}%"),
            ("Maximum failure probability", f"{defaults.group('failure')}%"),
            ("Business-impact multiplier", f"{defaults.group('impact')}%"),
        ),
    )
    lead_time_table = _table(
        ("Lead-time band", "Buffer"),
        (
            ("Up to 21 days", lead_time.group("up21")),
            (">21 days", lead_time.group("over21")),
            (">30 days", lead_time.group("over30")),
            (">45 days", lead_time.group("over45")),
        ),
    )
    incoterm_table = _table(
        ("Incoterm", "Freight exposure"),
        (
            ("DDP", incoterm.group("ddp")),
            ("DAP", f"{incoterm.group('dap')} of maximum"),
            ("CIF", incoterm.group("cif")),
            ("FOB", incoterm.group("fob")),
            ("EXW", incoterm.group("exw")),
            ("Unknown", f"{incoterm.group('unknown')} of maximum"),
        ),
    )

    return (
        "**Total cost of ownership (TCO)**\n\n"
        + overview
        + "\n\n**Default model parameters**\n\n"
        + defaults_table
        + "\n\n**Lead-time buffers**\n\n"
        + lead_time_table
        + "\n\n**Incoterm freight exposure**\n\n"
        + incoterm_table
        + "\n\n*These are governed portfolio model assumptions, not universal market standards. SourceMate only explains registered logic; it does not recalculate TCO.*"
    )


def format_sourcemate_answer_for_display(answer: str, intent: str | None = None) -> str:
    """Return a more readable representation without changing answer semantics."""
    text = str(answer or "")
    if intent == "project_knowledge" and "total cost of ownership" in text.casefold():
        structured = _format_tco_answer(text)
        if structured:
            return structured
    return text
