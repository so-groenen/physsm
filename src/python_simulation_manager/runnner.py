from __future__ import annotations
from typing import override
import subprocess
from pathlib import Path

class IRunner:
    def run(self, cwd: Path, args: Path, verbose_log: bool = False, my_env: None | dict = None):
        raise NotImplementedError()

class CargoRunner(IRunner):
    def __init__(self, cargo_toml_path: Path):
        self.cargo_toml_path = cargo_toml_path
        
    @override
    def run(self, cwd: Path, args: Path,  verbose_log: bool = False, my_env: None | dict = None):
        cargo_toml_path = self.cargo_toml_path 
        command = f"cargo run --manifest-path {cargo_toml_path} --release -- {args}"

        if verbose_log:
            print(f"Command: \"{command}\"")   
        else:
            print(f"Running cargo --release with from rust dir \"{cargo_toml_path.parent.relative_to(cwd)}\" and args=\"{args.name}\"")   

        
        with subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1, text=True, stderr=subprocess.STDOUT, cwd=cwd, env=my_env) as stream:
            for lines in stream.stdout:
                print("Rust: ", lines, end='')

class BinaryRunner(IRunner):
    def __init__(self, binary_path: Path):
        self.binary = binary_path

    @override
    def run(self, cwd: Path, args: Path, verbose_log: bool = False, my_env: None | dict = None):
        command = f"{self.binary} {args}"
        if verbose_log:
            print(f"Command: \"{command}\"")   
        else:
            print(f"Command: Executing \"{self.binary.name}\" with \"{args.name}\"")   

        with subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1, text=True, stderr=subprocess.STDOUT, cwd=cwd, env=my_env) as stream:
            for lines in stream.stdout:
                print("C/C++: ", lines, end='')
        print("")
        
if __name__ == "__main__":
    print("")