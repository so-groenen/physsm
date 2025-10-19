from pathlib import Path
from typing import override
from abc import ABC, abstractmethod

class IPathLogger(ABC):
    @abstractmethod
    def log_path(self, path: Path) -> Path:
        ...        
    @abstractmethod
    def is_verbose(self) -> bool:
        ...

class PathLogger(IPathLogger):
    def __init__(self, proj_dir: Path = Path(""), verbose_log: bool = False) -> None:
        self.proj_dir    = proj_dir
        self.verbose_log = verbose_log
    
    @override
    def log_path(self, path: Path) -> Path:
        if not self.verbose_log:
            return path.relative_to(self.proj_dir)
        return path
    
    @override
    def is_verbose(self) -> bool:
        return self.verbose_log