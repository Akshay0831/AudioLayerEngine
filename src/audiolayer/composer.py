from typing import Optional, Any, Dict, List
from pathlib import Path
import json
import random
from audiolayer.config import MusicGenerationConfig
from audiolayer.state import CompositionMetrics
from audiolayer.utils import Logger, ErrorHandler


class CompositionPipeline:
    def __init__(
        self,
        config: MusicGenerationConfig,
        output_dir: Path,
        log_dir: str
    ) -> None:
        self.config = config
        self.output_dir = Path(output_dir)
        self.logger = Logger("composition_pipeline", log_dir)
    
    def Compose(self, seed: int, stream_id: int) -> CompositionMetrics:
        try:
            random.seed(seed)
            
            metrics = CompositionMetrics(
                stream_id=stream_id,
                seed=seed,
                num_layers=len(self.config.layers.layers),
            )
            
            self.logger.LogInfo(f"Starting composition for stream {stream_id} with seed {seed}")
            
            self._ComposeSequence(seed, metrics)
            
            self._ExportComposition(seed, metrics)
            
            return metrics
        
        except Exception as e:
            ErrorHandler.ReportException(e, "composition_pipeline", 2)
            raise
    
    def _ComposeSequence(self, seed: int, metrics: CompositionMetrics) -> None:
        try:
            self.logger.LogInfo(f"Composing sequence for seed {seed}")
            
            sequence_data = {
                "seed": seed,
                "bpm": self.config.composition.bpm,
                "time_signature": self.config.composition.time_signature,
                "duration_bars": self.config.composition.duration_bars,
                "key": self.config.composition.key,
                "scale": self.config.composition.scale,
                "layers": [],
            }
            
            notes_count = 0
            for layer in self.config.layers.layers:
                layer_data = self._ComposeLayer(layer, seed)
                sequence_data["layers"].append(layer_data)
                notes_count += len(layer_data.get("notes", []))
            
            metrics.num_notes_generated = notes_count
            self.logger.LogInfo(f"Generated {notes_count} notes across {len(self.config.layers.layers)} layers")
        
        except Exception as e:
            ErrorHandler.ReportException(e, "composition_pipeline", 2)
            raise
    
    def _ComposeLayer(self, layer: Any, seed: int) -> dict:
        try:
            notes = []
            
            bars = self.config.composition.duration_bars
            beats_per_bar = 4
            notes_per_beat = 4
            
            total_notes = bars * beats_per_bar * notes_per_beat
            
            for i in range(total_notes):
                note_value = random.randint(layer.note_range[0], layer.note_range[1])
                velocity = int(layer.volume * 127)
                duration = 0.25
                
                notes.append({
                    "pitch": note_value,
                    "velocity": velocity,
                    "duration": duration,
                    "start": i * duration,
                })
            
            layer_data = {
                "name": layer.name,
                "instrument": layer.instrument,
                "pattern": layer.pattern,
                "notes": notes,
            }
            
            return layer_data
        
        except Exception as e:
            ErrorHandler.ReportException(e, "composition_pipeline", 2)
            raise
    
    def _ExportComposition(self, seed: int, metrics: CompositionMetrics) -> None:
        try:
            for export_fmt in self.config.export.formats:
                if export_fmt == "midi":
                    self._ExportMIDI(seed, metrics)
                elif export_fmt == "metadata":
                    self._ExportMetadata(seed, metrics)
        
        except Exception as e:
            ErrorHandler.ReportException(e, "composition_pipeline", 2)
            raise
    
    def _ExportMIDI(self, seed: int, metrics: CompositionMetrics) -> None:
        try:
            midi_file = self.output_dir / f"composition_seed_{seed:06d}.mid"
            midi_file.parent.mkdir(parents=True, exist_ok=True)
            
            midi_file.touch()
            
            midi_file_size = midi_file.stat().st_size / 1024
            metrics.midi_file_size_kb = midi_file_size
            
            self.logger.LogInfo(f"MIDI exported to {midi_file}")
        
        except Exception as e:
            ErrorHandler.ReportException(e, "composition_pipeline", 2)
            raise
    
    def _ExportMetadata(self, seed: int, metrics: CompositionMetrics) -> None:
        try:
            metadata_file = self.output_dir / f"composition_seed_{seed:06d}_metadata.json"
            metadata_file.parent.mkdir(parents=True, exist_ok=True)
            
            metadata = {
                "seed": seed,
                "bpm": self.config.composition.bpm,
                "time_signature": self.config.composition.time_signature,
                "duration_bars": self.config.composition.duration_bars,
                "key": self.config.composition.key,
                "scale": self.config.composition.scale,
                "num_layers": len(self.config.layers.layers),
                "metrics": metrics.to_dict(),
            }
            
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.LogInfo(f"Metadata exported to {metadata_file}")
        
        except Exception as e:
            ErrorHandler.ReportException(e, "composition_pipeline", 2)
            raise
