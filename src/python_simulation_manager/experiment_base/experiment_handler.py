from __future__ import annotations
import numpy as np
import os
from typing import Protocol
from .experiment_output import ExperimentOutput

def array_to_str(array: np.ndarray, rounding: int) -> list[str]:
    temps_str = []
    for val in array:
        temps_str.append(str(round(val,rounding)))
    return ", ".join(temps_str)


class ExperimentHandler(Protocol):
    
    def __init__(self, name: str, folder: str, lengths):
        self.name: str                  = name
        self.folder: str                = folder
        self.lengths: np.ndarray        = lengths
        self.param_files: dict          = dict()
        self.out_files: dict            = dict()
        self.__init_directory()
        self.__set_files()
    
    def write_formated(self, L, rounding=3):
        raise NotImplementedError()

    def missing_parameters(self) -> dict:
        raise NotImplementedError()
    
    def set_result_type(self, output_file: str) -> ExperimentOutput:
        raise NotImplementedError()
    
    def write_parameter_file(self, L: int, rounding = 3) -> None:
        if len(self.missing_parameters()):
            print(f">> Error Missing parameters: {self.missing_parameters()}")
            return False

        if self.param_files is None or self.out_files is None:
            print("Parameter & output files not set!")
        try:
            self.write_formated(L, rounding)
            print(f"-- {self.param_files[L]}: ", end="")
            return True
        except Exception as e:
            print(f"Error occured: {e}, {e.args}")
                
    def write_parameter_files(self, temp_rounding=3):
        print(f">> writing parameter files:")
        for L in self.lengths:
            try:
                if self.write_parameter_file(L, temp_rounding):
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
            with open(f"{self.folder}/{self.name}/parameter_{L}x{L}.txt", "r") as _:
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
            file = f"\"{self.folder}/{self.name}/parameter_{L}x{L}.txt\""
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
     
    def get_parameter_file(self, L):
        return self.param_files[L]
    
    def are_results_available(self):
        all_available = True
        some_availabe = False
        missing_files = []
        print(">> Looking for output files:")
        for L in self.lengths:
            file = f"\"{self.folder}/{self.name}/out_{L}x{L}.txt\""
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
            os.makedirs(f"{self.folder}/{self.name}")
            print(f">> Directory \"{self.folder}/{self.name}\" created")
        except FileExistsError:
            print(f">> Directory \"{self.folder}/{self.name}\" Found.")
        except OSError as e:
            print(f"Error creating directory: {e}")

    def has_output(self, L):
        try:
            with open(f"{self.folder}/{self.name}/out_{L}x{L}.txt", "r") as _:
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
                print(f"Found output: \"{self.folder}/{self.name}/out_{L}x{L}.txt")
                has_results = True
        if not has_results:
            return None
        
        for L in self.lengths:
            if self.has_output(L):
                results[L] = self.set_result_type(f"{self.folder}/{self.name}/out_{L}x{L}.txt")
                results[L].grab_files()

        return results 
