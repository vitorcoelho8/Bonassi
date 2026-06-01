MATCH_PHASES = {
    "GROUP_STAGE": {
        "label": "Fase de grupos",
        "round_order": 1,
    },
    "ROUND_OF_32": {
        "label": "Segunda fase",
        "round_order": 2,
    },
    "ROUND_OF_16": {
        "label": "Oitavas de final",
        "round_order": 3,
    },
    "QUARTER_FINAL": {
        "label": "Quartas de final",
        "round_order": 4,
    },
    "SEMI_FINAL": {
        "label": "Semifinal",
        "round_order": 5,
    },
    "FINAL": {
        "label": "Final",
        "round_order": 6,
    },
    "THIRD_PLACE": {
        "label": "Disputa de 3o lugar",
        "round_order": 6,
    },
}

DEFAULT_MATCH_PHASE = "GROUP_STAGE"


def normalize_phase(value: str | None) -> str:
    phase = str(value or DEFAULT_MATCH_PHASE).strip().upper()
    if phase not in MATCH_PHASES:
        raise ValueError("Fase da partida invalida.")

    return phase


def phase_label(phase: str | None) -> str | None:
    return MATCH_PHASES.get(str(phase or "").upper(), {}).get("label")


def phase_round_order(phase: str | None) -> int | None:
    return MATCH_PHASES.get(str(phase or "").upper(), {}).get("round_order")


def is_knockout_phase(phase: str | None) -> bool:
    return normalize_phase(phase) != DEFAULT_MATCH_PHASE
