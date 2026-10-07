import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

from core.feature_schema import (
    DEFAULT_FEATURES, DEPLOYMENT_SCHEMA, FEATURE_NAMES, FEATURE_OPTIONS, INITIAL_BELIEF,
    OPTIMAL_KNOWLEDGE_BASE, TRAIN_ROWS, TEST_ROWS, validate_features,
)
from core.ds_engine import DSEngine
from core.model_validator import validate_knowledge_base

engine = validate_knowledge_base(OPTIMAL_KNOWLEDGE_BASE)


class FeatureTests(unittest.TestCase):
    def test_schema_is_derived_from_research_datasets(self):
        self.assertEqual(len(FEATURE_OPTIONS), 13)
        expected_size = DEPLOYMENT_SCHEMA["dataset_size"]
        if TRAIN_ROWS and TEST_ROWS:
            self.assertEqual(len(TRAIN_ROWS), expected_size["train"])
            self.assertEqual(len(TEST_ROWS), expected_size["test"])
        else:
            self.assertEqual(expected_size, {"train": 736, "test": 185})
        self.assertEqual(tuple(FEATURE_OPTIONS), FEATURE_NAMES)

    def test_belief_and_optimal_rules_have_identical_evidence(self):
        initial = {(r["symptom_col"], r["symptom_val"]) for r in INITIAL_BELIEF["rules"]}
        optimal = {(r["symptom_col"], r["symptom_val"]) for r in OPTIMAL_KNOWLEDGE_BASE["rules"]}
        self.assertEqual(initial, optimal)
        self.assertEqual(len(optimal), 19)
        self.assertIn(("Wifi", "Sinyal Lemah/Tidak Stabil"), optimal)
        self.assertIn(("Wifi", "Hilang Total/Tidak Dapat Diaktifkan"), optimal)
        self.assertIn(("Kamera", "Bergetar / OIS Tidak Stabil"), optimal)

    def test_invalid_provider_value_is_rejected(self):
        features, rejected = validate_features({"LCD": "Pasti Rusak"})
        self.assertEqual(features["LCD"], DEFAULT_FEATURES["LCD"])
        self.assertEqual(len(rejected), 1)


class DSEngineTests(unittest.TestCase):
    def test_runtime_priors_are_normalized(self):
        self.assertAlmostEqual(sum(engine.priors.values()), 1.0, places=9)

    def test_fallback_probability_is_normalized(self):
        result = engine.run_inference(DEFAULT_FEATURES)
        self.assertAlmostEqual(sum(x["probability"] for x in result["all_diagnoses"]), 1.0, places=3)

    def test_active_evidence_metrics_are_bounded(self):
        features = DEFAULT_FEATURES.copy()
        features["LCD"] = "Gelap"
        result = engine.run_inference(features)
        self.assertGreater(result["active_rules_count"], 0)
        self.assertTrue(0 <= result["uncertainty_theta"] <= 1)
        self.assertAlmostEqual(sum(result["dev_log"]["pignistic_probabilities"].values()), 1.0, places=3)
        top = result["top_diagnosis"]
        self.assertLessEqual(result["belief"][top], result["plausibility"][top])

    def test_high_uncertainty_evidence_is_exposed(self):
        features = DEFAULT_FEATURES.copy()
        features["Tombol"] = "Tidak Berfungsi"
        result = engine.run_inference(features)
        self.assertGreaterEqual(result["uncertainty_theta"], 0.2)

    def test_two_evidences_produce_two_distinct_clinical_topics(self):
        from core.clinical_knowledge import build_clinical_knowledge
        features = DEFAULT_FEATURES.copy()
        features["Touchscreen"] = "Tidak bisa disentuh"
        features["Konektor Cas"] = "Keluar masuk"
        result = engine.run_inference(features)
        topics = build_clinical_knowledge(result, "iPhone 11")
        self.assertEqual([item["damage"] for item in topics], ["LCD Rusak", "Port Pengisian Rusak"])

    def test_manual_two_evidence_combination(self):
        theta = engine.Theta
        first = {frozenset([engine.all_damages[0]]): 0.6, theta: 0.4}
        second = {frozenset([engine.all_damages[0]]): 0.5, theta: 0.5}
        combined, conflict = engine._combine_two(first, second)
        self.assertAlmostEqual(conflict, 0.0)
        self.assertAlmostEqual(combined[frozenset([engine.all_damages[0]])], 0.8)
        self.assertAlmostEqual(combined[theta], 0.2)

    def test_total_conflict_is_explicit(self):
        first = {frozenset([engine.all_damages[0]]): 1.0}
        second = {frozenset([engine.all_damages[1]]): 1.0}
        combined, conflict = engine._combine_two(first, second)
        self.assertEqual(conflict, 1.0)
        self.assertEqual(combined, {engine.Theta: 1.0})


class ModelValidationTests(unittest.TestCase):
    def test_production_model_matches_runtime_contract(self):
        validated = validate_knowledge_base(OPTIMAL_KNOWLEDGE_BASE)
        self.assertEqual(validated.all_damages, engine.all_damages)

    def test_model_with_unknown_class_is_rejected(self):
        candidate = json.loads(json.dumps(OPTIMAL_KNOWLEDGE_BASE))
        candidate["class_priors"]["Unknown Damage"] = 0.01
        with self.assertRaisesRegex(ValueError, "Kelas model"):
            validate_knowledge_base(candidate)

    def test_model_with_changed_evidence_is_rejected(self):
        candidate = json.loads(json.dumps(OPTIMAL_KNOWLEDGE_BASE))
        candidate["rules"][0]["symptom_val"] = "Normal"
        with self.assertRaisesRegex(ValueError, "Pasangan evidence"):
            validate_knowledge_base(candidate)

    def test_model_with_invalid_metadata_is_rejected(self):
        candidate = json.loads(json.dumps(OPTIMAL_KNOWLEDGE_BASE))
        candidate["metadata"] = "invalid"
        with self.assertRaisesRegex(ValueError, "Metadata"):
            validate_knowledge_base(candidate)

    def test_corrupt_model_pointer_falls_back_to_default(self):
        from core import clinical_knowledge
        with tempfile.TemporaryDirectory() as temp_dir:
            pointer_path = os.path.join(temp_dir, "active_model.json")
            with open(pointer_path, "w", encoding="utf-8") as pointer_file:
                pointer_file.write("not-json")
            with patch.object(clinical_knowledge, "MODEL_POINTER_PATH", pointer_path):
                self.assertEqual(
                    clinical_knowledge.selected_knowledge_base_path(), clinical_knowledge.DEFAULT_KB_PATH
                )


if __name__ == "__main__":
    unittest.main()
