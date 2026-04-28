import logging
import os
from datetime import datetime

class HumanReadableFormatter(logging.Formatter):
    """
    Custom formatter for terminal output:
    - INFO: No preamble, just the message.
    - WARNING and above: [LEVEL] Name: Message.
    """
    def __init__(self):
        super().__init__()
        self.info_formatter = logging.Formatter('%(message)s')
        self.error_formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')

    def format(self, record):
        if record.levelno <= logging.INFO:
            return self.info_formatter.format(record)
        return self.error_formatter.format(record)


def setup_logging(work_dir):
    """
    Sets up dual logging: 
    - DEBUG and above to a timestamped file in work_dir/logs/
    - INFO and above to the terminal
    Returns the path to the log file.
    """
    log_dir = os.path.join(work_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"run_{timestamp}.log")
    abs_log_path = os.path.abspath(log_file)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Standard formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

    # File handler (DEBUG+)
    file_handler = logging.FileHandler(abs_log_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Console handler (INFO+)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(HumanReadableFormatter())
    root_logger.addHandler(console_handler)

    return abs_log_path
