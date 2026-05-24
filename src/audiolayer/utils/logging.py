import logging
from pathlib import Path
from typing import Optional


class Logger:
    def __init__(self, component: str, log_dir: Optional[str] = None) -> None:
        self.component = component
        
        if log_dir:
            log_path = Path(log_dir)
            log_path.mkdir(parents=True, exist_ok=True)
            log_file = log_path / f"{component}.log"
        else:
            log_file = None
        
        self.logger = logging.getLogger(component)
        self.logger.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            f"[%(asctime)s] [{component}] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def LogInfo(self, message: str) -> None:
        self.logger.info(message)
    
    def LogDebug(self, message: str) -> None:
        self.logger.debug(message)
    
    def LogWarning(self, message: str) -> None:
        self.logger.warning(message)
    
    def LogError(self, message: str) -> None:
        self.logger.error(message)
    
    def LogMetric(self, metric_name: str, value: float) -> None:
        self.logger.info(f"METRIC: {metric_name}={value}")
