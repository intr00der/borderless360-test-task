from datetime import datetime
import os
from pathlib import Path

from modules.default_theme import DefaultConsoleTheme

# Paths
BASE_DIR = Path(os.getcwd()).absolute()
DEFAULT_INPUT_PATH_PATTERN = os.path.join(BASE_DIR, 'input', '*')
DEFAULT_OUTPUT_PATH = os.path.join(BASE_DIR, 'output', f"{datetime.now().strftime('%d.%m.%Y_%H-%M')}_export.html")
DEFAULT_TEMPLATES_DIR_PATH = os.path.join(BASE_DIR, 'templates')

# Console settings
DEFAULT_CONSOLE_WIDTH = 40
DEFAULT_CONSOLE_THEME = DefaultConsoleTheme
