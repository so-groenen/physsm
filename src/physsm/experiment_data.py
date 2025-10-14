from __future__ import annotations
import numpy as np
from typing import Any, TypeVar
from .experiment_output import ExperimentOutput
from .runnner import*
from pathlib import Path
from dataclasses import dataclass

 

class PathData:
    proj_dir: Path                        = Path()
    out_paths:   dict[int|float, Path]    = dict()
    param_paths: dict[int|float, Path]    = dict()
    target_dir: Path                      = Path()

class Parameters:
    scale_variables: list|np.ndarray|None = None
    scale_variable_names: list[str]       = ["L"]  
    static_params:  dict[str, Any]        = dict()
    scaling_params: dict[str, dict]       = dict()
    
OutType =  TypeVar("OutType", bound= ExperimentOutput,) 

class BaseExperimentData[OutType]:
    def __init__(self):
        self.verbose_log: bool             = False
        self.paths_data                    = PathData()
        self.parameters                    = Parameters()        
        self.out_type: type[OutType]|None  = None                
        self.runner: IRunner|None          = None
        self.out_key                       = "outputfile"

    def copy_data(self, exp_data: BaseExperimentData):
        self.verbose_log          = exp_data.verbose_log
        self.paths_data           = exp_data.paths_data
        self.paths_data           = self.paths_data 
        self.parameters           = exp_data.parameters 
        self.out_type             = exp_data.out_type
        self.runner               = exp_data.runner
        self.out_key              = exp_data.out_key

    
if __name__ == "__main__":
    pass
 