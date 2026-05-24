from dataclasses import dataclass, field
from typing import Optional
from audiolayer.config import LayerDefinition
from audiolayer.utils import MusicTheory


@dataclass
class LayerState:
    layer_def: LayerDefinition
    notes_generated: int = 0
    is_playing: bool = False
    current_position: float = 0.0
    generated_notes: list = field(default_factory=list)


class LayerManager:
    def __init__(self, layers: list[LayerDefinition]) -> None:
        self.layers: dict[str, LayerState] = {}
        
        for layer_def in layers:
            self.layers[layer_def.name] = LayerState(layer_def=layer_def)
    
    def GetLayer(self, name: str) -> Optional[LayerState]:
        return self.layers.get(name)
    
    def GetAllLayers(self) -> list[LayerState]:
        return list(self.layers.values())
    
    def GetActiveLayerCount(self) -> int:
        return sum(1 for layer in self.layers.values() if layer.is_playing)
    
    def StartLayer(self, name: str) -> bool:
        if name not in self.layers:
            return False
        
        self.layers[name].is_playing = True
        self.layers[name].current_position = 0.0
        return True
    
    def StopLayer(self, name: str) -> bool:
        if name not in self.layers:
            return False
        
        self.layers[name].is_playing = False
        return True
    
    def StartAllLayers(self) -> int:
        count = 0
        for name in self.layers:
            if self.StartLayer(name):
                count += 1
        return count
    
    def StopAllLayers(self) -> int:
        count = 0
        for name in self.layers:
            if self.StopLayer(name):
                count += 1
        return count
    
    def UpdateLayerPosition(self, name: str, delta_time: float) -> bool:
        if name not in self.layers:
            return False
        
        layer = self.layers[name]
        if layer.is_playing:
            layer.current_position += delta_time
        
        return True
    
    def GenerateNotesForLayer(
        self
        name: str
        num_notes: int
        root_note: str
        scale: str
        octave: int
    ) -> list[int]:
        if name not in self.layers:
            return []
        
        layer = self.layers[name]
        scale_notes = MusicTheory.GetScaleNotes(root_note, scale, octave, num_notes)
        layer.generated_notes = scale_notes
        layer.notes_generated = num_notes
        
        return scale_notes
    
    def GetLayerNotes(self, name: str) -> list[int]:
        if name not in self.layers:
            return []
        
        return self.layers[name].generated_notes
    
    def GetTotalNotesGenerated(self) -> int:
        return sum(layer.notes_generated for layer in self.layers.values())
    
    def ResetLayer(self, name: str) -> bool:
        if name not in self.layers:
            return False
        
        layer = self.layers[name]
        layer.notes_generated = 0
        layer.is_playing = False
        layer.current_position = 0.0
        layer.generated_notes = []
        
        return True
    
    def ResetAllLayers(self) -> int:
        count = 0
        for name in self.layers:
            if self.ResetLayer(name):
                count += 1
        return count
    
    def ExportToDict(self) -> dict:
        return {
            "layers": {
                name: {
                    "name": layer.layer_def.name
                    "instrument": layer.layer_def.instrument
                    "notes_generated": layer.notes_generated
                    "is_playing": layer.is_playing
                    "current_position": layer.current_position
                }
                for name, layer in self.layers.items()
            }
            "total_notes": self.GetTotalNotesGenerated()
        }
