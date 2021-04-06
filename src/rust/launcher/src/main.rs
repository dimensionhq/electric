use colored::*;
use reqwest::blocking;
use std::process::Command;
use std::thread;
use std::{env, fs::File, io::Write};
use std::{process, time::Duration};

fn main() {
    let args: Vec<String> = env::args().collect();
    // Handle Package Installation
    // ["C:\\Users\\xtrem\\Desktop\\Electric\\electric\\src\\rust\\launcher\\target\\release\\launcher.exe", "electric:configuration=https://srv-store5.gofile.io/download/UfDNfJ/electric-configuration.electric,name=test"]
    let mut parse: String = args[1].to_string();

    // Install Electric Packages
    if parse.starts_with("electric:packages=") {
        println!("Installing Packages");
        parse = parse.replace("electric:packages=", "");

        Command::new("powershell.exe")
            .arg("-c")
            .arg("electric")
            .arg("install")
            .arg(parse)
            .spawn()
            .unwrap();
    }
    // Install Electric Configuration
    else if parse.starts_with("electric:configuration=") {
        println!("Installing Configuration");
        // Parse Url
        parse = parse.replace("electric:configuration=", "");
        parse = parse.replace("name=", "");
        let parse_array: Vec<&str> = parse.split(",").collect();
        let url = &parse_array[0];
        let configuration_name = &parse_array[1];
        println!("Downloading Electric Configuration...");
        let file_path = download_configuration(configuration_name, url);
        println!("Successfully Downloaded Configuration");
        println!("{}", file_path);
        Command::new("powershell.exe")
            .arg("-c")
            .arg("electric")
            .arg("config")
            .arg(format!("\"{}\"", file_path))
            .spawn()
            .unwrap();
    }
}

pub fn download_configuration(name: &str, url: &str) -> String {
    #[allow(unused_assignments)]
    let mut res: String = String::new();

    match blocking::get(format!("{}", url)) {
        Ok(response) => {
            if response.status() == reqwest::StatusCode::OK {
                // Response Code Is 200 OK
                match response.text() {
                    Ok(text) => {
                        res = text;
                    }
                    Err(e) => {
                        println!(
                            "{} {}",
                            "Failed To Parse Response:".to_string().yellow(),
                            e.to_string().bright_red()
                        );
                        process::exit(1);
                    }
                }
            } else {
                println!("Invalid Url For Configuration!");
                thread::sleep(Duration::from_secs(5));
                process::exit(1);
            }
        }
        Err(err) => {
            println!("Failed To Request Configuration => {}", err);
            thread::sleep(Duration::from_secs(5));
            process::exit(1)
        }
    }

    let temp = format!(r"{}\{}.electric", env::var("TEMP").unwrap(), name);
    let mut file = File::create(&temp).unwrap();
    file.write_all(res.as_bytes()).unwrap();

    temp
}
