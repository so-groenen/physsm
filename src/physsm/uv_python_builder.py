from .experiment_data import BaseExperimentData
from .abstract_experiment import AbstractExperiment
from .abstract_experiment_builder import AbstractExperimentBuilder
from .runnner import IRunner
from .path_logger import PathLogger
from pathlib import Path
from typing import override
import subprocess


class UvRunner(IRunner):
    def __init__(self, py_file: Path):
        self.main_py = py_file
        
    
    @override
    def run(self, cwd: Path, args: Path, verbose_log: bool = False, my_env: None | dict = None):
        command = f"uv run {self.main_py} {args}"
        if verbose_log:
            print(f"Command: \"{command}\"")   
        else:
            print(f"Command: Executing \"{self.main_py.name}\" with \"{args.name}\"")   

        with subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1, text=True, stderr=subprocess.STDOUT, cwd=cwd, env=my_env) as stream:
            if stream.stdout is not None:
                for lines in stream.stdout:
                    print("uv: ", lines, end='')
        print("")


class PythonuvExperiment(AbstractExperiment):
    def __init__(self, exp_data: BaseExperimentData):
        super().__init__(exp_data)

    @override
    def run(self, scale: int | float, env_var: dict | None = None, verbose_log=False) -> None:
        if self.runner is None:
            raise TypeError("run_executable() error: Runner not set [use: set_executable]")
        
        if not isinstance(self.runner, UvRunner):
            raise TypeError("run_executable() error: Runner not set to BinaryRunner [use: set_executable]")
        try:
            param_path = self.get_parameter_path(scale)
        except KeyError as _:
            print(">> run_cargo: cannot find parameter")            
            return

        cwd  = self.paths_data.proj_dir
        args = param_path
        self.runner.run(cwd, args, verbose_log, env_var)        

class PythonuvExperimentBuilder(AbstractExperimentBuilder):
    def __init__(self, proj_dir: Path, results_dir: str, exp_name: str, verbose_log: bool = False):
        super().__init__(proj_dir, results_dir, exp_name, PathLogger(proj_dir, verbose_log))
        self.runner: UvRunner|None = None
        
    def set_executable(self, binary_path: Path):
        if not binary_path.exists():
            raise FileNotFoundError(f"set_executable(): Cannot find {binary_path}")
        self.runner = UvRunner(binary_path)
        print(f">> Python file path set to \"{self.log_path(binary_path)}\" [Current mode: uv Python mode]")
    
    @override
    def build(self, load_only = False) -> PythonuvExperiment:
        experiment        = self._make_base_experiment()
        experiment.runner = self.runner
        if experiment.runner is None and not load_only:
            raise TypeError("Python UvRunner not set!")
        
        return PythonuvExperiment(experiment)
    
if __name__ == "__main__":
    pass