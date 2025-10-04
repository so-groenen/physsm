from __future__ import annotations
import numpy as np
from typing import Protocol
from .output import ExperimentOutput
from .runnner import*
from pathlib import Path
from io import TextIOWrapper


def array_to_str(array: np.ndarray, rounding: int) -> list[str]:
    temps_str = []
    for val in array:
        temps_str.append(str(round(val, rounding)))
    return ", ".join(temps_str)
 
class ExperimentHandler(Protocol):
    
    def __init__(self, proj_dir: Path, exp_dir_name: str, results_dir_name: str, verbose_log:bool = False):
        self.verbose_log: bool                  = verbose_log
        if self.verbose_log:
            print(">> verbose log is On: All paths shown are Absolute]")
        
        self.proj_dir: Path                     = proj_dir
        self.target_dir: Path                   = None
        self.out_paths:   dict[int|float, Path] = dict()
        self.param_paths: dict[int|float, Path] = dict()
        self.__set_target_dir(results_dir_name, exp_dir_name)

        self.scale_variables: np.ndarray|list          = None
        self.scale_variable_names: list[str]           = ["L"]

        self.static_params: dict[str, any]             = dict()
        self.scaling_params: dict[str, dict[int, any]] = dict()

        self.out_type: type[ExperimentOutput] = None
        self.runner: IRunner                  = None
    
    def _log_path(self, path: Path) -> Path:
        if not self.verbose_log:
            return path.relative_to(self.proj_dir)
        return path
        
    def __set_target_dir(self, results_dir_name: str, exp_dir_name: str):
        _results_dir    = self.proj_dir.joinpath(results_dir_name)
        self.target_dir = _results_dir.joinpath(exp_dir_name)
        
        if self.target_dir.exists():
            print(f">> Directory \"{self._log_path(self.target_dir)}\" Found.")
        else:
            self.target_dir.mkdir(parents=True)
            print(f">> Directory \"{self._log_path(self.target_dir)}\" created.")

    def set_files(self):
        print(">> Setting file paths:")
        if self.scale_variables is None:
            return        
        
        prefix = dict()
        for L in self.scale_variables:
            prefix[L] = ",".join([f"{scale_name}={L}" for scale_name in self.scale_variable_names])

        for L in self.scale_variables:
            self.param_paths[L] = self.target_dir.joinpath(f"parameter_{prefix[L]}.txt")
            print(f"-- setting paramfile \"{self._log_path(self.param_paths[L])}\"")
            
        for L in self.scale_variables:           
            self.out_paths[L] = self.target_dir.joinpath(f"out_{prefix[L]}.txt")
            print(f"-- setting outfile \"{self._log_path(self.out_paths[L])}\"")
    

    def get_scale_variables(self) -> list[int|float]:
        return self.scale_variables

    def set_scale_variables(self, variables: list|np.ndarray):
        self.scale_variables = variables
        
    def set_scale_variable_names(self, names: list[str]):
        self.scale_variable_names = names
        # if self.scale_variables is not None:
        #     self.set_files()
        
    def set_executable(self, binary_path: Path):
        self.runner = BinaryRunner(binary_path)
        print(f">> Binary path set to \"{self._log_path(binary_path)}\" [Current mode: Binary mode]")
        
    def set_cargo_toml_path(self, cargo_toml_path: Path):
        self.runner = CargoRunner(cargo_toml_path)
        print(f">> Cargo toml path set to \"{self._log_path(cargo_toml_path)}\" [Current mode: Cargo mode]")

    def __get_scale_variables_from_dict(self, scaling_param: dict[int|float, any]):
        scale_variables = []
        for L in scaling_param.keys():
            scale_variables.append(L)
        scale_variables.sort()
        return scale_variables
    
    def run_executable(self, scale: int|float, env_var:dict = None, verbose = False):
        if not isinstance(self.runner, BinaryRunner):
            raise TypeError("ERROR: Runner not set to BinaryRunner [use: set_executable]")
        try:
            param_path = self.get_parameter_path(scale)
        except KeyError as _:
            print(">> run_cargo: cannot find parameter")            
            return

        cwd  = self.proj_dir
        args = param_path
        self.runner.run(cwd, args, verbose, env_var)

    def run_cargo(self, scale: int|float, env_var:dict = None, verbose:bool = False):
        if not isinstance(self.runner, CargoRunner):
            raise TypeError("ERROR: Runner not set to CargoRunner [use: set_cargo_toml_path]")
        try:
            param_path = self.get_parameter_path(scale)
        except KeyError as _:
            print(">> run_cargo: cannot find parameter")            
            return
              
        cwd  = self.proj_dir
        args = param_path
        self.runner.run(cwd, args, verbose, env_var)

    
    def __is_valid_scaling_parameter(self, name: str, new_scaling_param: dict[int, any]) -> bool:
        
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
    
    def set_result_type(self, output_file: str) -> ExperimentOutput:
        raise NotImplementedError()
    
    def set_output_type(self, out_type: type[ExperimentOutput]):
        self.out_type = out_type       
     
    
    def add_static_parameter(self, key: str, value):
        print(f">> Succesfully added \"{key}\"")
        self.static_params.update({key : value})
        
    def add_scaling_parameter(self, name: str, new_param: dict[int|float, any]):
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
    
    def get_static_parameter(self, key):
        try:
            return self.static_params[key]
        except KeyError as _:
            print(f">> Key \"{key}\" not found")
            

    
    def get_scaling_parameter(self, key) -> dict[int, any]:
        try:
            return self.scaling_params[key]
        except KeyError as _:
            print(f">> Key {key} not found")

            
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
 
    
    def write_parameter_file(self, L: int, delim: str=':', rounding=3) -> None:
        if self.param_paths is None or self.out_paths is None:
            print("Parameter & output files not set!")
        try:
            self.__write_formated(L, delim, rounding)
            print(f"-- \"{self._log_path(self.param_paths[L])}\": ", end="")          
            return True
        except Exception as e:
            print(f"Error occured: {e}, {e.args}")
                
    def write_parameter_files(self, delim: str=':', rounding=3):
        print(f">> writing parameter files:")
        for L in self.scale_variables:
            try:
                if self.write_parameter_file(L, delim, rounding):
                    print("done")
            except Exception as e:
                print(f"Error occured: {e}, {e.args}")
 
    
    def are_parameter_files_available(self) -> bool:
        has_all_files = True
        missing_files = []
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
                print(f"-- not written yet: {files}")
        return has_all_files
     
    def get_parameter_path(self, L):
        return self.param_paths[L]
    
    def get_output(self, L):
        return self.out_paths[L]
    
    def has_output(self, L):
        return self.out_paths[L].exists()
    
    def are_results_available(self):
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
            for files in missing_files:
                print(f"-- {files}")
        if not some_availabe:
            print("* No output files created yet.")
            
        return some_availabe


    def get_results(self) -> dict[int, ExperimentOutput]: 
        print("")
        has_results = False
        results: dict[int, ExperimentOutput] = dict()

        for L in self.scale_variables:
            if self.has_output(L):
                print(f"Found output: \"{self.get_output(L)}")
                has_results = True
        if not has_results:
            return None
        
        if self.out_type is None:
            raise TypeError("ERROR: ExperimentOutput type not set.\n")
        
        for L in self.scale_variables:
            if self.has_output(L):
                results[L] = self.out_type(self.get_output(L))
                results[L].grab_files()

        return results 
