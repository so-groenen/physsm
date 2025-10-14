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
        self.paths_data.proj_dir             = proj_dir
        self.paths_data.target_dir           = self._get_target_dir(proj_dir, results_dir, exp_name, verbose_log)   
        self.paths_are_set                   = False
        self.experiment.verbose_log          = verbose_log

    def _log_path(self, path: Path) -> Path:
        if not self.verbose_log:
            return path.relative_to(self.paths_data.proj_dir)
        return path
        
    def _get_target_dir(self, proj_dir: Path, results_dir: str, exp_name: str, verbose = False):
        _results_dir = proj_dir.joinpath(results_dir)
        target_dir   = _results_dir.joinpath(exp_name)
        if not proj_dir.exists():
            raise NotADirectoryError(f">> Project Directory \"{self._log_path(proj_dir)}\" Not Found.")
        else:
            if not verbose:
                print(f">> Project Directory \"{proj_dir.name}\" Found.")
            else:
                print(f">> Project Directory \"{proj_dir}\" Found.")
                
        if target_dir.exists():
            print(f">> Directory \"{self._log_path(target_dir)}\" Found.")
        else:
            target_dir.mkdir(parents=True)
            print(f">> Directory \"{self._log_path(target_dir)}\" created.")
        return target_dir

    def _set_files(self):
        print(">> Setting file paths:")
        if self.parameters.scale_variables is None:
            raise ValueError("set_files() Error: No scale variables")
        suffix = dict()
        out_name   = self.out_data.file_name
        ext        = self.out_data.extension 
        target_dir = self.paths_data.target_dir
        param_name = self.param_data.file_name
        param_ext  = self.param_data.extension
        
        for L in self.parameters.scale_variables:
            suffix[L] = ",".join([f"{scale_name}={L}" for scale_name in self.parameters.scale_variable_names])
        for L in self.parameters.scale_variables:
            self.paths_data.param_paths[L] = target_dir.joinpath(f"{param_name}_{suffix[L]}.{param_ext}")
            print(f"-- setting paramfile \"{self._log_path(self.paths_data.param_paths[L])}\"")
        for L in self.parameters.scale_variables:          
            self.paths_data.out_paths[L] = target_dir.joinpath(f"{out_name}_{suffix[L]}.{ext}")
            print(f"-- setting outfile \"{self._log_path(self.paths_data.out_paths[L])}\"")
            
        self.paths_are_set = True
        self.experiment.paths_data = self.paths_data
        self.experiment.parameters = self.parameters 
    
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

    def __scale_variables_from_dict(self, scaling_param: dict[int|float, Any]):
        scale_variables = []
        for L in scaling_param.keys():
            scale_variables.append(L)
        scale_variables.sort()
        return scale_variables

    def __is_valid_scaling_parameter(self, name: str, new_scaling_param: dict) -> bool:
        if len(self.parameters.scaling_params) == 0:
            return True
        
        new_length = []
        for L in new_scaling_param.keys():
            if not isinstance(L, int) or isinstance(L, float):
                print(f">> Error \"{name}\" contains non scaling key {L}")
                return False
            new_length.append(L)
            
        new_length.sort()
        for key, params in self.parameters.scaling_params.items():
            length = self.__scale_variables_from_dict(params)
            
            if new_length != length:
                print(f">> Error \"{name}\" does not contain same scaling parameters as {key}")
                return False
        return True         
 
    def set_output_type(self, out_type: Type[OutType]):
        self.experiment.out_type = out_type       
        
    def add_static_parameter(self, key: str, value):
        print(f">> Succesfully added \"{key}\"")
        self.parameters.static_params.update({key : value})
        
    def add_scaling_parameter(self, name: str, new_param: dict):
        if not self.__is_valid_scaling_parameter(name, new_param):
            return
        print(f">> Succesfully added \"{name}\"")
        self.parameters.scaling_params.update({name : new_param})
        if self.parameters.scale_variables is None:
            self.parameters.scale_variables = self.__scale_variables_from_dict(new_param)

    def set_static_parameter(self, key, value):
        try:
            self.parameters.static_params[key] = value
            print(f">> \"{key}\" set")
        except KeyError as _:
            print(f">> Key \"{key}\" not found")
    
    def set_scaling_parameter(self, key, value):
        try:
            self.parameters.scaling_params[key] = value
            print(f">> \"{key}\" set")
        except KeyError as _:
            print(f">> Key \"{key}\" not found")
    
    @abstractmethod
    def build(self, load_only = False) -> Any: 
        ...

if __name__ == "__main__":
    pass
 