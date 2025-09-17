## Small Monte Carlo Simulation Manager Interface written in Python. 
The goal is to handle 2D simulations (mostly on a square lattice) written in low-level languages (C, C++, Rust) from a Python notebook interface and perform experiment with increasing system sizes "L".<br>
Please have a look at 
``` 
example.ipynb
```
for an example for the 2D Ising model.
#### Example Usage (2D Ising model):
* Parameters (temperatures, external magnetic field, name of outputfile) can be set & written in a python notebook and then passed as a file (<b><i>"parameter_LxL.text"</b></i>) to Rust, C or C++.<br>
* By default the corresponding outputfile name will be <b><i>"out_LxL.txt"</b></i>.<br>
* If we create an experiment "experiment_1", in a folder "experiment_folder", and we want to measure, say, the magnetisation for L system size= [8, 16, 32, 64],
then we save by default the parameters in the folder "experiment_folder/experiment_1" (<i><b>"experiment_folder/experiment_1/parameter_8x8.txt"</i></b> etc).
* Then, after the low-level computation, the default folder for the out_file will be the same (<i><b>"experiment_folder/experiment_1/out_8x8.txt"</i></b>). so as the results can be gathered directly for further analyzing.<br>
#### Customization:
* You can create your own class which inherits from the "<b>ExperimentHandler</b>" class then add & override functionality; and same for the "<b>ExperimentOutput</b>" class.
* The easiest is simply to modify the "<b>MonteCarloExperiment</b>" & "<b>MonteCarloData</b>" classes in the example to suit your need (ie: change/add parameters, change the formatted output etc).
#### TODO:
* Example libs to read the parameter / output results for 2D Ising in Rust

See also: [2d_ising_in_rust](https://github.com/so-groenen/2d_ising_in_rust)
