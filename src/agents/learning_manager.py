import json
import os
from typing import Dict, Any

class LearningManager:
    def __init__(self, model_path: str = "models/learning_patterns.json"):
        self.model_path = model_path
        self.pattern_stats: Dict[str, Dict[str, int]] = self._load_patterns()

    def _load_patterns(self) -> Dict[str, Dict[str, int]]:
        if os.path.exists(self.model_path):
            with open(self.model_path, "r") as f:
                return json.load(f)
        return {}

    def record_success(self, field: str, pattern: str):
        if field not in self.pattern_stats:
            self.pattern_stats[field] = {}
        if pattern not in self.pattern_stats[field]:
            self.pattern_stats[field][pattern] = 0
        self.pattern_stats[field][pattern] += 1
        self._save_patterns()

    def get_top_patterns(self, field: str, top_n: int = 3):
        if field not in self.pattern_stats:
            return []
        sorted_patterns = sorted(self.pattern_stats[field].items(), key=lambda x: x[1], reverse=True)
        return [p[0] for p in sorted_patterns[:top_n]]

    def record_feedback(self, field: str, pattern: str, correct: bool):
        if field not in self.pattern_stats:
            self.pattern_stats[field] = {}
        if pattern not in self.pattern_stats[field]:
            self.pattern_stats[field][pattern] = 0
        # Positive feedback increases, negative decreases (but not below zero)
        if correct:
            self.pattern_stats[field][pattern] += 1
        else:
            self.pattern_stats[field][pattern] = max(0, self.pattern_stats[field][pattern] - 1)
        self._save_patterns()

    def _save_patterns(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, "w") as f:
            json.dump(self.pattern_stats, f, indent=2)
