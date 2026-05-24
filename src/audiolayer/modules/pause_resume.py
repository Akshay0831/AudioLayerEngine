from dataclasses import dataclass


@dataclass
class PauseResumeConfig:
    enabled: bool = True
    checkpoint_dir: str = "./checkpoints"


class PauseResume:
    def __init__(self, config: PauseResumeConfig) -> None:
        self.config = config
    
    def IsEnabled(self) -> bool:
        return self.config.enabled
    
    def GetCheckpointDir(self) -> str:
        return self.config.checkpoint_dir
