// This file is part of rget.
//
// Copyright (C) 2016-2017 Arcterus (Alex Lyon) and rget contributors.
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

#[macro_use]
extern crate clap;
extern crate term;
extern crate rget;

use std::io::{Write};
use std::process;

use rget::Downloader;
use rget::network::DownloaderConfig;

const DEFAULT_PARALLEL: &'static str = "4";

fn main() {
    let matches = clap_app!(rget =>
      (version: crate_version!())
      (author: crate_authors!())
      (about: "Download accelerator written in Rust")
      (@arg PARALLEL: -n --parallel +takes_value {is_number} /*default_value: "4"*/ "Number of parallel downloads")
      (@arg OUTPUT:   -o --output   +takes_value "Output file name")
      (@arg USERNAME: -u --user     +takes_value "Username")
      (@arg PASSWORD: -p --password +takes_value "Password")
      (@arg INSECURE: --insecure "Disable hostname verification")
      (@arg INPUT: +required "URL of the file to download")
      (@subcommand validate =>
         (about: "Validates a downloaded file")
      )
   ).get_matches();

   let mut stderr = term::stderr().unwrap();

   let parallel = match matches.value_of("PARALLEL").unwrap_or(DEFAULT_PARALLEL).parse::<u64>() {
      Ok(m) => m,
      Err(f) => {
         stderr.fg(term::color::RED).unwrap();
         writeln!(stderr, "{}", f).unwrap();
         process::exit(1)
      }
   };
   let input = matches.value_of("INPUT").unwrap();

   if let Some(_) = matches.subcommand_matches("validate") {
      unimplemented!();
   } else {
      let config = DownloaderConfig {
          username: matches.value_of("USERNAME").map(Into::into),
          password: matches.value_of("PASSWORD").map(Into::into),
          insecure: matches.is_present("INSECURE")
      };
      let mut downloader = Downloader::new(parallel, config);
      if let Err(f) = downloader.download(input, matches.value_of("OUTPUT")) {
         stderr.fg(term::color::RED).unwrap();
         writeln!(stderr, "error: {}", f).unwrap();
      }
   }
}

fn is_number(input: String) -> Result<(), String> {
   match input.parse::<u64>() {
      Ok(num) => if num > 0 {
         Ok(())
      } else {
         Err(String::from("the number of parallel downloads must be greater than 0"))
      },
      Err(_) => Err(String::from("the number of parallel downloads must be an integer"))
   }
}
