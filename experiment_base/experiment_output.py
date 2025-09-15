from typing import Protocol
import numpy as np


class ExperimentOutput(Protocol):
    def __init__(self, file_name):
        self.file_name = file_name

    def has_file(self)->bool:
        try:
            with open(self.file_name, "r") as _:
                pass
            return True
        except Exception as e:
            print(f"Could not open file: {e}")
            return False
        
    def __to_nd_array(self, name):
        my_lists = getattr(self, name)
        
        if not isinstance(my_lists, np.ndarray):            
            setattr(self, name, np.asarray(my_lists))

    def all_lists_to_array(self):
        for name in vars(self).keys():
            if name != "elapsed_time":
                self.__to_nd_array(name)

    def parse_output(self, line_number: int, lines: str):
        pass

    def grab_files(self) -> None:
        if not self.has_file():
            return
        with open(self.file_name, "r") as file:
            for (n, lines) in enumerate(file):
                self.parse_output(n, lines)
        self.all_lists_to_array()