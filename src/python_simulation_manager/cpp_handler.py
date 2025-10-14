from .experiment_data import ExperimentData
from .abstract_experiment import AbstractExperiment
from .abstract_experiment_builder import AbstractExperimentBuilder
from .runnner import BinaryRunner
from pathlib import Path
from typing import override


class CppExperiment(AbstractExperiment):
    def __init__(self, exp_data: ExperimentData):
        self.copy_data(exp_data)
    
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
    
    @override
    def run(self, scale: int | float, env_var: dict | None = None, verbose=False) -> None:
        self.run_executable(scale, env_var, verbose)
        

class CppExperimentBuilder(AbstractExperimentBuilder):
    def __init__(self, proj_dir: Path, results_dir: str, exp_name: str, verbose_log: bool = False):
        super().__init__(proj_dir, results_dir, exp_name, verbose_log)
        
    def set_executable(self, binary_path: Path):
        self.experiment.runner = BinaryRunner(binary_path)
        print(f">> Binary path set to \"{self._log_path(binary_path)}\" [Current mode: Binary mode]")
    
    @override
    def build(self, load_only = False) -> CppExperiment:
        self._set_files()
        if self.experiment.runner is None and not load_only:
            raise TypeError("Binary path not set!")
        return CppExperiment(self.experiment)
    
if __name__ == "__main__":
    pass