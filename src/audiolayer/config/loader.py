from pathlib import Path
from typing import Optional
import json
import yaml
from audiolayer.config.schema import MusicGenerationConfig, ConfigError


class ConfigLoader:
    @staticmethod
    def Load(config_path: str) -> MusicGenerationConfig:
        try:
            path = Path(config_path)
            
            if not path.exists():
                raise FileNotFoundError(f"Config file not found: {config_path}")
            
            if path.suffix.lower() in [".yaml", ".yml"]:
                with open(path, "r") as f:
                    data = yaml.safe_load(f)
            elif path.suffix.lower() == ".json":
                with open(path, "r") as f:
                    data = json.load(f)
            else:
                raise ConfigError(f"Unsupported config format: {path.suffix}")
            
            if data is None:
                data = {}
            
            return MusicGenerationConfig.FromDict(data)
        
        except FileNotFoundError as e:
            raise ConfigError(f"Config file not found: {config_path}") from e
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in config file: {e}") from e
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in config file: {e}") from e
        except Exception as e:
            raise ConfigError(f"Failed to load config: {e}") from e
    
    @staticmethod
    def LoadWithDefaults(config_path: Optional[str] = None) -> MusicGenerationConfig:
        if config_path is None:
            from audiolayer.config.defaults import GetDefaultConfig
            return GetDefaultConfig()
        
        try:
            return ConfigLoader.Load(config_path)
        except ConfigError:
            from audiolayer.config.defaults import GetDefaultConfig
            return GetDefaultConfig()
