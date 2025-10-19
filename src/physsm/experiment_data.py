from __future__ import annotations
import numpy as np
from typing import Any, TypeVar
from .experiment_output import ExperimentOutput
from .runnner import*
from pathlib import Path
from .path_logger import PathLogger, IPathLogger

class PathData:
    def __init__(self, logger: IPathLogger) -> None:
        self.proj_dir: Path                        = Path()
        self.out_paths:   dict[int|float, Path]    = dict()
        self.param_paths: dict[int|float, Path]    = dict()
        self.target_dir: Path                      = Path()
        self.path_logger: IPathLogger              = logger
        
    def log_path(self, path: Path) -> Path:
        return self.path_logger.log_path(path)

    def set_param_path(self, key, path_name: str):       
        self.param_paths[key] =  self.target_dir.joinpath(path_name)
        print(f"-- setting paramfile \"{self.log_path(self.param_paths[key])}\"")
        
    def set_out_path(self, key, out_path_name: str):       
        self.out_paths[key] = self.target_dir.joinpath(out_path_name)
        print(f"-- setting outfile \"{self.log_path(self.out_paths[key])}\"")

    def set_logger(self, logger: IPathLogger):
        self.path_logger = logger
    
    def set_proj_dir(self, proj_dir):
        self.proj_dir = proj_dir
        
    def set_target_dir(self, results_dir: str, exp_name: str):
           
        _results_dir = self.proj_dir.joinpath(results_dir)
        target_dir   = _results_dir.joinpath(exp_name)
        if not self.proj_dir.exists():
            raise NotADirectoryError(f">> Project Directory \"{self.log_path(self.proj_dir)}\" Not Found.")
        else:
            if not self.path_logger.is_verbose():
                print(f">> Project Directory \"{self.proj_dir.name}\" Found.")
            else:
                print(f">> Project Directory \"{self.proj_dir}\" Found.")
                
        if target_dir.exists():
            print(f">> Directory \"{self.log_path(target_dir)}\" Found.")
        else:
            target_dir.mkdir(parents=True)
            print(f">> Directory \"{self.log_path(target_dir)}\" created.")

        self.target_dir = target_dir
      

class Parameters:
    def __init__(self) -> None:
        self.scale_variables: list|np.ndarray|None = None
        self.scale_variable_names: list[str]       = ["L"]  
        self.static_params:  dict[str, Any]        = dict()
        self.scaling_params: dict[str, dict]       = dict()
        
    @staticmethod
    def get_scale_variables_from_dict(scaling_param: dict[int|float, Any]):
        scale_variables = []
        for L in scaling_param.keys():
            scale_variables.append(L)
        scale_variables.sort()
        return scale_variables

    def compare_new_scaling_param(self, name: str, new_scaling_param: dict) -> bool:
        new_lengths = Parameters.get_scale_variables_from_dict(new_scaling_param) 
        
        for key, params in self.scaling_params.items():
            lengths = Parameters.get_scale_variables_from_dict(params)
            if new_lengths != lengths:
                ValueError(f"\"{name}\" does not contain same scaling parameters as {key}")
        return True
    
    def valididate_scaling_parameter(self, name: str, new_scaling_param: dict):
       
        for L in new_scaling_param.keys():
            if not isinstance(L, int) or isinstance(L, float):
                raise ValueError(f"\"{name}\" contains non scaling key {L}")
        if self.scaling_params is None or len(self.scaling_params) == 0:
            return 
        self.compare_new_scaling_param(name, new_scaling_param)

    def add_scaling_parameter(self, name: str, new_scaling_param: dict):
        try:
            self.valididate_scaling_parameter(name, new_scaling_param)
        except Exception as e:
            raise ValueError(f"add_scaling_parameter() error {e.args}")
        
        print(f">> Succesfully added \"{name}\"")
        self.scaling_params.update({name : new_scaling_param})
        
        if self.scale_variables is None:
            self.scale_variables = Parameters.get_scale_variables_from_dict(new_scaling_param)
    
    def add_static_parameter(self, key: str, value):
        print(f">> Succesfully added \"{key}\"")
        self.static_params.update({key : value})
    
    def set_static_parameter(self, key, value):
        try:
            self.static_params[key] = value
            print(f">> \"{key}\" set")
        except KeyError as _:
            print(f">> Key \"{key}\" not found")
    
    def set_scaling_parameter(self, key, value):
        try:
            self.scaling_params[key] = value
            print(f">> \"{key}\" set")
        except KeyError as _:
            print(f">> Key \"{key}\" not found")
            
OutType =  TypeVar("OutType", bound= ExperimentOutput,) 

class BaseExperimentData[OutType]:
    def __init__(self, paths_data: PathData):
        self.paths_data: PathData          = paths_data
        self.parameters                    = Parameters()        
        self.out_type: type[OutType]|None  = None                
        self.runner: IRunner|None          = None
        self.out_key                       = "outputfile"

    def copy_data(self, exp_data: BaseExperimentData):
        self.paths_data    = exp_data.paths_data
        self.parameters    = exp_data.parameters 
        self.out_type      = exp_data.out_type
        self.runner        = exp_data.runner
        self.out_key       = exp_data.out_key

    def log_path(self, path: Path):
        return self.paths_data.log_path(path)
    def is_verbose_log(self) -> bool:
        return self.paths_data.path_logger.is_verbose()
    
if __name__ == "__main__":
    pass
 