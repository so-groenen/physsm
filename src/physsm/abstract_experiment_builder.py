from __future__ import annotations
import numpy as np
from typing import Any, Generic, TypeVar,Type
from abc import abstractmethod
from .experiment_output import ExperimentOutput
from .runnner import*
from .experiment_data import BaseExperimentData, PathData, Parameters
from .path_logger import IPathLogger, PathLogger
from pathlib import Path

OutType = TypeVar("OutType", bound = ExperimentOutput) 

class FileData:
    def __init__(self, file_name: str, extension: str) -> None:
        self.file_name  = file_name
        self.extension  = extension
    def set_extension(self, extension: str):
        self.extension = extension
    def set_output_name(self, filename: str):
        self.file_name = filename
 
class OutputClassData(FileData, Generic[OutType]):
    def __init__(self, file_name: str, extension: str, out_key ="outputfile", out_type: type[OutType] = ExperimentOutput) -> None:
        super().__init__(file_name, extension)
        self.out_key    = out_key
        self.out_type   = out_type
    def set_key(self, key: str):
        self.out_key = key
        
    def set_out_type(self, out_type: type[OutType]):
        self.out_type = out_type

        
class AbstractExperimentBuilder(Generic[OutType]):
    def __init__(self, proj_dir: Path, results_dir: str, exp_name: str, logger: IPathLogger):
        self.parameters                      = Parameters()
        self.param_file_data                 = FileData(file_name="parameter", extension="txt")
        self.out_data                        = OutputClassData(file_name="out",extension="txt",out_key="outputfile",out_type=ExperimentOutput)
        self.paths_data                      = PathData(logger)
        self.paths_data.set_proj_dir(proj_dir)
        self.paths_data.set_target_dir(results_dir, exp_name)
        
    def log_path(self, path: Path) -> Path:
        return self.paths_data.log_path(path)
    
    def __set_paths(self):
        print(">> Setting file paths:")
        if self.parameters.scale_variables is None:
            raise ValueError("set_files() Error: No scale variables")
        suffix = dict()

        out_name   = self.out_data.file_name
        out_ext    = self.out_data.extension 
        param_name = self.param_file_data.file_name
        param_ext  = self.param_file_data.extension

        for L in self.parameters.scale_variables:
            suffix[L] = ",".join([f"{scale_name}={L}" for scale_name in self.parameters.scale_variable_names])

        for L in self.parameters.scale_variables:
            param_path_name = f"{param_name}_{suffix[L]}.{param_ext}"
            self.paths_data.set_param_path(L, param_path_name)
            
        for L in self.parameters.scale_variables:          
            out_path_name = f"{out_name}_{suffix[L]}.{out_ext}"
            self.paths_data.set_out_path(L, out_path_name)

    def _make_base_experiment(self) -> BaseExperimentData:
        self.__set_paths()
        base_exp = BaseExperimentData(self.paths_data)
        base_exp.out_key    = self.out_data.out_key
        base_exp.out_type   = self.out_data.out_type
        base_exp.parameters = self.parameters 
        base_exp.paths_data = self.paths_data 
        return base_exp

    def set_parameter_file_data(self, filename: str="parameter", extension = "txt"):
        self.param_file_data.set_extension(extension)
        self.param_file_data.set_output_name(filename)
    
    def set_output_file_data(self, key: str = "outputfile", filename: str="out", extension = "txt"):
        self.out_data.set_extension(extension)
        self.out_data.set_output_name(filename)
        self.out_data.set_key(key)
    
    def set_scale_variables(self, variables: list|np.ndarray):
        self.parameters.scale_variables = variables
        
    def set_scale_variable_names(self, names: list[str]):
        self.parameters.scale_variable_names = names

    def set_output_type(self, out_type: Type[OutType]):
        self.out_data.set_out_type(out_type)

    def add_static_parameter(self, key: str, value):
        self.parameters.add_static_parameter(key, value)
        
    def add_scaling_parameter(self, name: str, new_param: dict):
        self.parameters.add_scaling_parameter(name, new_param)

    def set_static_parameter(self, key, value):
        self.parameters.set_static_parameter(key, value)
    
    def set_scaling_parameter(self, key, value):
        self.parameters.set_scaling_parameter(key, value)
    
    @abstractmethod
    def build(self, load_only = False) -> Any: 
        ...

if __name__ == "__main__":
    pass
 