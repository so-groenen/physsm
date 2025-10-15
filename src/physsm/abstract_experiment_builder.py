from __future__ import annotations
import numpy as np
from typing import Any, Generic, TypeVar,Type
from abc import abstractmethod
from .experiment_output import ExperimentOutput
from .runnner import*
from pathlib import Path
from .experiment_data import BaseExperimentData, PathData, Parameters

OutType = TypeVar("OutType", bound = ExperimentOutput) 

class FileData:
    def __init__(self, file_name: str, extension: str) -> None:
        self.file_name  = file_name
        self.extension  = extension
    def set_extension(self, extension: str):
        self.extension = extension
    def set_output_name(self, filename: str):
        self.file_name = filename
 

class AbstractExperimentBuilder(Generic[OutType]):
    def __init__(self, proj_dir: Path, results_dir: str, exp_name: str, verbose_log:bool = False):
        self.verbose_log                     = verbose_log
        self.experiment                      = BaseExperimentData()
        self.parameters                      = Parameters()
        self.out_data                        = FileData(file_name="out", extension="txt")
        self.param_data                      = FileData(file_name="parameter", extension="txt")
        self.paths_data                      = PathData()
        self.paths_are_set                   = False
        self.verbose_log                     = verbose_log
        self.experiment.verbose_log          = verbose_log
        self.paths_data.set_proj_dir(proj_dir)
        self.paths_data.set_target_dir(results_dir, exp_name, verbose_log)
        
    def _log_path(self, path: Path) -> Path:
        if not self.verbose_log:
            return path.relative_to(self.paths_data.proj_dir)
        return path
    
    def _set_files(self):
        print(">> Setting file paths:")
        if self.parameters.scale_variables is None:
            raise ValueError("set_files() Error: No scale variables")
        suffix = dict()

        out_name   = self.out_data.file_name
        out_ext    = self.out_data.extension 
        param_name = self.param_data.file_name
        param_ext  = self.param_data.extension

        for L in self.parameters.scale_variables:
            suffix[L] = ",".join([f"{scale_name}={L}" for scale_name in self.parameters.scale_variable_names])

        for L in self.parameters.scale_variables:
            param_path_name = f"{param_name}_{suffix[L]}.{param_ext}"
            self.paths_data.set_param_path(L, param_path_name, self.verbose_log)
            
        for L in self.parameters.scale_variables:          
            out_path_name = f"{out_name}_{suffix[L]}.{out_ext}"
            self.paths_data.set_out_path(L, out_path_name, self.verbose_log)

        self.experiment.paths_data = self.paths_data
        self.experiment.parameters = self.parameters 
        self.paths_are_set = True

    def set_parameter_file_data(self, filename: str="parameter", extension = "txt"):
        self.param_data.set_extension(extension)
        self.param_data.set_output_name(filename)
    
    def set_output_file_data(self, key: str = "outputfile", filename: str="out", extension = "txt"):
        self.experiment.out_key = key 
        self.out_data.set_extension(extension)
        self.out_data.set_output_name(filename)

    def set_scale_variables(self, variables: list|np.ndarray):
        self.parameters.scale_variables = variables
        
    def set_scale_variable_names(self, names: list[str]):
        self.parameters.scale_variable_names = names

    def set_output_type(self, out_type: Type[OutType]):
        self.experiment.out_type = out_type       
        
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
 