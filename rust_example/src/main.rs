use std::env;
use std::fs;
use std::io::{Write, Result};

fn my_sum(a: usize, b: usize)->usize
{
    a+b
}
fn my_mul(a: usize, b: usize)->usize
{
    a*b
}

fn main() -> Result<()>
{
    let args: Vec<String> = env::args().collect();

    let parameter_file = &args[1];
    let contents       = fs::read_to_string(parameter_file)
        .expect("Should have been able to read the file");
    
    println!("Reading parameters:\n{contents}");

    let mut output_file_name: Option<String> = None;
    let mut length: Option<usize>            = None;
    let mut my_bool: Option<bool>            = None;
    
    for line in contents.lines()
    {
        if line.contains("outputfile")
        {
            let (_, output)  = line.split_once(":").expect("Should be able to split");
            output_file_name = Some(output.trim().to_owned());
        }
        if line.contains("Lx")
        {
            let (_, output) = line.split_once(":").expect("Should be able to split");
            length = Some(output.trim().parse().expect("Should be able to parse Lx"));
        }
        if line.contains("my_bool")
        {
            let (_, output) = line.split_once(":").expect("Should be able to split");
            my_bool = Some(output.trim().parse().expect("Should be able to parse my_bool"));
        }
    }

    let Some(output_file_name) = output_file_name else 
    {
        println!("Missing output filename! Cannot continue");
        std::process::exit(1);
    };
    let Some(length) = length else 
    {
        println!("Missing length! Cannot continue");
        std::process::exit(1);
    };

    if my_bool.is_none()
    {
        println!("Missing my_bool! Cannot continue");
        std::process::exit(1);
    };

    println!("Writing in {output_file_name}");
    let mut file = std::fs::File::create(output_file_name)?;

    writeln!(&mut file, "Hello world! [Lx={length}]")?;
    writeln!(&mut file, "{}, {}", my_sum(length,length), my_mul(length, length))?;
    
    Ok(())
}
