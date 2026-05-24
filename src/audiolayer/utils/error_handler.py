import traceback
from audiolayer.utils.logging import Logger


class ErrorHandler:
    @staticmethod
    def ReportException(exception: Exception, source: str, severity: int = 2) -> None:
        logger = Logger(source)
        
        if severity == 1:
            logger.LogWarning(f"{type(exception).__name__}: {str(exception)}")
        elif severity == 2:
            logger.LogError(f"{type(exception).__name__}: {str(exception)}")
        elif severity == 3:
            logger.LogError(f"FATAL - {type(exception).__name__}: {str(exception)}")
        
        logger.LogDebug(traceback.format_exc())
    
    @staticmethod
    def LogError(message: str, source: str = "error_handler") -> None:
        logger = Logger(source)
        logger.LogError(message)
    
    @staticmethod
    def LogWarning(message: str, source: str = "error_handler") -> None:
        logger = Logger(source)
        logger.LogWarning(message)
