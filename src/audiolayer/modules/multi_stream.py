from dataclasses import dataclass


@dataclass
class MultiStreamConfig:
    enabled: bool = True
    num_streams: int = 1
    max_concurrent: int = 4


class MultiStream:
    def __init__(self, config: MultiStreamConfig) -> None:
        self.config = config
    
    def GetStreamCount(self) -> int:
        if not self.config.enabled:
            return 1
        return min(self.config.num_streams, self.config.max_concurrent)
    
    def IsEnabled(self) -> bool:
        return self.config.enabled and self.config.num_streams > 1
    
    def GetMaxConcurrent(self) -> int:
        return self.config.max_concurrent
