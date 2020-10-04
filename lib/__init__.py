from logging.config import dictConfig as loggingConfig
from pathlib import Path

from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

loggingConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        }
    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO',
        },
        'save_file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'filename': 'logs/parser.log',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'D',
            'interval': 7,
            'backupCount': 3,
            'utc': True,
        },
    },
    'loggers': {
        'parser': {
            'handlers': ['default', "save_file"],
            'level': 'INFO',
            'propagate': True,
        },
    },
})