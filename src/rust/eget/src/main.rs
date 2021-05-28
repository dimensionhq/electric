// Modules
mod download;

use download::network::DownloaderConfig;

use download::Downloader;
use std::env::args;

fn main() {
    ansi_term::enable_ansi_support().unwrap();
    let args: Vec<String> = args().collect();
    let url = &args[1];
    let threads = &args[2].parse::<u64>().unwrap();
    let checksum;

    if args.len() > 3 {
        checksum = Some(&args[2]);
    }

    // Download
    let mut dl = Downloader::new(threads.to_owned(), DownloaderConfig::default());
    dl.download(url.as_str(), Some("test.exe")).unwrap();
}
