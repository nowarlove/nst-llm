"""
Layanan Pengetahuan Klinis Kerusakan iPhone.
Menghubungkan hasil diagnosis Dempster-Shafer dengan rekomendasi teknis
dan estimasi biaya dari basis pengetahuan pakar (expertDiagnosesAndFix.json).
"""

import copy
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_KB_PATH = str(DATA_DIR / "optimal_knowledge_base.json")
MODEL_POINTER_PATH = str(DATA_DIR / "active_model.json")
EXPERT_DB_PATH = str(DATA_DIR / "expertDiagnosesAndFix.json")


def selected_knowledge_base_path():
    if not os.path.exists(MODEL_POINTER_PATH):
        return DEFAULT_KB_PATH
    try:
        with open(MODEL_POINTER_PATH, "r", encoding="utf-8") as pointer_file:
            relative = json.load(pointer_file).get("path", "")
        candidate = os.path.abspath(os.path.join(BASE_DIR, relative))
        allowed = os.path.abspath(os.path.join(DATA_DIR, "models")) + os.sep
        return candidate if candidate.startswith(allowed) and os.path.isfile(candidate) else DEFAULT_KB_PATH
    except (ValueError, OSError):
        return DEFAULT_KB_PATH


def _load_expert_db():
    if os.path.exists(EXPERT_DB_PATH):
        with open(EXPERT_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def apply_dynamic_price(expert_advice, damage_class, phone_type, store=None):
    advice = copy.deepcopy(expert_advice) if expert_advice else expert_advice
    if not advice or not store or not hasattr(store, "resolve_price"):
        return advice
    try:
        price = store.resolve_price(damage_class, phone_type)
    except Exception:
        price = None
    if not price:
        return advice
    minimum = int(price["minimum_price"])
    maximum = int(price["maximum_price"])
    advice["estimasi_biaya"] = {
        "rentang": f"Rp {minimum:,.0f} - Rp {maximum:,.0f}".replace(",", "."),
        "rincian": {price["service_name"]: f"Rp {minimum:,.0f} - Rp {maximum:,.0f}".replace(",", ".")},
        "sumber": "database",
        "catatan": price.get("notes") or "",
    }
    return advice


def build_clinical_knowledge(result, phone_type, expert_db=None, store=None):
    """Membangun ringkasan klinis perbaikan untuk setiap evidence aktif."""
    if expert_db is None:
        expert_db = _load_expert_db()

    selected = []
    for rule in result.get("dev_log", {}).get("active_rules", []):
        hypotheses = [
            hypothesis for hypothesis in rule.get("hypotheses", [])
            if float(hypothesis.get("optimal_belief", 0)) > 0
        ]
        if not hypotheses:
            continue
        damage = max(hypotheses, key=lambda item: float(item.get("optimal_belief", 0))).get("damage")
        if damage and damage not in selected:
            selected.append(damage)

    distribution = {item["damage"]: item for item in result.get("all_diagnoses", [])}
    selected.sort(key=lambda damage: distribution.get(damage, {}).get("probability", 0), reverse=True)
    knowledge = []
    for damage in selected:
        advice = apply_dynamic_price(expert_db.get("kerusakan", {}).get(damage), damage, phone_type, store)
        if advice:
            probability = distribution.get(damage, {})
            knowledge.append({
                "damage": damage,
                "probability": probability.get("probability", 0),
                "percentage": probability.get("percentage", 0),
                "advice": advice,
            })
    return knowledge
