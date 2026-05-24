from typing import Optional
from pathlib import Path
import time
from audiolayer.config import MusicGenerationConfig, ConfigValidator
from audiolayer.state import (
    CompositionState,
    CompositionMetrics,
    StreamState,
    CheckpointManager,
    ResourceMonitor,
)
from audiolayer.utils import Logger, ErrorHandler
from audiolayer.composer import CompositionPipeline


class CompositionOrchestrator:
    def __init__(
        self,
        config: MusicGenerationConfig,
        output_dir: str = "./output",
        num_streams: Optional[int] = None,
        log_dir: Optional[str] = None,
    ) -> None:
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        num_streams = num_streams or config.features.num_streams
        self.num_streams = min(num_streams, 16)
        
        self.log_dir = log_dir or str(self.output_dir / "logs")
        self.logger = Logger("composition_orchestrator", self.log_dir)
        
        self.checkpoint_dir = str(self.output_dir / "checkpoints")
        self.checkpoint_manager = CheckpointManager(self.checkpoint_dir)
        
        self.stream_states: dict[int, StreamState] = {}
        self.stream_metrics: dict[int, CompositionMetrics] = {}
        self.stream_monitors: dict[int, ResourceMonitor] = {}
        self.pipeline: Optional[CompositionPipeline] = None
    
    def ValidateConfig(self) -> tuple[bool, list[str]]:
        is_valid, errors = ConfigValidator.Validate(self.config)
        
        if not is_valid:
            self.logger.LogError(f"Config validation failed: {errors}")
        
        return (is_valid, errors)
    
    def ComposeBatch(self, seeds: list[int]) -> dict[int, CompositionMetrics]:
        try:
            is_valid, errors = self.ValidateConfig()
            if not is_valid:
                raise ValueError(f"Invalid configuration: {errors}")
            
            if not self.pipeline:
                self.pipeline = CompositionPipeline(self.config, self.output_dir, self.log_dir)
            
            self.logger.LogInfo(f"Starting composition batch with {len(seeds)} seeds across {self.num_streams} stream(s)")
            
            stream_id = 0
            for seed in seeds:
                if stream_id >= self.num_streams:
                    stream_id = 0
                
                stream_state = StreamState(stream_id=stream_id, seed=seed)
                self.stream_states[seed] = stream_state
                
                monitor = ResourceMonitor()
                monitor.Start()
                self.stream_monitors[seed] = monitor
                
                start_time = time.time()
                
                try:
                    self.logger.LogInfo(f"Composing stream {stream_id} with seed {seed}")
                    metrics = self.pipeline.Compose(seed, stream_id)
                    
                    elapsed = time.time() - start_time
                    metrics.composition_time_sec = elapsed
                    
                    monitor.Update()
                    metrics.peak_cpu_percent = monitor.GetPeakCPU()
                    metrics.peak_ram_gb = monitor.GetPeakRAM()
                    
                    stream_state.state = CompositionState.COMPLETED
                    stream_state.composition_complete = True
                    stream_state.metrics = metrics
                    
                    self.stream_metrics[seed] = metrics
                    self.checkpoint_manager.SaveCheckpoint(stream_state)
                    
                    self.logger.LogInfo(f"Stream {stream_id} (seed {seed}) completed in {elapsed:.2f}s")
                
                except Exception as e:
                    monitor.Stop()
                    stream_state.state = CompositionState.FAILED
                    stream_state.error_message = str(e)
                    ErrorHandler.ReportException(e, "composition_orchestrator", 2)
                    self.checkpoint_manager.SaveCheckpoint(stream_state)
                
                stream_id += 1
            
            return self.stream_metrics
        
        except Exception as e:
            ErrorHandler.ReportException(e, "composition_orchestrator", 3)
            raise
    
    def PauseStream(self, stream_id: int) -> bool:
        try:
            for seed, state in self.stream_states.items():
                if state.stream_id == stream_id and state.state == CompositionState.COMPOSING:
                    state.state = CompositionState.PAUSED
                    self.checkpoint_manager.SaveCheckpoint(state)
                    self.logger.LogInfo(f"Stream {stream_id} paused")
                    return True
            
            return False
        except Exception as e:
            ErrorHandler.ReportException(e, "composition_orchestrator", 2)
            return False
    
    def ResumeStream(self, stream_id: int) -> bool:
        try:
            checkpoint_files = self.checkpoint_manager.ListCheckpoints()
            
            for checkpoint_file in checkpoint_files:
                state = self.checkpoint_manager.LoadCheckpoint(checkpoint_file)
                if state and state.stream_id == stream_id and state.state == CompositionState.PAUSED:
                    state.state = CompositionState.COMPOSING
                    self.checkpoint_manager.SaveCheckpoint(state)
                    self.logger.LogInfo(f"Stream {stream_id} resumed")
                    return True
            
            return False
        except Exception as e:
            ErrorHandler.ReportException(e, "composition_orchestrator", 2)
            return False
    
    def PauseAll(self) -> int:
        paused_count = 0
        
        try:
            for state in self.stream_states.values():
                if state.state == CompositionState.COMPOSING:
                    state.state = CompositionState.PAUSED
                    self.checkpoint_manager.SaveCheckpoint(state)
                    paused_count += 1
            
            self.logger.LogInfo(f"Paused {paused_count} stream(s)")
            return paused_count
        
        except Exception as e:
            ErrorHandler.ReportException(e, "composition_orchestrator", 2)
            return 0
    
    def ResumeAll(self) -> int:
        resumed_count = 0
        
        try:
            checkpoint_files = self.checkpoint_manager.ListCheckpoints()
            
            for checkpoint_file in checkpoint_files:
                state = self.checkpoint_manager.LoadCheckpoint(checkpoint_file)
                if state and state.state == CompositionState.PAUSED:
                    state.state = CompositionState.COMPOSING
                    self.checkpoint_manager.SaveCheckpoint(state)
                    resumed_count += 1
            
            self.logger.LogInfo(f"Resumed {resumed_count} stream(s)")
            return resumed_count
        
        except Exception as e:
            ErrorHandler.ReportException(e, "composition_orchestrator", 2)
            return 0
    
    def SubmitFeedback(self, seed: int, feedback_type: str, score: float, comment: str = "") -> bool:
        try:
            if seed not in self.stream_states:
                self.logger.LogWarning(f"Feedback for unknown seed {seed}")
                return False
            
            state = self.stream_states[seed]
            self.logger.LogInfo(f"Feedback for seed {seed}: {feedback_type}={score} ({comment})")
            
            feedback_file = Path(self.output_dir) / "feedback" / f"seed_{seed}_feedback.json"
            feedback_file.parent.mkdir(parents=True, exist_ok=True)
            
            import json
            feedback_data = {
                "seed": seed,
                "type": feedback_type,
                "score": score,
                "comment": comment,
                "timestamp": state.timestamp,
            }
            
            with open(feedback_file, "w") as f:
                json.dump(feedback_data, f, indent=2)
            
            return True
        
        except Exception as e:
            ErrorHandler.ReportException(e, "composition_orchestrator", 2)
            return False
    
    def GetStreamStatus(self, seed: int) -> Optional[dict]:
        try:
            if seed not in self.stream_states:
                return None
            
            state = self.stream_states[seed]
            return {
                "seed": seed,
                "stream_id": state.stream_id,
                "state": state.state.value,
                "layers_completed": len(state.completed_layers),
                "midi_generated": state.midi_generated,
                "complete": state.composition_complete,
                "error": state.error_message,
            }
        
        except Exception as e:
            ErrorHandler.ReportException(e, "composition_orchestrator", 2)
            return None
    
    def Finalize(self) -> None:
        try:
            for monitor in self.stream_monitors.values():
                monitor.Stop()
            
            self.logger.LogInfo("Composition orchestrator finalized")
        
        except Exception as e:
            ErrorHandler.ReportException(e, "composition_orchestrator", 2)
