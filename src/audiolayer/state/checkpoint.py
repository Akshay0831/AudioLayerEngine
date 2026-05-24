from pathlib import Path
import json
from typing import Optional
from audiolayer.state.state_machine import StreamState, CompositionState


class CheckpointError(Exception):
    pass


class CheckpointManager:
    def __init__(self, checkpoint_dir: str) -> None:
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def SaveCheckpoint(self, stream_state: StreamState) -> None:
        try:
            checkpoint_file = self.checkpoint_dir / f"stream_{stream_state.stream_id:02d}_seed_{stream_state.seed:06d}.json"
            
            checkpoint_data = {
                "stream_id": stream_state.stream_id,
                "seed": stream_state.seed,
                "state": stream_state.state.value,
                "current_stage": stream_state.current_stage,
                "completed_layers": stream_state.completed_layers,
                "midi_generated": stream_state.midi_generated,
                "composition_complete": stream_state.composition_complete,
                "timestamp": stream_state.timestamp,
            }
            
            with open(checkpoint_file, "w") as f:
                json.dump(checkpoint_data, f, indent=2)
        
        except Exception as e:
            raise CheckpointError(f"Failed to save checkpoint: {e}") from e
    
    def LoadCheckpoint(self, checkpoint_file: str) -> Optional[StreamState]:
        try:
            path = Path(checkpoint_file)
            
            if not path.exists():
                return None
            
            with open(path, "r") as f:
                data = json.load(f)
            
            stream_state = StreamState(
                stream_id=data.get("stream_id", 0),
                seed=data.get("seed", 0),
                state=CompositionState(data.get("state", "idle")),
                current_stage=data.get("current_stage", 0),
                completed_layers=data.get("completed_layers", []),
                midi_generated=data.get("midi_generated", False),
                composition_complete=data.get("composition_complete", False),
                timestamp=data.get("timestamp", ""),
            )
            
            return stream_state
        
        except Exception as e:
            raise CheckpointError(f"Failed to load checkpoint: {e}") from e
    
    def DeleteCheckpoint(self, stream_id: int) -> None:
        try:
            checkpoint_file = self.checkpoint_dir / f"stream_{stream_id:02d}_*.json"
            
            for file in self.checkpoint_dir.glob(f"stream_{stream_id:02d}_*.json"):
                file.unlink()
        
        except Exception as e:
            raise CheckpointError(f"Failed to delete checkpoint: {e}") from e
    
    def ListCheckpoints(self) -> list[str]:
        try:
            checkpoints = sorted(self.checkpoint_dir.glob("stream_*.json"))
            return [str(cp) for cp in checkpoints]
        except Exception as e:
            raise CheckpointError(f"Failed to list checkpoints: {e}") from e
