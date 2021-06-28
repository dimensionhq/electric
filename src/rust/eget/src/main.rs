// Modules
mod download;

use download::network::DownloaderConfig;

use download::Downloader;
use std::env;
use std::env::args;

fn main() {
    ansi_term::enable_ansi_support().unwrap();
    let args: Vec<String> = args().collect();
    let url = &args[1];
    let threads = &args[2].parse::<u64>().unwrap();
    let checksum;
    let name = &args[3];

    if args.len() > 4 {
        checksum = Some(&args[4]);
    }

    // Download
    let mut dl = Downloader::new(threads.to_owned(), DownloaderConfig::default());
    dl.download(
        url.as_str(),
        Some(format!(r"{}\Setup-{}.exe", env!("TEMP"), name).as_str()),
    )
    .unwrap();
}
