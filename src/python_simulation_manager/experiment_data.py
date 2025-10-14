from __future__ import annotations
import numpy as np
from typing import Any, Generic, TypeVar,Type
from .output import ExperimentOutput
from .runnner import*
from pathlib import Path
 


OutType =  TypeVar("OutType", bound= ExperimentOutput) 

class ExperimentData(Generic[OutType]):
    def __init__(self):
        self.verbose_log: bool                     = False
        self.proj_dir: Path                        = Path()
        self.out_paths:   dict[int|float, Path]    = dict()
        self.param_paths: dict[int|float, Path]    = dict()
        self.target_dir: Path                      = Path()
        self._scale_variables: list|np.ndarray|None = None
        self.scale_variable_names: list[str]        = ["L"]  
        self.static_params:  dict[str, Any]         = dict()
        self.scaling_params: dict[str, dict]        = dict()
        self.out_type: type[OutType]|None           = None                
        self.runner: IRunner|None                   = None

    def copy_data(self, exp_data: ExperimentData):
        self.verbose_log          = exp_data.verbose_log
        self.proj_dir             = exp_data.proj_dir
        self.out_paths            = exp_data.out_paths
        self.param_paths          = exp_data.param_paths
        self.target_dir           = exp_data.target_dir
        self._scale_variables     = exp_data._scale_variables
        self.scale_variable_names = exp_data.scale_variable_names
        self.static_params        = exp_data.static_params
        self.scaling_params       = exp_data.scaling_params
        self.out_type             = exp_data.out_type
        self.runner               = exp_data.runner

    
if __name__ == "__main__":
    pass
 