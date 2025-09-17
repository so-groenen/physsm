import numpy as np
from .experiment_base.experiment_handler import array_to_str, ExperimentHandler
from .experiment_base.experiment_output import ExperimentOutput
from typing import override
import subprocess

def get_length_from_dicts(therm_steps: dict, measure_steps: dict):
    lengths = []
    for (L1, L2) in zip(therm_steps.keys(), measure_steps.keys()):
        if L1 != L2:
            return None
        lengths.append(L1)
    return lengths

class MonteCarloData(ExperimentOutput):
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
        else:
            slines = lines.split(", ")
            self.temperatures.append(float(slines[0]))
            self.energy_density.append(float(slines[1]))
            self.magnetisation.append(float(slines[2]))
            self.specific_heat.append(float(slines[3]))
            self.mag_susceptibility.append(float(slines[4]))
            self.correlation_length.append(float(slines[5]))
            
            
            
            
class MonteCarloExperiment(ExperimentHandler):
    def __init__(self, name, folder, lengths):
        
        super().__init__(name, folder, lengths)
        self.therm_steps   = None
        self.measure_steps = None
        self.temperatures  = None
        self.measure_correlation_length = False
        
    @override
    def set_result_type(self, output_file) -> ExperimentOutput:
        return MonteCarloData(output_file)
    
    @override
    def missing_parameters(self) -> list: 
        missing = []
        for (key, val) in vars(self).items():
            if val is None:
                missing.append(key)
        return missing

    @override
    def write_formated(self, L, rounding=3):
        with open(self.get_parameter_file(L), "w") as f:
            f.write(f"rows: {L}\n")
            f.write(f"cols: {L}\n")
            f.write(f"therm_steps: {self.therm_steps[L]}\n")
            f.write(f"measure_steps: {self.measure_steps[L]}\n")
            f.write(f"temperatures: {array_to_str(self.temperatures, rounding)}\n")
            f.write(f"measure_struct_fact: {self.measure_correlation_length}\n")
            f.write(f"outputfile: {self.out_files[L]}\n")

    @override
    def run(self, L):
        command  = f"cargo run --release -- {self.get_parameter_file(L)}"
        print(f"Command: \"{command}\"")   
        with subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1, text=True, stderr=subprocess.STDOUT) as stream:
            for line in stream.stdout:
                if line.__contains__("Time taken: "):
                    time_str = line.split("Time taken: ")[1]
                    # time     = int(time_str.removesuffix("s\n"))
                print(f" * From Rust: {line}", end='') 
    
    def set_struct_fact_measure(self, val: bool):
        self.measure_correlation_length = val
        
    def set_parameters(self, therm_steps: dict, measure_steps: dict):
        param_lengths = get_length_from_dicts(therm_steps, measure_steps)
        if param_lengths is None:
            print(">> therm steps & measure steps should use same lengths")
        if param_lengths != self.lengths:
            print(">> Monte carlo parameter lengths do not match original lengths!")
        else:
            self.measure_steps = measure_steps
            self.therm_steps   = therm_steps
        print(">> Monte Carlo parameters set!")
    
    def set_temperatures(self, temps: np.ndarray):
        if isinstance(temps, np.ndarray):
            print(">> Temperatures set!")
            self.temperatures = temps
        else:
            print(">> Temperatures not numpy array!")
    
    @staticmethod
    def new_from_parameters(name: str, folder: str, therm_steps: dict, measure_steps: dict, temperatures: np.ndarray):
        lengths = []
        for (L, _) in zip(therm_steps.keys(), measure_steps.keys()):
            lengths.append(L)
                    
        new_exp = MonteCarloExperiment(name, folder, lengths)
        new_exp.set_parameters(therm_steps, measure_steps)
        new_exp.set_temperatures(temperatures)
        return new_exp
        
if __name__ == "__main":
    
    None
