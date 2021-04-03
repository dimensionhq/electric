use std::env;
use std::{thread, time};

fn main() {
    let args: Vec<String> = env::args().collect();
    // Handle Package Installation
    println!("{:?}", args);
    thread::sleep(time::Duration::from_secs(10));
}
