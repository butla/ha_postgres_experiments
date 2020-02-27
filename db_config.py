from dataclasses import dataclass


@dataclass
class DBSettings:
    host: str
    port: int
    user: str


DATABASES = [
    DBSettings('142.93.131.34', 5432, 'postgres'),
    DBSettings('64.227.47.75', 5432, 'postgres'),
]
