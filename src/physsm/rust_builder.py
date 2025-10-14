from .experiment_data import BaseExperimentData
from .abstract_experiment import AbstractExperiment
from .abstract_experiment_builder import AbstractExperimentBuilder
from .experiment_output import ExperimentOutput
from .runnner import CargoRunner
from pathlib import Path
from typing import override, TypeVar

OutType = TypeVar("OutType", bound = ExperimentOutput) 

class RustExperiment(AbstractExperiment):
    def __init__(self, exp_data: BaseExperimentData):
        super().__init__()
        self.copy_data(exp_data)
        
    @override
    def run(self, scale: int | float, env_var: dict | None = None, verbose_log=False) -> None:
        if self.runner is None:
            raise TypeError("run_cargo() error: Runner not set [use: set_executable]")        
        
        if not isinstance(self.runner, CargoRunner):
            raise TypeError("run_cargo() error: : Runner not set to CargoRunner [use: set_cargo_toml_path]")
        try:
            param_path = self.get_parameter_path(scale)
        except KeyError as _:
            print(">> run_cargo: cannot find parameter")            
            return
              
        cwd  = self.paths_data.proj_dir
        args = param_path
        self.runner.run(cwd, args, verbose_log, env_var)
        
        
class RustExperimentBuilder(AbstractExperimentBuilder[OutType]):
    def __init__(self, proj_dir: Path, results_dir: str, exp_name: str, verbose_log: bool = False):
        super().__init__(proj_dir, results_dir, exp_name, verbose_log)
        
    def set_cargo_toml_path(self, cargo_toml_path: Path):
        if not cargo_toml_path.exists():
            raise FileNotFoundError(f"set_cargo_toml_path(): Cannot find {cargo_toml_path}")
        
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