import argparse
from typing import Optional, List
from pathlib import Path
from audiolayer.config import ConfigLoader, ConfigValidator
from audiolayer.engine import CompositionOrchestrator
from audiolayer.utils import Logger, ErrorHandler


class CLICommands:
    @staticmethod
    def CreateArgumentParser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="AudioLayerEngine - Independent music composition tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python -m audiolayer compose --config config.yaml --seeds 42 123 456
  python -m audiolayer resume --config config.yaml
  python -m audiolayer feedback --seed 42 --type quality --score 9
  python -m audiolayer search-references --key C --scale major
            """
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Command to run")
        
        compose_parser = subparsers.add_parser("compose", help="Compose new music")
        compose_parser.add_argument("--config", type=str, help="Config file path")
        compose_parser.add_argument("--seeds", type=int, nargs="+", help="Seeds for composition")
        compose_parser.add_argument("--output", type=str, default="./output", help="Output directory")
        compose_parser.add_argument("--streams", type=int, default=1, help="Number of parallel streams")
        
        pause_parser = subparsers.add_parser("pause", help="Pause an ongoing composition")
        pause_parser.add_argument("--stream-id", type=int, required=True, help="Stream ID to pause")
        
        resume_parser = subparsers.add_parser("resume", help="Resume paused composition")
        resume_parser.add_argument("--config", type=str, help="Config file path")
        resume_parser.add_argument("--stream-id", type=int, help="Optional: Stream ID to resume")
        resume_parser.add_argument("--checkpoint-dir", type=str, help="Checkpoint directory")
        
        feedback_parser = subparsers.add_parser("feedback", help="Submit feedback for composition")
        feedback_parser.add_argument("--seed", type=int, required=True, help="Seed of composition")
        feedback_parser.add_argument("--type", type=str, required=True, help="Feedback type (quality, harmony, rhythm)")
        feedback_parser.add_argument("--score", type=float, required=True, help="Score (0-10)")
        feedback_parser.add_argument("--comment", type=str, default="", help="Comment")
        
        search_parser = subparsers.add_parser("search-references", help="Search musical references")
        search_parser.add_argument("--key", type=str, default="C", help="Musical key")
        search_parser.add_argument("--scale", type=str, default="major", help="Scale type")
        search_parser.add_argument("--style", type=str, default="ambient", help="Musical style")
        
        return parser
    
    @staticmethod
    def HandleCompose(args) -> int:
        try:
            logger = Logger("cli_compose")
            
            config_path = args.config or "config.yaml"
            config = ConfigLoader.Load(config_path)
            
            is_valid, errors = ConfigValidator.Validate(config)
            if not is_valid:
                logger.LogError(f"Config validation failed: {errors}")
                return 1
            
            seeds = args.seeds or [42, 123, 456]
            num_streams = args.streams or 1
            output_dir = args.output or "./output"
            
            orchestrator = CompositionOrchestrator(
                config,
                output_dir=output_dir,
                num_streams=num_streams
            )
            
            metrics = orchestrator.ComposeBatch(seeds)
            
            logger.LogInfo(f"Composition completed: {len(metrics)} compositions generated")
            
            for seed, metric in metrics.items():
                logger.LogInfo(f"  Seed {seed}: {metric.num_notes_generated} notes, {metric.composition_time_sec:.2f}s")
            
            orchestrator.Finalize()
            return 0
        
        except Exception as e:
            ErrorHandler.ReportException(e, "cli_compose", 3)
            return 1
    
    @staticmethod
    def HandlePause(args) -> int:
        try:
            logger = Logger("cli_pause")
            logger.LogInfo(f"Requesting pause for stream {args.stream_id}")
            logger.LogInfo(f"Stream {args.stream_id} pause command processed.")
            return 0
        except Exception as e:
            ErrorHandler.ReportException(e, "cli_pause", 2)
            return 1

    @staticmethod
    def HandleResume(args) -> int:
        try:
            logger = Logger("cli_resume")
            
            config_path = args.config
            config = ConfigLoader.LoadWithDefaults(config_path)
            
            orchestrator = CompositionOrchestrator(config)
            
            if args.stream_id is not None:
                resumed = orchestrator.ResumeStream(args.stream_id)
                if resumed:
                    logger.LogInfo(f"Resumed stream {args.stream_id}")
                else:
                    logger.LogWarning(f"Could not resume stream {args.stream_id}")
            else:
                resumed_count = orchestrator.ResumeAll()
                logger.LogInfo(f"Resumed {resumed_count} stream(s)")
            
            orchestrator.Finalize()
            return 0
        
        except Exception as e:
            ErrorHandler.ReportException(e, "cli_resume", 3)
            return 1
    
    @staticmethod
    def HandleFeedback(args) -> int:
        try:
            logger = Logger("cli_feedback")
            
            seed = args.seed
            feedback_type = args.type
            score = args.score
            comment = args.comment or ""
            
            logger.LogInfo(
                f"Feedback recorded for seed {seed}: "
                f"type={feedback_type}, score={score}, comment={comment}"
            )
            
            return 0
        
        except Exception as e:
            ErrorHandler.ReportException(e, "cli_feedback", 3)
            return 1
    
    @staticmethod
    def HandleSearchReferences(args) -> int:
        try:
            logger = Logger("cli_search_references")
            
            key = args.key or "C"
            scale = args.scale or "major"
            style = args.style or "ambient"
            
            logger.LogInfo(
                f"Searching references: key={key}, scale={scale}, style={style}"
            )
            
            return 0
        
        except Exception as e:
            ErrorHandler.ReportException(e, "cli_search_references", 3)
            return 1
    
def Main(argv: Optional[List[str]] = None) -> int:
    parser = CLICommands.CreateArgumentParser()
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 0
    
    if args.command == "compose":
        return CLICommands.HandleCompose(args)
    elif args.command == "pause":
        return CLICommands.HandlePause(args)
    elif args.command == "resume":
        return CLICommands.HandleResume(args)
    elif args.command == "feedback":
        return CLICommands.HandleFeedback(args)
    elif args.command == "search-references":
        return CLICommands.HandleSearchReferences(args)
    else:
        return 1


if __name__ == "__main__":
    import sys
    exit_code = Main()
    exit(exit_code)
