from .experiment_data import ExperimentData
from .abstract_experiment import AbstractExperiment
from .abstract_experiment_builder import AbstractExperimentBuilder
from .output import ExperimentOutput
from .runnner import CargoRunner
from pathlib import Path
from typing import Type, override, TypeVar

OutType = TypeVar("OutType", bound = ExperimentOutput) 

class RustExperiment(AbstractExperiment[OutType]):
    def __init__(self, exp_data: ExperimentData):
        super().__init__()
        self.copy_data(exp_data)
        
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
        
    @override
    def run(self, scale: int | float, env_var: dict | None = None, verbose=False) -> None:
        self.run_cargo(scale, env_var, verbose)

class RustExperimentBuilder(AbstractExperimentBuilder[OutType]):
    def __init__(self, proj_dir: Path, exp_dir_name: str, results_dir_name: str, verbose_log:  bool = False):
        super().__init__(proj_dir, exp_dir_name, results_dir_name, verbose_log)
        
    def set_cargo_toml_path(self, cargo_toml_path: Path):
        self.experiment.runner = CargoRunner(cargo_toml_path)
        print(f">> Cargo toml path set to \"{self._log_path(cargo_toml_path)}\" [Current mode: Cargo mode]")

    @override
    def build(self, load_only = False) -> RustExperiment:
        self._set_files()
        if self.experiment.runner is None and not load_only:
            raise TypeError("Cargo toml not set!")
        return RustExperiment(self.experiment)

if __name__ == "__main__":
    pass