from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class InstrumentType(Enum):
    PIANO = "piano"
    SYNTH = "synth"
    STRINGS = "strings"
    DRUMS = "drums"
    BASS = "bass"


class PatternType(Enum):
    STEADY = "steady"
    RANDOM = "random"
    WAVE = "wave"
    ARPEGGIO = "arpeggio"


class ExportFormat(Enum):
    MIDI = "midi"
    METADATA = "metadata"
    AUDIO = "audio"


@dataclass
class LayerDefinition:
    name: str
    instrument: str
    pattern: str
    volume: float = 0.8
    octave: int = 4
    note_range: tuple[int, int] = (36, 84)


@dataclass
class CompositionConfig:
    bpm: int = 120
    time_signature: str = "4/4"
    duration_bars: int = 32
    key: str = "C"
    scale: str = "major"
    style: str = "ambient"
    mood: str = "mysterious"


@dataclass
class LayerConfig:
    layers: list[LayerDefinition] = field(default_factory=list)


@dataclass
class InstrumentConfig:
    builtin_dir: str = "./instruments/builtin"
    custom_dir: Optional[str] = None


@dataclass
class ExportConfig:
    formats: list[str] = field(default_factory=lambda: ["midi"])
    output_dir: str = "./output"


@dataclass
class CompositionFeatures:
    enable_multi_stream: bool = True
    num_streams: int = 1
    enable_pause_resume: bool = True
    enable_feedback: bool = True
    enable_reference_search: bool = False


@dataclass
class ReferenceConfig:
    enable_search: bool = False
    index_path: str = "./references"


@dataclass
class MusicGenerationConfig:
    composition: CompositionConfig = field(default_factory=CompositionConfig)
    layers: LayerConfig = field(default_factory=LayerConfig)
    instruments: InstrumentConfig = field(default_factory=InstrumentConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    features: CompositionFeatures = field(default_factory=CompositionFeatures)
    references: ReferenceConfig = field(default_factory=ReferenceConfig)
    
    @staticmethod
    def FromDict(data: dict) -> "MusicGenerationConfig":
        composition = CompositionConfig(**data.get("composition", {}))
        
        layers_data = data.get("layers", {})
        layer_defs = [LayerDefinition(**layer) for layer in layers_data.get("layers", [])]
        layers = LayerConfig(layers=layer_defs)
        
        instruments = InstrumentConfig(**data.get("instruments", {}))
        export = ExportConfig(**data.get("export", {}))
        features = CompositionFeatures(**data.get("features", {}))
        references = ReferenceConfig(**data.get("references", {}))
        
        return MusicGenerationConfig(
            composition=composition,
            layers=layers,
            instruments=instruments,
            export=export,
            features=features,
            references=references
        )


class ConfigError(Exception):
    pass
