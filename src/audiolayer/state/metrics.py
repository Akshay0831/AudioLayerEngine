from dataclasses import dataclass, field
import psutil
import time
from typing import Optional


@dataclass
class ResourceSnapshot:
    cpu_usage: float
    ram_usage_gb: float
    timestamp: float = field(default_factory=time.time)


class ResourceMonitor:
    def __init__(self) -> None:
        self.start_time = None
        self.peak_cpu = 0.0
        self.peak_ram = 0.0
        self.is_running = False
    
    def Start(self) -> None:
        self.start_time = time.time()
        self.is_running = True
        self.peak_cpu = psutil.cpu_percent(interval=0.1)
        self.peak_ram = self._GetCurrentRAM()
    
    def Update(self) -> None:
        if not self.is_running:
            return
        
        try:
            current_cpu = psutil.cpu_percent(interval=0.1)
            self.peak_cpu = max(self.peak_cpu, current_cpu)
            
            current_ram = self._GetCurrentRAM()
            self.peak_ram = max(self.peak_ram, current_ram)
        except Exception:
            pass
    
    def Stop(self) -> None:
        self.is_running = False
    
    def GetElapsedTime(self) -> float:
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
    
    def GetPeakCPU(self) -> float:
        return self.peak_cpu
    
    def GetPeakRAM(self) -> float:
        return self.peak_ram
    
    @staticmethod
    def _GetCurrentRAM() -> float:
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024 ** 3)
        except Exception:
            return 0.0
    
    @staticmethod
    def GetSystemRAM() -> float:
        try:
            return psutil.virtual_memory().total / (1024 ** 3)
        except Exception:
            return 0.0
    
    @staticmethod
    def GetAvailableSystemRAM() -> float:
        try:
            return psutil.virtual_memory().available / (1024 ** 3)
        except Exception:
            return 0.0
