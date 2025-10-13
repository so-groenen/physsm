from __future__ import annotations
import numpy as np
from typing import Any, Generic, TypeVar,Type
from .output import ExperimentOutput
from .runnner import*
from pathlib import Path
from io import TextIOWrapper
 

def array_to_str(array: np.ndarray, rounding: int) -> str:
    temps_str = []
    for val in array:
        temps_str.append(str(round(val, rounding)))
    return ", ".join(temps_str)
 

OutType = TypeVar("OutType", bound = ExperimentOutput) 
 
class ExperimentHandler(Generic[OutType]):
    
    def __init__(self, proj_dir: Path, exp_dir_name: str, results_dir_name: str, verbose_log:bool = False):
        self.verbose_log: bool                  = verbose_log
        if self.verbose_log:
            print(">> verbose log is On: All paths shown are Absolute]")
        
        self.proj_dir: Path                     = proj_dir
        self.out_paths:   dict[int|float, Path] = dict()
        self.param_paths: dict[int|float, Path] = dict()
        self.target_dir: Path                   = self.__get_target_dir(results_dir_name, exp_dir_name)
        self.paths_are_set                      = False
        
        self.scale_variables: list|np.ndarray|None = None
        self.scale_variable_names: list[str]       = ["L"]

        self.static_params:  dict[str, Any]   = dict()
        self.scaling_params: dict[str, dict]  = dict()

        self.out_type: Type[OutType]|None          = None
        self.runner: IRunner|None                  = None

        
    def _log_path(self, path: Path) -> Path:
        if not self.verbose_log:
            return path.relative_to(self.proj_dir)
        return path
        
        
    def __get_target_dir(self, results_dir_name: str, exp_dir_name: str):
        results_dir = self.proj_dir.joinpath(results_dir_name)
        target_dir   = results_dir.joinpath(exp_dir_name)
        
        if not self.proj_dir.exists():
            raise NotADirectoryError(f">> Project Directory \"{self._log_path(self.proj_dir)}\" Not Found.")
        else:
            if not self.verbose_log:
                print(f">> Project Directory \"{self.proj_dir.name}\" Found.")
            else:
                print(f">> Project Directory \"{self.proj_dir}\" Found.")
                
        if target_dir.exists():
            print(f">> Directory \"{self._log_path(target_dir)}\" Found.")
        else:
            target_dir.mkdir(parents=True)
            print(f">> Directory \"{self._log_path(target_dir)}\" created.")
        return target_dir

    def set_files(self):
        print(">> Setting file paths:")
        if self.scale_variables is None:
            raise ValueError("set_files() Error: No scale variables")
        
        prefix = dict()
        for L in self.scale_variables:
            prefix[L] = ",".join([f"{scale_name}={L}" for scale_name in self.scale_variable_names])

        for L in self.scale_variables:
            self.param_paths[L] = self.target_dir.joinpath(f"parameter_{prefix[L]}.txt")
            print(f"-- setting paramfile \"{self._log_path(self.param_paths[L])}\"")
            
        for L in self.scale_variables:           
            self.out_paths[L] = self.target_dir.joinpath(f"out_{prefix[L]}.txt")
            print(f"-- setting outfile \"{self._log_path(self.out_paths[L])}\"")
        self.paths_are_set = True

    def get_scale_variables(self) -> Any:
        if self.scale_variables is None:
            raise ValueError("get_scale_variables() Error: No scale variables")
        return self.scale_variables

    def set_scale_variables(self, variables: list|np.ndarray):
        self.scale_variables = variables
        
    def set_scale_variable_names(self, names: list[str]):
        self.scale_variable_names = names

    def set_executable(self, binary_path: Path):
        self.runner = BinaryRunner(binary_path)
        print(f">> Binary path set to \"{self._log_path(binary_path)}\" [Current mode: Binary mode]")
        
    def set_cargo_toml_path(self, cargo_toml_path: Path):
        self.runner = CargoRunner(cargo_toml_path)
        print(f">> Cargo toml path set to \"{self._log_path(cargo_toml_path)}\" [Current mode: Cargo mode]")

    def __get_scale_variables_from_dict(self, scaling_param: dict[int|float, Any]):
        scale_variables = []
        for L in scaling_param.keys():
            scale_variables.append(L)
        scale_variables.sort()
        return scale_variables
    
    def run_executable(self, scale: int|float, env_var:dict|None = None, verbose = False):
        if self.runner is None:
            raise TypeError("run_executable() error: Runner not set [use: set_executable]")
        
        if not isinstance(self.runner, BinaryRunner):
            raise TypeError("run_executable() error: Runner not set to BinaryRunner [use: set_executable]")
        try:
            param_path = self.get_parameter_path(scale)
        except KeyError as _:
            print(">> run_cargo: cannot find parameter")            
            return

        cwd  = self.proj_dir
        args = param_path
        self.runner.run(cwd, args, verbose, env_var)

    def run_cargo(self, scale: int|float, env_var:dict|None = None, verbose:bool = False):
        if self.runner is None:
            raise TypeError("run_cargo() error: Runner not set [use: set_executable]")        
        
        if not isinstance(self.runner, CargoRunner):
            raise TypeError("run_cargo() error: : Runner not set to CargoRunner [use: set_cargo_toml_path]")
        try:
            param_path = self.get_parameter_path(scale)
        except KeyError as _:
            print(">> run_cargo: cannot find parameter")            
            return
              
        cwd  = self.proj_dir
        args = param_path
        self.runner.run(cwd, args, verbose, env_var)

    
    def __is_valid_scaling_parameter(self, name: str, new_scaling_param: dict) -> bool:
        if len(self.scaling_params) == 0:
            return True
        
        new_length = []
        for L in new_scaling_param.keys():
            if not isinstance(L, int) or isinstance(L, float):
                print(f">> Error \"{name}\" contains non scaling key {L}")
                return False
            new_length.append(L)
            
        new_length.sort()
        for key, params in self.scaling_params.items():
            length = self.__get_scale_variables_from_dict(params)
            
            if new_length != length:
                print(f">> Error \"{name}\" does not contain same scaling parameters as {key}")
                return False
        return True         
 
    
    def set_output_type(self, out_type: type[OutType]):
        self.out_type = out_type       

    
    def add_static_parameter(self, key: str, value):
        print(f">> Succesfully added \"{key}\"")
        self.static_params.update({key : value})
        
    def add_scaling_parameter(self, name: str, new_param: dict):
        if not self.__is_valid_scaling_parameter(name, new_param):
            return
        print(f">> Succesfully added \"{name}\"")
        self.scaling_params.update({name : new_param})
        if self.scale_variables is None:
            self.scale_variables = self.__get_scale_variables_from_dict(new_param)

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
    
    def get_static_parameter(self, key) -> Any:
        return self.static_params[key]
 
               
    def get_scaling_parameter(self, key) -> dict:
        return self.scaling_params[key]
    
            
    def __write_formated(self, L, delim: str=':', rounding=3):          
        with self.param_paths[L].open("w") as file:
            for name in self.scale_variable_names:
                file.write(f"{name}{delim} {L}\n")
            self.__write_static(file, delim, rounding)
            self.__write_scaling(file, L, delim, rounding)
            file.write(f"outputfile{delim} {self.out_paths[L]}")
            
    def __write_scaling(self, file: TextIOWrapper, L, delim: str, rounding: int):
         for key in self.scaling_params:
            param_value = self.get_scaling_parameter(key)[L]
            
            if isinstance(param_value, np.ndarray):
                param_value = array_to_str(param_value, rounding)
            file.write(f"{key}{delim} {param_value}\n")
            
    def __write_static(self, file: TextIOWrapper, delim: str, rounding: int):
        for key in self.static_params:
            param = self.get_static_parameter(key)
            if isinstance(param, np.ndarray):
                param = array_to_str(param, rounding)
            file.write(f"{key}{delim} {param}\n")
 
    
    def write_parameter_file(self, L: int, delim: str=':', rounding=3) -> bool:
        if not self.paths_are_set:
            print("Parameter & output files not set!")
            return False
        
        try:
            self.__write_formated(L, delim, rounding)
            print(f"-- \"{self._log_path(self.param_paths[L])}\": ", end="")          
            return True
        except Exception as e:
            print(f"write_parameter_file error: {e}, {e.args}")
            return False
            
    def write_parameter_files(self, delim: str=':', rounding=3):
        if not self.paths_are_set:
            print("Parameter & output files not set!")
            return
        
        if self.scale_variables is None:
            raise ValueError("writing parameter Error: scale_variables not set!")
        
        print(f">> writing parameter files:")
        for L in self.scale_variables:
            try:
                if self.write_parameter_file(L, delim, rounding):
                    print("done")
            except Exception as e:
                print(f"write_parameter_files Error: {e}, {e.args}")
 
    
    def are_parameter_files_available(self) -> bool:
        if not self.paths_are_set:
            print(">> Parameter & output files not set!")
            return False
        
        has_all_files = True
        missing_files: list[Path] = []
        print(">> Looking for parameter files:")
        if self.scale_variables is None:
            print(f"* No scale_variables set")
            return False
        
        for L in self.scale_variables:
            param_path = self.param_paths[L]
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
        return self.param_paths[L]
    
    def get_output(self, L):
        return self.out_paths[L]
    
    def has_output(self, L):
        return self.out_paths[L].exists()
    
    def are_results_available(self) -> bool:
        if self.scale_variables is None:
            print("* No scale variables found, cannot search results.")
            return False 
        
        all_available = True
        some_availabe = False
        missing_files = []
        print(">> Looking for output files:")
        for L in self.scale_variables:
            file = self.out_paths[L]  
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
        if self.scale_variables is None:
            raise ValueError("get_results() error: scale_variables not set!")
        
        if self.out_type is None:
            raise TypeError("get_results() error: output_type not set!")


        print("")
        has_results = False
        results: dict[int, OutType] = dict()
        
        for L in self.scale_variables:
            if self.has_output(L):
                print(f"Found output: \"{self._log_path(self.get_output(L))}")
                has_results = True
        if not has_results:
            return dict()
 
        for L in self.scale_variables:
            if self.has_output(L):
                results[L] = self.out_type(self.get_output(L))
                results[L].grab_files()
        return results 
