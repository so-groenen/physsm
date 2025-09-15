import numpy as np

def array_to_str(array: np.ndarray, rounding: int) -> list[str]:
    temps_str = []
    for val in array:
        temps_str.append(str(round(val,rounding)))
    return ", ".join(temps_str)


def write_formated(param_file: str, out_file: str, rows: np.uint, cols: np.uint, therm_steps: np.uint, measure_steps: np.uint, temperatures: np.uint, rounding = 3)->None:
    with open(param_file, "w") as f:
        f.write(f"rows: {rows}\n")
        f.write(f"cols: {cols}\n")
        f.write(f"therm_steps: {therm_steps}\n")
        f.write(f"measure_steps: {measure_steps}\n")
        f.write(f"temperatures: {array_to_str(temperatures, rounding)}\n")
        f.write(f"outputfile: {out_file}\n")
