from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


class CompositionState(Enum):
    IDLE = "idle"
    COMPOSING = "composing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class CompositionMetrics:
    stream_id: int
    seed: int
    composition_time_sec: float = 0.0
    rendering_time_sec: float = 0.0
    midi_file_size_kb: float = 0.0
    peak_cpu_percent: float = 0.0
    peak_ram_gb: float = 0.0
    num_notes_generated: int = 0
    num_layers: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def total_time_sec(self) -> float:
        return self.composition_time_sec + self.rendering_time_sec
    
    def to_dict(self) -> dict:
        return {
            "stream_id": self.stream_id,
            "seed": self.seed,
            "composition_time_sec": self.composition_time_sec,
            "rendering_time_sec": self.rendering_time_sec,
            "total_time_sec": self.total_time_sec,
            "midi_file_size_kb": self.midi_file_size_kb,
            "peak_cpu_percent": self.peak_cpu_percent,
            "peak_ram_gb": self.peak_ram_gb,
            "num_notes_generated": self.num_notes_generated,
            "num_layers": self.num_layers,
            "timestamp": self.timestamp,
        }


@dataclass
class StreamState:
    stream_id: int
    seed: int
    state: CompositionState = CompositionState.IDLE
    current_stage: int = 0
    completed_layers: list[str] = field(default_factory=list)
    midi_generated: bool = False
    composition_complete: bool = False
    metrics: Optional[CompositionMetrics] = None
    error_message: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "stream_id": self.stream_id,
            "seed": self.seed,
            "state": self.state.value,
            "current_stage": self.current_stage,
            "completed_layers": self.completed_layers,
            "midi_generated": self.midi_generated,
            "composition_complete": self.composition_complete,
            "error_message": self.error_message,
            "timestamp": self.timestamp,
        }
