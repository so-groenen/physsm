from __future__ import annotations
from abc import abstractmethod
import numpy as np
from pathlib import Path

class ExperimentOutput:
    def __init__(self, out_path):
        self.file: Path = out_path
    
    @abstractmethod
    def parse_output(self, line_number: int, line: str):
        ...
    
    def has_file(self) -> bool:
        return self.file.exists()
        
    def __to_nd_array(self, name):
        my_lists = getattr(self, name)
        
        if isinstance(my_lists, list):            
            setattr(self, name, np.asarray(my_lists))

    def all_lists_to_array(self):
        for name in vars(self).keys():
            self.__to_nd_array(name)

    def grab_files(self) -> None:
        if not self.has_file():
            raise ValueError("Error: outputfile not found")
        
        with self.file.open("r") as file:
            for (n, line) in enumerate(file):
                self.parse_output(n, line)
        self.all_lists_to_array()
 