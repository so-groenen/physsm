use std::env;
use std::fs;
use std::io::{Write, Result};
 

fn main() -> Result<()>
{
    let args: Vec<String> = env::args().collect();
    if args.len() < 2
    {
        eprintln!("Usage: rust_example.exe parameter.txt");
        std::process::exit(1);
    }

    let parameter_file = &args[1];
    let contents       = fs::read_to_string(parameter_file)
        .expect("Should have been able to read the file!");
    
    println!("Hello from Rust! Reading parameters: \n{contents}");

    let mut output_file_name: Option<String>  = None;
    let mut length: Option<usize>             = None;
    let mut monte_carlo_trials: Option<usize> = None;
    let mut temperature: Option<Vec<f32>>     = None;
    
    for line in contents.lines()
    {
        let (key, value)  = line.split_once(":").expect("Should be able to split");
        let key           = key.trim();
        let value         = value.trim();
        
        match key
        {
            "outputfile" =>  output_file_name          = Some(value.to_string()),
            "length"     =>  length                    = Some(value.trim().parse().expect("Should be able to parse length")),
            "monte_carlo_trials" => monte_carlo_trials = Some(value.trim().parse().expect("Should be able to parse monte_carlo_trials")),
            "temperature" => temperature               = Some(value.split(',').map(|x|x.trim().parse().unwrap()).collect::<Vec<_>>()),
            _ => eprintln!("Unknown key encountered!")
        }
    }

    let output_file_name   = output_file_name.expect("missing outputfile!");
    let length             = length.expect("missing length!");
    let monte_carlo_trials = monte_carlo_trials.expect("missing monte_carlo_trials!");
    let temperature        = temperature.expect("missing temperature!");

    assert!(!temperature.is_empty(), "temperature vector should not be empty!");

    let n_temp = temperature.len();
    let start  = temperature.first().unwrap();
    let last   = temperature.last().unwrap();

    println!(">> Performing Mock experiment using length={length} with trials={monte_carlo_trials} with {n_temp} temps from {:.2} to {:.2}.",
                start, last);

    println!(">> Writing in {output_file_name}");
    let mut file = std::fs::File::create(output_file_name)?;

    writeln!(&mut file, "Hello from Rust!")?;
    writeln!(&mut file, "result1 => {:.2}", (length as f32) * 100_f32 + 42_f32)?;
    writeln!(&mut file, "result2 => {}",    (monte_carlo_trials as f32) + 42_f32)?;
    
    Ok(())
}
