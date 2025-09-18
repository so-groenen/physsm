from __future__ import annotations
import numpy as np
import os
from typing import Protocol
from .experiment_output import ExperimentOutput
import subprocess

def array_to_str(array: np.ndarray, rounding: int) -> list[str]:
    temps_str = []
    for val in array:
        temps_str.append(str(round(val,rounding)))
    return ", ".join(temps_str)

class ExperimentHandler(Protocol):
    
    def __init__(self, name: str, folder: str, rust_proj_dir: str, lengths=None):
        self.name: str                  = name
        self.folder: str                = folder
        self.lengths: np.ndarray        = lengths
        self.rust_proj_dir: str         = rust_proj_dir
        self.param_files: dict          = dict()
        self.out_files: dict            = dict()
        self.static_params: dict        = dict()
        self.scaling_params: dict[str, dict[int, any]] = dict()
        self.path                       = f"{self.rust_proj_dir}/{self.folder}/{self.name}"
        self.scaling_names              = ["rows", "cols"]
        self.__init_directory()

    def get_lengths(self) -> int:
        return self.lengths

    def set_scaling_name(self, names: list[str]):
        self.scaling_names = names
    
    def __get_lengths_from_dict(self, scaling_param: dict[int, any]):
        length = []
        for L in scaling_param.keys():
            length.append(L)
        length.sort()
        return length
    
    def _is_valid_scaling_parameter(self, name: str, new_scaling_param: dict[int, any]) -> bool:
        
        if len(self.scaling_params) == 0:
            return True
        
        new_length = []
        for L in new_scaling_param.keys():
            if not isinstance(L, int):
                print(f">> Error \"{name}\" contains non scaling key {L}")
                return False
            new_length.append(L)
            
        new_length.sort()
        for key, params in self.scaling_params.items():
            length = self.__get_lengths_from_dict(params)
            
            if new_length != length:
                print(f">> Error \"{name}\" does not contain same scaling parameters as {key}")
                return False
        return True         
    
    def set_result_type(self, output_file: str) -> ExperimentOutput:
        raise NotImplementedError()
    
    def add_static_parameter(self, key: str, value):
        print(f">> Succesfully added {key}")
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
    
    def get_static_parameter(self, key):
        try:
            return self.static_params[key]
        except KeyError as _:
            print(f">> Key \"{key}\" not found")
            
    def add_scaling_parameter(self, name: str, new_param: dict[int, any]):
        if not self._is_valid_scaling_parameter(name, new_param):
            return
        print(f">> Succesfully added {name}")
        self.scaling_params.update({name : new_param})
        if self.lengths is None:
            self.lengths = self.__get_lengths_from_dict(new_param)
            self.__set_files()
    
    def get_scaling_parameter(self, key) -> dict[int, any]:
        try:
            return self.scaling_params[key]
        except KeyError as _:
            print(f">> Key {key} not found")
    
    def get_rust_dir(self) -> str:
        return self.rust_proj_dir
    
    def __write_scaling(self, file, L, delim, rounding):
         for key in self.scaling_params:
            param = self.get_scaling_parameter(key)[L]
            if isinstance(param, np.ndarray):
                param = array_to_str(param, rounding)
            file.write(f"{key}{delim} {param}\n")
            
    def __write_static(self, file, delim, rounding):
        for key in self.static_params:
            param = self.get_static_parameter(key)
            if isinstance(param, np.ndarray):
                param = array_to_str(param, rounding)
            file.write(f"{key}{delim} {param}\n")
            
    
    def __write_formated(self, L, delim: str=':', rounding=3):
        with open(self.get_parameter_file(L), "w") as file:
            for name in self.scaling_names:
                file.write(f"{name}{delim} {L}\n")
            self.__write_static(file, delim, rounding)
            self.__write_scaling(file, L, delim, rounding)
            file.write(f"outputfile{delim} {self.out_files[L]}")
            
    def perform_rust_computation(self, L):
        command  = f"cargo run --release -- {self.get_parameter_file_relative(L)}"
        cwd      = self.get_rust_dir()
        print(f"Command: \"{command}\"")   
        with subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1, text=True, stderr=subprocess.STDOUT, cwd=cwd) as stream:
            for line in stream.stdout:
                print(f" * From Rust: {line}", end='') 
            # # for key in self.static_params:
                
            # #     param = self.get_static_parameter(key)
            # #     if isinstance(param, np.ndarray):
            # #         param = array_to_str(param, rounding)
            # #     param_file.write(f"{key}{delim} {param}\n")
            
            # for key in self.scaling_params:
                
            #     param = self.get_scaling_parameter(key)[L]
            #     if isinstance(param, np.ndarray):
            #         param = array_to_str(param, rounding)
            #     param_file.write(f"{key}{delim} {param}\n")
                
            # param_file.write(f"outputfile{delim} {self.out_files[L]}")
    
    def write_parameter_file(self, L: int, delim: str=':', rounding=3) -> None:
        if self.param_files is None or self.out_files is None:
            print("Parameter & output files not set!")
        try:
            self.__write_formated(L, delim, rounding)
            print(f"-- {self.param_files[L]}: ", end="")
            return True
        except Exception as e:
            print(f"Error occured: {e}, {e.args}")
                
    def write_parameter_files(self, delim: str=':', rounding=3):
        print(f">> writing parameter files:")
        for L in self.lengths:
            try:
                if self.write_parameter_file(L, delim, rounding):
                    print("done")
            except Exception as e:
                print(f"Error occured: {e}, {e.args}")
                
    def __set_files(self):
        print(">> Setting file paths:")
        if self.lengths is None:
            print(">> Set Files: Error: No lengths found!")
            return

        for L in self.lengths:
            self.param_files[L] = f"{self.folder}/{self.name}/parameter_{L}x{L}.txt"
            print(f"-- setting paramfile \"{self.param_files[L]}\"")
        for L in self.lengths:
            self.out_files[L]   = f"{self.folder}/{self.name}/out_{L}x{L}.txt"
            print(f"-- setting outfile \"{self.out_files[L]}\"")
    
    
    def has_param_file(self, L: int) -> bool:
        try:
            with open(self.get_parameter_file(L), "r") as _:
                pass
            return True
        except FileNotFoundError as _:
            return False
    
    def are_parameter_files_available(self) -> bool:
        has_all_files = True
        missing_files = []
        print(">> Looking for parameter files:")
        if self.lengths is None:
            print(f"* No lengths set")
            return False
        
        for L in self.lengths:
            file = self.get_parameter_file(L)
            if self.has_param_file(L):
                print(f"-- Found parameter file: {file}")
            else:
                missing_files.append(file)
                has_all_files = False
                
        if has_all_files:
            print("* Parameter files available")
        else:
            print("* Not all parameter files created yet:")    
            for files in missing_files:
                print(f"-- not written yet: {files}")
        return has_all_files
     
    def get_parameter_file_relative(self, L):
        return self.param_files[L]
    
    def get_parameter_file(self, L):
        return self.rust_proj_dir + "/" + self.param_files[L]

    def get_output(self, L):
        return self.rust_proj_dir + "/" + self.out_files[L]
    
    
    def are_results_available(self):
        all_available = True
        some_availabe = False
        missing_files = []
        print(">> Looking for output files:")
        for L in self.lengths:
            file = f"\"{self.path}/out_{L}x{L}.txt\""
            if self.has_output(L):
                print(f"-- Found output: {file}")
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
        
    def __init_directory(self):
        try:
            os.makedirs(f"{self.path}")
            print(f">> Directory \"{self.path}\" created")
        except FileExistsError:
            print(f">> Directory \"{self.path}\" Found.")
        except OSError as e:
            print(f"Error creating directory: {e}")

    def has_output(self, L):
        try:
            with open(self.get_output(L), "r") as _:
                pass
            return True
        except FileNotFoundError as e:
            return False
    

    def get_results(self) -> dict[int, ExperimentOutput]: #tuple[np.ndarray, dict[int, MonteCarloData]]:
        print("")
        has_results = False
        results: dict[int, ExperimentOutput] = dict()

        for L in self.lengths:
            if self.has_output(L):
                print(f"Found output: \"{self.get_output(L)}")
                has_results = True
        if not has_results:
            return None
        
        for L in self.lengths:
            if self.has_output(L):
                results[L] = self.set_result_type(self.get_output(L))
                results[L].grab_files()

        return results 
