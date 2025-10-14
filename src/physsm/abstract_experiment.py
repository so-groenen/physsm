from __future__ import annotations
import numpy as np
from typing import Any, Generic 
from abc import abstractmethod, ABC
from pathlib import Path
from io import TextIOWrapper

from .experiment_data import BaseExperimentData, OutType
from .runnner import*

def array_to_str(array: np.ndarray, rounding: int) -> str:
    temps_str = []
    for val in array:
        temps_str.append(str(round(val, rounding)))
    return ", ".join(temps_str)

class AbstractExperiment(ABC, BaseExperimentData, Generic[OutType]):
    def __init__(self):
        super().__init__()

    def _log_path(self, path: Path) -> Path:
        if not self.verbose_log:
            return path.relative_to(self.paths_data.proj_dir)
        return path
        
    def get_scale_variables(self) -> Any:
        if self.parameters.scale_variables is None:
            raise ValueError("scale_variables() Error: No scale variables")
        return self.parameters.scale_variables

    def get_static_parameter(self, key) -> Any:
        return self.parameters.static_params[key]
 
    def get_scaling_parameter(self, key) -> dict:
        return self.parameters.scaling_params[key]
            
    def __write_formated(self, L, delim: str=':', rounding=3):     
        
        out_key = self.out_key      
        with self.paths_data.param_paths[L].open("w") as file:
            for name in self.parameters.scale_variable_names:
                file.write(f"{name}{delim} {L}\n")
            self.__write_static(file, delim, rounding)
            self.__write_scaling(file, L, delim, rounding)
            file.write(f"{out_key}{delim} {self.paths_data.out_paths[L]}")
            
    def __write_scaling(self, file: TextIOWrapper, L, delim: str, rounding: int):
         for key in self.parameters.scaling_params:
            param_value = self.get_scaling_parameter(key)[L]
            
            if isinstance(param_value, np.ndarray):
                param_value = array_to_str(param_value, rounding)
            file.write(f"{key}{delim} {param_value}\n")
            
    def __write_static(self, file: TextIOWrapper, delim: str, rounding: int):
        for key in self.parameters.static_params:
            param = self.get_static_parameter(key)
            if isinstance(param, np.ndarray):
                param = array_to_str(param, rounding)
            file.write(f"{key}{delim} {param}\n")
 
    def write_parameter_file(self, L: int, delim: str=':', rounding=3) -> bool:
        try:
            self.__write_formated(L, delim, rounding)
            print(f"-- \"{self._log_path(self.paths_data.param_paths[L])}\": ", end="")          
            return True
        except Exception as e:
            print(f"write_parameter_file error: {e}, {e.args}")
            return False
            
    def write_parameter_files(self, delim: str=':', rounding=3):        
        if self.parameters.scale_variables is None:
            raise ValueError("writing parameter Error: scale_variables not set!")
        
        print(f">> writing parameter files:")
        for L in self.parameters.scale_variables:
            try:
                if self.write_parameter_file(L, delim, rounding):
                    print("done")
            except Exception as e:
                print(f"write_parameter_files Error: {e}, {e.args}")
 
    def are_parameter_files_available(self) -> bool:        
        has_all_files = True
        missing_files: list[Path] = []
        print(">> Looking for parameter files:")
        if self.parameters.scale_variables is None:
            print(f"* No scale_variables set")
            return False
        
        for L in self.parameters.scale_variables:
            param_path = self.paths_data.param_paths[L]
            if param_path.exists():
                print(f"-- Found parameter file: {self._log_path(param_path)}")
            else:
                missing_files.append(param_path)
                has_all_files = False
                
        if has_all_files:
            print("* Parameter files available")
        else:
            print("* Not all parameter files created yet:")    
            for files in missing_files:
                print(f"-- not written yet: {self._log_path(files)}")
        return has_all_files
     
    def get_parameter_path(self, L):
        return self.paths_data.param_paths[L]
    
    def get_output(self, L):
        return self.paths_data.out_paths[L]
    
    def has_output(self, L):
        return self.paths_data.out_paths[L].exists()
    
    def are_results_available(self) -> bool:
        if self.parameters.scale_variables is None:
            print("* No scale variables found, cannot search results.")
            return False 
        
        all_available = True
        some_availabe = False
        missing_files = []
        print(">> Looking for output files:")
        for L in self.parameters.scale_variables:
            file = self.paths_data.out_paths[L]  
            if self.has_output(L):
                print(f"-- Found output: {self._log_path(file)}")
                some_availabe = True
            else:
                missing_files.append(file)
                all_available = False
                
        if not all_available:
            print(f"* missing output:")
            for file in missing_files:
                print(f"-- {self._log_path(file)}")
        if not some_availabe:
            print("* No output files created yet.")
            
        return some_availabe

    def get_results(self) -> dict[int, OutType]: 
        if self.parameters.scale_variables is None:
            raise ValueError("get_results() error: scale_variables not set!")
        
        if self.out_type is None:
            raise TypeError("get_results() error: output_type not set!")
         
        has_results = False
        results: dict[int, OutType] = dict()
        
        for L in self.parameters.scale_variables:
            if self.has_output(L):
                if self.verbose_log:
                    print(f"Found output: \"{self._log_path(self.get_output(L))}")
                has_results = True
        if not has_results:
            return dict()
 
        for L in self.parameters.scale_variables:
            if self.has_output(L):
                results[L] = self.out_type(self.get_output(L))
                results[L].grab_files()
        return results
     
    @abstractmethod
    def run(self, scale: int|float, env_var:dict|None = None, verbose_log = False) -> None:
        ...

if __name__ == "__main__":
    pass
 