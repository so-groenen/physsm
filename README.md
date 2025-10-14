# Physsm: A crossplatform Physics Simulation Manager written in Python. 
### WORK IN PROGRESS

The goal of this small package is to handle simulations written in **low-level languages** (C, C++, Fortran, Rust) from a **Python notebook interface**:
<br>
We define the outline of the output file, write the parameters in Python, set the executable path of the C/C++/Fortran programm (or Rust Cargo.toml path), run the simulations and grab the results!<br> 


The package uses pathlib for crossplatform path handling & uv for packaging.<br>
## Tested for:
* [C++: DMRG simulation of 1D Heisenberg chain](https://github.com/so-groenen/DMRG_Antiferro_S-1_Heisenberg_chain)
* [Rust: 2D Ising Metropolis](https://github.com/so-groenen/2d_ising_in_rust)
* [Rust: 2D Ising Swendsen-Wang cluster algorithm](https://github.com/so-groenen/swendsen_wang_ising_rust)
<!-- * [C++: DMRG simulation of 1D Heisenberg chain](https://github.com/so-groenen/DMRG_Antiferro_S-1_Heisenberg_chain) -->

## Example for a C++ Monte-Carlo experiment

Assume we have a C++ Monte-Carlo progrmam `main.exe` which:
* reads a file containing a range of *temperatures*, system-size length **Lx**, that
* For each length **Lx**, compute the **energy** and **magnetization** and write it in a file.
* is **executed 3 times**, once for lengths **Lx** $=2,4,8$, each time with different **Monte-Carlo steps**.

<br> This can be achieved by first defining the outline of the outputfile so that the manager knows how to grab the results. This is done by inheriting from `ExperimentOutput` and implementing the `parse_output` method:

```Python
from physsm.experiment_output import ExperimentOutput

class MyOutput(ExperimentOutput):
    def __init__(self, out_path):
        super().__init__(out_path)
        self.energy        = []
        self.magnetization = []

    @override
    def parse_output(self, line_number, line):
        e, m = line.split(",")
        self.energy.append(float(e))
        self.magnetization.append(float(m))
```
The manager distinguishes between:
* *scale_variable*: the variable which varies for different run of an experiment (for ex: *system size* $L$ in a Monte-Carlo experiment)
* *static_parameters*: the parameters kept constant for exach run (for ex: *temperatures*, *external magnetic field*...)
* *scaling_parameters*: parameters which depend on the scale variable and differ from one programm run to another (for ex: number of *monte-carlo steps*)
We can define/add the needed parameters using the `CppExperimentBuilder`:

```python
from pathlib import Path
from physsm.cpp_builder import CppExperimentBuilder

thermalization_steps = {2: 1_000_000, 4: 500_000,  8: 100_000}
measure_steps        = {2: 1_000_000, 4: 500_000,  8: 100_000}
temperatures         = np.arange(0, 5, 0.5)
project_dir          = Path.cwd()  #current working directory
executable           = project_dir / "build" / "main.exe"
builder              = CppExperimentBuilder(project_dir, results_dir="results", exp_name="overview")

builder.set_output_type(MyOutput)
builder.set_scale_variable_names(["Lx"])
builder.add_static_parameter("temperatures", temperatures)
builder.add_scaling_parameter("thermalization_steps", thermalization_steps)
builder.add_scaling_parameter("measure_steps", measure_steps)
builder.set_executable(executable)

experiment = builder.build()
```
Here, the scale variables $L_x$ will be inferred from the dictionnaries.
Then we write the files
```python
experiment.write_parameter_files(delim =':', rounding = 3)
```
will output
```
>> writing parameter files:
-- "results/overview/parameter_Lx=2.txt": done
-- "results/overview/parameter_Lx=4.txt": done
-- "results/overview/parameter_Lx=8.txt": done
``` 
and the files will have the form
```
Lx: 2
temperature: 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5
thermalization_steps: 1000000
measure_steps: 1000000
outputfile: path/to/project_dir/results/overview/out_Lx=2.txt
```
Here the default "rounding=3" is used to round np.ndarray to string of numbers.
We can then execute the `main.exe` executable:

```Python
for L in experiment.get_scale_variables():
    experiment.run(L)
```
Here the parameter files are passed as arg-variables, and the `run method` simply executes `path/to/main.exe path/to/parameter_Lx=2.txt` in the project directory. The results of the calculation will then have the form `results/overview/out=8.txt` and be saved in the same folder.
They can be loaded readily, in form of dictionnary "MyOutput" type using

```Python
results = experiment.get_results()
```
for plotting & further analysis or plotting. For example:
```Python
import matplotlib.pyplot as plt

for (Lx, result) in results.items():
    plt.plot(temperatures, result.energy)
    plt.plot(temperatures, result.magnetization)

```
See the [provided example](examples/sim_managers/c_manager.ipynb) or a concrete case of the [2D Ising model](https://github.com/so-groenen/2d_ising_in_rust/blob/main/calculation_manager/ising_run_and_plot.ipynb).

## Rust example
For the Rust example we simply use the `RustExperimentBuilder` and `set_cargo_toml_path` method:
```Python
from physsm.rust_builder import RustExperiment, RustExperimentBuilder

thermalization_steps = {2: 1_000_000, 4: 500_000,  8: 100_000}
measure_steps        = {2: 1_000_000, 4: 500_000,  8: 100_000}
temperatures         = np.arange(0, 5, 0.5)
project_dir          = Path().cwd()   
cargo_path           = project_dir / "rust_project" / "Cargo.toml"
builder              = RustExperimentBuilder(project_dir, results_dir="results", exp_name="overview")

builder.set_scale_variable_names(["Lx"])
builder.add_static_parameter("temperatures", temperatures)
builder.add_scaling_parameter("thermalization_steps", thermalization_steps)
builder.add_scaling_parameter("measure_steps", measure_steps)
builder.set_cargo_toml_path(cargo_path)
experiment = builder.build()
experiment.write_parameter_files()
```
The run method will then call `cargo run --manifest-path {cargo_toml_path} --release -- {args}`

# Installing the package:

Add to your Python uv project:
```
uv add "python_simulation_manager @ git+https://github.com/so-groenen/python_simulation_manager"
```
Install the package to your uv virtual environnement:
```
uv pip install "git+https://github.com/so-groenen/python_simulation_manager"
```
<br>
More on managing dependencies with uv:

[https://docs.astral.sh/uv/pip/packages](https://docs.astral.sh/uv/pip/packages/)  <br>
[https://docs.astral.sh/uv/concepts/projects/dependencies/](https://docs.astral.sh/uv/concepts/projects/dependencies/)  <br>
If you are not familiar: [docs.astral.sh/uv/](https://docs.astral.sh/uv/)

## Example usage
The package contains a C and Rust example, with two small programms which read files containing a "length" variable, "temperatures" static parameters,
"monte_carlo_trials" scaling parameters and the outputfile variable, to store the results. The C & Rust programm will simply read the files
and output `monte_carlo_trials + 0.42` & `lenght + 0.42`.<br>
First download the package using (in bash or powershell):
```
git clone https://github.com/so-groenen/python_simulation_manager
cd python_simulation_manager
```
And initlize the python virtual environnement using `uv init`.
### C/C++
Change directory `cd examples/c_example`.<br>
You can compile the the small C programm in `src/main.c` using the small python script `uv run make.py`, which will compile it using clang & put the binary into `build/c_example.exe`.<br>

Run then all the scripts in [examples/sim_managers/c_manager.ipynb](examples/sim_managers/c_manager.ipynb).<br>
In these scripts we encapsulate the building steps in a "Factory" class, so as to avoid having to redo the steps everytime.
### Rust
From the `python_simulation_manager` dir, change directory `cd examples/rust_example`.<br>

Run then all the scripts in [examples/sim_managers/rust_manager.ipynb](examples/sim_managers/rust_manager.ipynb).<br>

## Customization
The package uses some default options:
```
experiment.write_parameter_files(delim =':', rounding=3)
```
where rounding is used to map *np.ndarray* to strings.
Similarly, we can set the outputfile key, file_name and extension:
```
builder.set_output_file_data(key="outputfile", filename="out", extension="txt")
```
as well as for the parameter file
```
builder.set_parameter_file_data(filename="parameter", extension="txt")   
```
By default, the terminal displays relative paths, we can display absolute paths by using the "verbose" option:
```
builder = CppExperimentBuilder(project_dir, results_dir="results", exp_name="overview", verbose_log=True)
```

## Environnement variables
When running a simulation, one often needs to use environnement variables (for ex: number of threads). This is achieved as follows:
```
import os
env_var = os.environ.copy()
env_var["OMP_NUM_THREADS "] = "4"

for L in experiment.get_scale_variables():
    experiment.run(L, verbose_log=True, env_var=env_var)
```
Note, we used the "verbose=True", which full path"