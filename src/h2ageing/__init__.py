"""h2ageing: effect of stack ageing on the life cycle assessment of a hydrogen chain
(PEM electrolyser, compression, type IV tank, PEM fuel cell)."""
from .config import load_config, with_values
from .run import run

__all__ = ["load_config", "with_values", "run"]
__version__ = "1.0.0"
