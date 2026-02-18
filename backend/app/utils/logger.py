"""Structured logging utilities with correlation ID support."""
import logging
import sys
from contextvars import ContextVar
from typing import Optional
from datetime import datetime
import json

# Context variable to store correlation ID for current request
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON with correlation ID and context."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'correlation_id': correlation_id_var.get(),
        }

        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'analysis_id'):
            log_data['analysis_id'] = record.analysis_id
        if hasattr(record, 'document_id'):
            log_data['document_id'] = record.document_id
        if hasattr(record, 'status_code'):
            log_data['status_code'] = record.status_code
        if hasattr(record, 'method'):
            log_data['method'] = record.method
        if hasattr(record, 'path'):
            log_data['path'] = record.path
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class SimpleFormatter(logging.Formatter):
    """Simple colored formatter for development."""

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors and correlation ID."""
        color = self.COLORS.get(record.levelname, '')
        reset = self.RESET

        # Build the log message
        timestamp = datetime.utcnow().strftime('%H:%M:%S')
        corr_id = correlation_id_var.get() or 'N/A'

        # Base message
        msg = f"{color}[{timestamp}] {record.levelname:8s}{reset} [{corr_id[:8]}] {record.getMessage()}"

        # Add context if present
        context_parts = []
        if hasattr(record, 'user_id'):
            context_parts.append(f"user={record.user_id[:8]}")
        if hasattr(record, 'analysis_id'):
            context_parts.append(f"analysis={record.analysis_id[:8]}")
        if hasattr(record, 'document_id'):
            context_parts.append(f"doc={record.document_id[:8]}")
        if hasattr(record, 'method'):
            context_parts.append(f"{record.method} {getattr(record, 'path', '')}")
        if hasattr(record, 'status_code'):
            context_parts.append(f"status={record.status_code}")
        if hasattr(record, 'duration_ms'):
            context_parts.append(f"{record.duration_ms}ms")

        if context_parts:
            msg += f" {{{', '.join(context_parts)}}}"

        return msg


def setup_logging(json_logs: bool = False) -> None:
    """Configure application-wide logging."""
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove existing handlers
    root_logger.handlers = []

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    # Use appropriate formatter
    if json_logs:
        formatter = StructuredFormatter()
    else:
        formatter = SimpleFormatter()

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Set specific logger levels
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.error').setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for current context."""
    correlation_id_var.set(correlation_id)


def get_correlation_id() -> Optional[str]:
    """Get correlation ID from current context."""
    return correlation_id_var.get()


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    **context
) -> None:
    """Log with additional context fields."""
    extra = {k: v for k, v in context.items() if v is not None}
    logger.log(level, message, extra=extra)
