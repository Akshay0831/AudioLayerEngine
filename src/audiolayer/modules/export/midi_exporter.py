from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from audiolayer.modules.sequencer import MIDISequencer


class BaseExporter(ABC):
    def __init__(self, output_dir: str = "./output") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def Export(self, data: any, filename: str) -> bool:
        pass
    
    def _GetFullPath(self, filename: str) -> Path:
        return self.output_dir / filename


class MIDIExporter(BaseExporter):
    def Export(self, sequencer: MIDISequencer, filename: str) -> bool:
        try:
            midi_data = sequencer.GenerateMIDI()
            
            file_path = self._GetFullPath(filename)
            
            with open(file_path, "wb") as f:
                f.write(midi_data)
            
            return True
        except Exception as e:
            raise IOError(f"Failed to export MIDI: {e}") from e
    
    def ExportToBytes(self, sequencer: MIDISequencer) -> bytes:
        return sequencer.GenerateMIDI()


class ExportError(Exception):
    pass
