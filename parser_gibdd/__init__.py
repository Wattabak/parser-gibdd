from dataclasses import dataclass
from logging.config import dictConfig
from pathlib import Path
from typing import List

from dotenv import load_dotenv

env_path = Path('') / '.env'
load_dotenv(dotenv_path=env_path)

dictConfig({
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
    },
    'loggers': {
        'root': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True,
        },
    },
})

APP_SETTINGS = {
    'GIBDD_HOST_URL': 'http://stat.gibdd.ru',
    'ROTATING_PROXIES': 1,
    'SESSION_MAX_RETRIES': 3,
    'PROXY_SETTINGS': {
        'USE_PROXY': 1,
        'PROXY_LIST': [
            'socks5://195.2.71.201:16072',
            'socks5://91.219.58.95:1080',
            'socks5://185.117.244.136:9050',
            'socks5://194.67.108.218:9050',
            'socks5://188.130.138.12:1080',
            'socks5://176.102.70.102:1080',
            'socks5://85.172.31.16:33427',
            'socks5://93.179.94.133:5678',
            'socks5://5.128.73.5:1080',
        ]
    }
}


@dataclass
class ProxySettings:
    USE_PROXY: int
    PROXY_LIST: List[str]


@dataclass
class Config:
    GIBDD_HOST_URL: str
    ROTATING_PROXIES: bool | int
    SESSION_MAX_RETRIES: int
    SESSION_TIMEOUT: int
    PROXY_SETTINGS: ProxySettings


def load_config(yml_config_path: Path, ):
    pass
