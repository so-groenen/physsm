import numpy as np
from .handler import ExperimentHandler
from .output import ExperimentOutput
from typing import override
import subprocess

class IsingData(ExperimentOutput):
    def __init__(self, file_name):
        super().__init__(file_name)

        self.temperatures       = []
        self.energy_density     = []
        self.magnetisation      = []
        self.specific_heat      = []
        self.mag_susceptibility = []
        self.elapsed_time       = -1
        self.correlation_length = []

    @override
    def parse_output(self, line_number, lines):
        if line_number == 0:
            slines = lines.split(':')
            try:
                self.observables  = slines[0].split(', ')
                self.elapsed_time = float(slines[1])
            except Exception as _:
                self.observables = lines.split(',')
                print("No elasped time found.")
            return
        
        slines = lines.split(", ")
        self.temperatures.append(float(slines[0]))
        self.energy_density.append(float(slines[1]))
        self.magnetisation.append(float(slines[2]))
        self.specific_heat.append(float(slines[3]))
        self.mag_susceptibility.append(float(slines[4]))
        self.correlation_length.append(float(slines[5]))
                       
class RustIsingExperiment(ExperimentHandler):
    
    def get_lengths(self) -> list[int]:
        return self.get_scale_variables()
    
class RustIsingExperimentBuilder:
    def __init__(self, name: str, folder: str, rust_dir: str):
        self.name: str     = name
        self.folder: str   = folder
        self.rust_dir: str = rust_dir

    def new_from_parameters(self, therm_steps: dict, measure_steps: dict, temperatures: np.ndarray, measure_struct_fact: bool = False) -> RustIsingExperiment:
     
        new_exp = RustIsingExperiment(self.name, self.folder, self.rust_dir)
        new_exp.set_output_type(IsingData)
        new_exp.set_scale_variable_names(["Lx", "Ly"])        
        
        new_exp.add_static_parameter("temperatures", temperatures)
        new_exp.add_static_parameter("measure_struct_fact", measure_struct_fact)
        
        new_exp.add_scaling_parameter("therm_steps", therm_steps)
        new_exp.add_scaling_parameter("measure_steps", measure_steps)
        new_exp.set_files()
        return new_exp
    
    def load(self, lengths: list[int]) -> RustIsingExperiment:
        new_exp = RustIsingExperiment(self.name, self.folder, self.rust_dir, lengths)
        new_exp.set_output_type(IsingData)
        new_exp.set_scale_variable_names(["Lx", "Ly"])        
        new_exp.set_files()
        return new_exp

    
    
if __name__ == "__main":
    None
