from __future__ import annotations
import numpy as np
from typing import Any, Generic, TypeVar,Type
from abc import ABC, abstractmethod

from .output import ExperimentOutput
from .runnner import*
from pathlib import Path
from .experiment_data import ExperimentData

OutType = TypeVar("OutType", bound = ExperimentOutput) 
  
    
class AbstractExperimentBuilder(Generic[OutType]):
    def __init__(self, proj_dir: Path, results_dir: str, exp_name: str, verbose_log:bool = False):
        self.experiment                      = ExperimentData()
        self.experiment.verbose_log          = verbose_log
        self.experiment.proj_dir             = proj_dir
        self.experiment.target_dir           = self.__get_target_dir(results_dir, exp_name)
        self.paths_are_set = False
        
    def _log_path(self, path: Path) -> Path:
        if not self.experiment.verbose_log:
            return path.relative_to(self.experiment.proj_dir)
        return path

    def __get_target_dir(self, results_dir: str, exp_name: str):
        _results_dir = self.experiment.proj_dir.joinpath(results_dir)
        target_dir   = _results_dir.joinpath(exp_name)
        
        if not self.experiment.proj_dir.exists():
            raise NotADirectoryError(f">> Project Directory \"{self._log_path(self.experiment.proj_dir)}\" Not Found.")
        else:
            if not self.experiment.verbose_log:
                print(f">> Project Directory \"{self.experiment.proj_dir.name}\" Found.")
            else:
                print(f">> Project Directory \"{self.experiment.proj_dir}\" Found.")
                
        if target_dir.exists():
            print(f">> Directory \"{self._log_path(target_dir)}\" Found.")
        else:
            target_dir.mkdir(parents=True)
            print(f">> Directory \"{self._log_path(target_dir)}\" created.")
        return target_dir

    def _set_files(self):
        print(">> Setting file paths:")
        if self.experiment._scale_variables is None:
            raise ValueError("set_files() Error: No scale variables")
        
        prefix = dict()
        for L in self.experiment._scale_variables:
            prefix[L] = ",".join([f"{scale_name}={L}" for scale_name in self.experiment.scale_variable_names])

        for L in self.experiment._scale_variables:
            self.experiment.param_paths[L] = self.experiment.target_dir.joinpath(f"parameter_{prefix[L]}.txt")
            print(f"-- setting paramfile \"{self._log_path(self.experiment.param_paths[L])}\"")
            
        for L in self.experiment._scale_variables:           
            self.experiment.out_paths[L] = self.experiment.target_dir.joinpath(f"out_{prefix[L]}.txt")
            print(f"-- setting outfile \"{self._log_path(self.experiment.out_paths[L])}\"")
        self.paths_are_set = True

    def set_scale_variables(self, variables: list|np.ndarray):
        self.experiment._scale_variables = variables
        
    def set_scale_variable_names(self, names: list[str]):
        self.experiment.scale_variable_names = names

    def __scale_variables_from_dict(self, scaling_param: dict[int|float, Any]):
        scale_variables = []
        for L in scaling_param.keys():
            scale_variables.append(L)
        scale_variables.sort()
        return scale_variables

    def __is_valid_scaling_parameter(self, name: str, new_scaling_param: dict) -> bool:
        if len(self.experiment.scaling_params) == 0:
            return True
        
        new_length = []
        for L in new_scaling_param.keys():
            if not isinstance(L, int) or isinstance(L, float):
                print(f">> Error \"{name}\" contains non scaling key {L}")
                return False
            new_length.append(L)
            
        new_length.sort()
        for key, params in self.experiment.scaling_params.items():
            length = self.__scale_variables_from_dict(params)
            
            if new_length != length:
                print(f">> Error \"{name}\" does not contain same scaling parameters as {key}")
                return False
        return True         
 
    def set_output_type(self, out_type: Type[OutType]):
        self.experiment.out_type = out_type       
    
    def add_static_parameter(self, key: str, value):
        print(f">> Succesfully added \"{key}\"")
        self.experiment.static_params.update({key : value})
        
    def add_scaling_parameter(self, name: str, new_param: dict):
        if not self.__is_valid_scaling_parameter(name, new_param):
            return
        print(f">> Succesfully added \"{name}\"")
        self.experiment.scaling_params.update({name : new_param})
        if self.experiment._scale_variables is None:
            self.experiment._scale_variables = self.__scale_variables_from_dict(new_param)

    def set_static_parameter(self, key, value):
        try:
            self.experiment.static_params[key] = value
            print(f">> \"{key}\" set")
        except KeyError as _:
            print(f">> Key \"{key}\" not found")
    
    def set_scaling_parameter(self, key, value):
        try:
            self.experiment.scaling_params[key] = value
            print(f">> \"{key}\" set")
        except KeyError as _:
            print(f">> Key \"{key}\" not found")
    
    @abstractmethod
    def build(self, load_only = False) -> Any: 
        ...

if __name__ == "__main__":
    pass
 