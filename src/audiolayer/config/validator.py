from audiolayer.config.schema import MusicGenerationConfig


class ConfigValidator:
    @staticmethod
    def Validate(config: MusicGenerationConfig) -> tuple[bool, list[str]]:
        errors = []
        
        errors.extend(ConfigValidator._ValidateComposition(config.composition))
        errors.extend(ConfigValidator._ValidateLayers(config.layers))
        errors.extend(ConfigValidator._ValidateExport(config.export))
        errors.extend(ConfigValidator._ValidateFeatures(config.features))
        
        return (len(errors) == 0, errors)
    
    @staticmethod
    def _ValidateComposition(composition) -> list[str]:
        errors = []
        
        if composition.bpm < 40 or composition.bpm > 300:
            errors.append(f"BPM must be between 40 and 300, got {composition.bpm}")
        
        valid_time_sigs = ["2/4", "3/4", "4/4", "6/8"]
        if composition.time_signature not in valid_time_sigs:
            errors.append(f"Invalid time signature: {composition.time_signature}")
        
        if composition.duration_bars < 1 or composition.duration_bars > 1024:
            errors.append(f"Duration must be 1-1024 bars, got {composition.duration_bars}")
        
        if not composition.key or len(composition.key) == 0:
            errors.append("Key cannot be empty")
        
        if not composition.scale or len(composition.scale) == 0:
            errors.append("Scale cannot be empty")
        
        return errors
    
    @staticmethod
    def _ValidateLayers(layers) -> list[str]:
        errors = []
        
        if not layers.layers:
            errors.append("At least one layer is required")
            return errors
        
        if len(layers.layers) > 32:
            errors.append(f"Maximum 32 layers allowed, got {len(layers.layers)}")
        
        layer_names = set()
        for layer in layers.layers:
            if not layer.name or len(layer.name) == 0:
                errors.append("Layer name cannot be empty")
            
            if layer.name in layer_names:
                errors.append(f"Duplicate layer name: {layer.name}")
            layer_names.add(layer.name)
            
            if layer.volume < 0.0 or layer.volume > 1.0:
                errors.append(f"Layer {layer.name} volume must be 0.0-1.0, got {layer.volume}")
            
            if layer.octave < 0 or layer.octave > 8:
                errors.append(f"Layer {layer.name} octave must be 0-8, got {layer.octave}")
            
            if not layer.instrument or len(layer.instrument) == 0:
                errors.append(f"Layer {layer.name} instrument cannot be empty")
        
        return errors
    
    @staticmethod
    def _ValidateExport(export) -> list[str]:
        errors = []
        
        valid_formats = ["midi", "metadata", "audio"]
        for fmt in export.formats:
            if fmt not in valid_formats:
                errors.append(f"Invalid export format: {fmt}")
        
        if not export.output_dir or len(export.output_dir) == 0:
            errors.append("Output directory cannot be empty")
        
        return errors
    
    @staticmethod
    def _ValidateFeatures(features) -> list[str]:
        errors = []
        
        if features.num_streams < 1 or features.num_streams > 16:
            errors.append(f"num_streams must be 1-16, got {features.num_streams}")
        
        return errors
