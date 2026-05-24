from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
import json
from pathlib import Path


class FeedbackType(Enum):
    QUALITY = "quality"
    MELODY = "melody"
    HARMONY = "harmony"
    RHYTHM = "rhythm"
    INSTRUMENTATION = "instrumentation"


@dataclass
class FeedbackScore:
    feedback_type: FeedbackType
    score: float
    comment: str = ""
    timestamp: str = ""
    
    def to_dict(self) -> dict:
        return {
            "type": self.feedback_type.value,
            "score": self.score,
            "comment": self.comment,
            "timestamp": self.timestamp,
        }


@dataclass
class FeedbackConfig:
    enabled: bool = True
    min_score: float = 0.0
    max_score: float = 10.0
    feedback_dir: str = "./feedback"
    apply_threshold: float = 6.0


class FeedbackIntegration:
    def __init__(self, config: FeedbackConfig) -> None:
        self.config = config
        self.feedback_dir = Path(config.feedback_dir)
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_scores: dict[int, list[FeedbackScore]] = {}
    
    def RecordScore(self, seed: int, feedback: FeedbackScore) -> bool:
        try:
            if seed not in self.feedback_scores:
                self.feedback_scores[seed] = []
            
            self.feedback_scores[seed].append(feedback)
            
            feedback_file = self.feedback_dir / f"seed_{seed:06d}_feedback.json"
            
            feedback_data = [f.to_dict() for f in self.feedback_scores[seed]]
            
            with open(feedback_file, "w") as f:
                json.dump(feedback_data, f, indent=2)
            
            return True
        except Exception:
            return False
    
    def GetAverageScore(self, seed: int) -> Optional[float]:
        if seed not in self.feedback_scores or not self.feedback_scores[seed]:
            return None
        
        scores = [f.score for f in self.feedback_scores[seed]]
        return sum(scores) / len(scores)
    
    def GetScoresByType(self, seed: int, feedback_type: FeedbackType) -> list[float]:
        if seed not in self.feedback_scores:
            return []
        
        return [
            f.score for f in self.feedback_scores[seed]
            if f.feedback_type == feedback_type
        ]
    
    def ApplyQualityThreshold(self, seed: int) -> bool:
        avg_score = self.GetAverageScore(seed)
        if avg_score is None:
            return True
        
        return avg_score >= self.config.apply_threshold
    
    def LoadFeedback(self, seed: int) -> list[FeedbackScore]:
        try:
            feedback_file = self.feedback_dir / f"seed_{seed:06d}_feedback.json"
            
            if not feedback_file.exists():
                return []
            
            with open(feedback_file, "r") as f:
                data = json.load(f)
            
            feedback_list = [
                FeedbackScore(
                    feedback_type=FeedbackType(item["type"]),
                    score=item["score"],
                    comment=item.get("comment", ""),
                    timestamp=item.get("timestamp", ""),
                )
                for item in data
            ]
            
            self.feedback_scores[seed] = feedback_list
            return feedback_list
        
        except Exception:
            return []
