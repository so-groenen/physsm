from __future__ import annotations
from typing import override
from abc import ABC
import subprocess
from pathlib import Path

class IRunner(ABC):
    def run(self, cwd: Path, args: Path, verbose_log: bool = False, my_env: None | dict = None):
        raise NotImplementedError()



if __name__ == "__main__":
    print("")