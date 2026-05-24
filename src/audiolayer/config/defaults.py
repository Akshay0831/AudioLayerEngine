from audiolayer.config.schema import (
    MusicGenerationConfig,
    CompositionConfig,
    LayerConfig,
    LayerDefinition,
    InstrumentConfig,
    ExportConfig,
    CompositionFeatures,
    ReferenceConfig,
)


def GetDefaultConfig() -> MusicGenerationConfig:
    composition = CompositionConfig(
        bpm=120,
        time_signature="4/4",
        duration_bars=32,
        key="C",
        scale="major"
    )
    
    default_layers = [
        LayerDefinition(
            name="bass",
            instrument="synth_bass",
            pattern="steady",
            volume=0.8,
            octave=2,
            note_range=(36, 48)
        ),
        LayerDefinition(
            name="pad",
            instrument="synth_pad",
            pattern="steady",
            volume=0.6,
            octave=4,
            note_range=(48, 72)
        ),
        LayerDefinition(
            name="melody",
            instrument="synth_lead",
            pattern="random",
            volume=0.7,
            octave=5,
            note_range=(60, 84)
        ),
        LayerDefinition(
            name="percussion",
            instrument="drums",
            pattern="steady",
            volume=0.9,
            octave=0,
            note_range=(36, 51)
        ),
    ]
    
    layers = LayerConfig(layers=default_layers)
    
    instruments = InstrumentConfig(
        builtin_dir="./instruments/builtin",
        custom_dir=None
    )
    
    export = ExportConfig(
        formats=["midi", "metadata"],
        output_dir="./output"
    )
    
    features = CompositionFeatures(
        enable_multi_stream=True,
        num_streams=1,
        enable_pause_resume=True,
        enable_feedback=True,
        enable_reference_search=False
    )
    
    references = ReferenceConfig(
        enable_search=False,
        index_path="./references"
    )
    
    return MusicGenerationConfig(
        composition=composition,
        layers=layers,
        instruments=instruments,
        export=export,
        features=features,
        references=references
    )
