## Small Monte Carlo Simulation Manager Interface written in Python. 
The goal of this small package is to handle 2D simulations written in low-level languages (C, C++, Rust) from a Python notebook interface, and perform numerical scaling experiments, that is, experiments with increasing system size "L".<br>
For now, executing Rust programm is built-in, but C/C++ is on the TODO list. 


## Goal of the package
The original goal of the package was to manage Monte Carlo simulations in Rust by passing parameters to Rust from Python, and grab the results:
```Python
thermalization_steps = {2: 1_000_000, 4: 500_000,  8: 100_000}
measure_steps        = {2: 1_000_000, 4: 500_000,  8: 100_000}
temperatures         = np.arange(0, 4, 0.1)
builder              = RustExperimentBuilder(name="ising_overview", folder="results", rust_dir="ising_rust")

experiment = builder.new_from_parameters(thermalization_steps, measure_steps, temperatures)
experiment.write_parameter_files()
```
Here the parameters of the form `parameters_LxL.txt` will be written in `ising_rust/results/ising_overview`, where the Rust programm could find them and be launched from a python notebook with

```Python
for L in experiment.get_lengths():
    experiment.perform_rust_computation(L)
```
The result of the calculation will then have the form `out_LxL.txt` and be saved in the same folder.
The results can then be gathered readily using

```Python
results = experiment.get_results()
```
for plotting & further analysis. See also: [2d_ising_in_rust](https://github.com/so-groenen/2d_ising_in_rust) for an example.<br>
TODO: Add also Swendsen-Wang Ising example. 

## Example usage
For the full example, please look at: 
``` 
example.ipynb
```
as well as the Rust code in `rust_example/src`.<br>
## Details of example.ipynb:
Let us assume we have a Rust program which will read a file and needs the following:
* A length called **Lx**
* An array called **my_array**
* A boolean called **my_boolean**
* A dictionnary **steps** which contains Monte Carlo steps for each length "Lx" <br>

The programm will simply **display** the parameters, and <b>compute</b> the following **add** = _Lx_ + _Lx_ and **multi**= _Lx_ * _Lx_.
The output file will be of the form:

``` 
Hello World form Lx = {Lx}
add, multi
``` 
and saved as `rust_example/test_results/test_experiment/out_LxL.txt`

#### The goal will be to
* write the parameters for _Lx = [2, 4, 8]_
* execute the programm for **each** of these values
* grab & print the output.

### Step 1) Defining the output class
First we need to import our base classes:
```Python
from python_simulation_manager.experiment_base.experiment_output import ExperimentOutput
```

We will create our <b>output</b> Class, which inhertis from `ExperimentOutput` base class. Here we simply need to outline
the layout of the Rust output file:

```Python
class MyTestOutput(ExperimentOutput):
    def __init__(self, file_name):
        super().__init__(file_name)
        self.hello_world     = None
        self.sums            = None
        self.multiplications = None

    @override
    def parse_output(self, line_number, lines):
        if line_number == 0:
            self.hello_world = lines
        else:
            slines = lines.split(", ")
            self.sums            = float(slines[0])
            self.multiplications = float(slines[1])

```

### Step 2) Defining the ExperimentHandler
Let us import the Handler:


Now we construct our Experiment Handler. It will derive from the `ExperimentHandler` base class. 
```Python
from python_simulation_manager.experiment_base.experiment_handler import ExperimentHandler
```
It only needs to now that the result will be of type `MyTestOutput`:
```Python
class MyTestExperiment(ExperimentHandler):

    @override
    def set_result_type(self, output_file) -> MyTestOutput:
        return MyTestOutput(output_file)
```
### Step 3) Defining the Builder

The builder's goal is to make our live easier: First it will need the default parameter for Handler, which are: the experiment name `name`, the folder where the experiment goes, `folder`, and the location of the Rust project, `rust_dir` dir.
The resulting parameters & Output will go to `rust_dir/folder/name`.<br>
Then in the builder method we want a _static_parameter_ (meaning, it does NOT depend on _L_), called `my_array` which is a numpy array,
another _static_parameter_ called `my_bool`. <br> 
Then, the "scaling parameters" `steps` will be a **dict[int, int]**, which mimicks the number of Monte Carlo steps for each length _L_.
Finally, we can name our scaling parameters "Lx" and "Ly", so that the Rust file can look both for _Lx_ & _Ly_.

```Python
class TestExperimentBuilder:
    def __init__(self, name: str, folder: str, rust_dir: str):
        self.name: str     = name
        self.folder: str   = folder
        self.rust_dir: str = rust_dir

    def build_experiment(self: str, my_array: np.array, my_bool: bool, steps: dict):
     
        new_exp = MyTestExperiment(self.name, self.folder, self.rust_dir)
        new_exp.add_static_parameter("my_array", my_array)
        new_exp.add_static_parameter("my_bool", my_bool)
        new_exp.add_scaling_parameter("steps", steps)
        new_exp.set_scaling_name(["Lx", "Ly"])
        return new_exp
```
### Step 4)  Using our example:
Now we can make use of our example. First we create our builder, which will save all the infos of the file structure:

```python
test_builder = TestExperimentBuilder(name="test_experiment", folder="test_results", rust_dir="rust_example")
```
Then we can construct our experiment and write the parameter fiels:
```Python
an_array          = np.arange(0, 10, 1)
a_boolean         = True
monte_carlo_steps = {
    2: 100,
    4: 1_000,
    8: 1_000_000
}
test_exp = test_builder.build_experiment(an_array, a_boolean, monte_carlo_steps) 
test_exp.write_parameter_files()
```
From the definition we gave of the builder method, the parameter files will be saved in `rust_example/test_results/test_experiment` & look like (for ex: `parameter_2x2.txt`):
```
Lx: 2
Ly: 2
my_array: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
my_bool: False
steps: 100
outputfile: test_results/test_experiment/out_2x2.txt
```

The Rust programm can then readily find them. We could then launch our experiments by performing
```python
for L in test_exp.get_lengths():
    test_exp.perform_rust_computation(L)
```
This will call `cargo run --release -- rust_example/test_results/test_experiment/...` under the hood.
Stdout in python:
```powershell
* From Rust:      Running `target\release\rust_example.exe test_results/test_experiment/parameter_2x2.txt`
 * From Rust: Reading parameters:
 * From Rust: Lx: 2
 * From Rust: Ly: 2
 * From Rust: my_array: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
 * From Rust: my_bool: False
 * From Rust: steps: 100
 * From Rust: outputfile: test_results/test_experiment/out_2x2.txt
* From Rust: Writing in test_results/test_experiment/out_2x2.txt
```
And similarly for 4x4 etc... <br>
Then, finally
```python
results = test_exp.get_results()

for (Lx, result) in results.items():
    print(f"For Lx = {Lx} we have:")
    print(result.hello_world)
    print(f"Sum            = {result.sum}")
    print(f"multiplication = {result.multiplication}")
```
Will generate:
```
Found output: "rust_example/test_results/test_experiment/out_2x2.txt
Found output: "rust_example/test_results/test_experiment/out_4x4.txt
Found output: "rust_example/test_results/test_experiment/out_8x8.txt
For Lx = 2 we have:
Hello world! [Lx=2]
Sum            = 4.0
multiplication = 4.0
For Lx = 4 we have:
Hello world! [Lx=4]
Sum            = 8.0
multiplication = 16.0
For Lx = 8 we have:
Hello world! [Lx=8]
Sum            = 16.0
multiplication = 64.0
```
 