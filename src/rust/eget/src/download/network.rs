// This file is part of rget.
//
// Copyright (C) 2016-2017 Arcterus (Alex Lyon) and rget contributors.
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.
#![allow(dead_code, deprecated, unused_mut)]

#[path = "pbr/mod.rs"]
mod pbr;

use pbr::{MultiBar, ProgressBar, Units};
use reqwest::header::{
    Authorization, Basic, ByteRangeSpec, ContentLength, /*ContentRange,*/
    Range,
};
use reqwest::StatusCode;
use reqwest::{Client, Url};
use std::fs::{self, File, OpenOptions};
use std::io::{self, BufWriter, Read, Write};
use std::mem;
use std::path::{Path, PathBuf};
use std::sync::Arc;
use std::thread;
use std::time::Duration;
use std::u64;
use toml::{self, Value};

use serde_derive::Serialize;

use crate::download::error::{self, Error, ErrorReason};
use crate::download::output::{OutputManager, StdOutputManager};
use crate::download::partial::FilePart;
use crate::download::util;

const PRINT_DELAY: u64 = 100;

#[derive(Default, Clone)]
pub struct DownloaderConfig {
    pub username: Option<String>,
    pub password: Option<String>,
    pub insecure: bool,
}

pub struct Downloader<T: OutputManager> {
    parallel: u64,
    config: DownloaderConfig,
    output: T,
}

impl Downloader<StdOutputManager> {
    pub fn new(parallel: u64, config: DownloaderConfig) -> Downloader<StdOutputManager> {
        Downloader::with_output_manager(parallel, config, StdOutputManager::new())
    }
}

impl<T: OutputManager> Downloader<T> {
    pub fn with_output_manager(
        parallel: u64,
        config: DownloaderConfig,
        output: T,
    ) -> Downloader<T> {
        Downloader {
            parallel: parallel,
            config: config,
            output: output,
        }
    }

    pub fn download(&mut self, input: &str, output: Option<&str>) -> error::Result<()> {
        let (output_path, url) = match Url::parse(input) {
            Ok(ref url) if url.scheme() != "file" => {
                // FIXME: still won't work if last character in url is /
                let closure = || input.rsplit('/').next().unwrap();
                (Path::new(output.unwrap_or_else(closure)), Some(url.clone()))
            }
            _ => {
                let closure = || {
                    input
                        .trim_left_matches("file://")
                        .trim_right_matches(".toml")
                };
                (Path::new(output.unwrap_or_else(closure)), None)
            }
        };
        let (parallel, url, scratch) = self.reload_state(output_path, url)?;
        self.download_url(url, output_path, parallel, scratch)
    }

    fn download_url<P: AsRef<Path>>(
        &mut self,
        url: Url,
        output: P,
        mut parallel: u64,
        mut scratch: bool,
    ) -> error::Result<()> {
        // Apparently Client contains a connection pool, so reuse the same Client
        let mut client_builder = Client::builder().unwrap();
        if self.config.insecure {
            client_builder.danger_disable_hostname_verification();
        }
        let client = Arc::new(client_builder.build().unwrap());
        //let config = Arc::new(self.config.clone());

        let length = match self.get_length(client.clone(), url.clone()) {
            Some(length) => Some(length),
            None => {
                scratch = true;
                parallel = 1;
                None
            }
        };

        let mut children = vec![];
        let mut mb = MultiBar::new();

        for i in 0u64..parallel {
            let url = url.clone();
            let output = output.as_ref().to_path_buf();
            let client = client.clone();
            let config = self.config.clone();
            let mut progbar = mb.create_bar(100);

            progbar.set_max_refresh_rate(Some(Duration::from_millis(PRINT_DELAY)));
            progbar.show_message = true;
            progbar.set_units(Units::Bytes);

            children.push(thread::spawn(move || {
                Downloader::<T>::download_callback(
                    i, progbar, client, url, output, length, parallel, config, scratch,
                )
            }));
        }

        if scratch {
            if let Err(f) = self.create_download_config(output.as_ref(), url, parallel) {
                self.output.error(&f); // continue, but let the user know that they can't stop the download
            }
        }

        mb.listen();

        let mut errors = vec![];
        for child in children {
            match child.join() {
                Ok(Err(f)) => errors.push(f),
                Err(f) => errors.push(Error::new(ErrorReason::FailedThread(f))),
                _ => {}
            }
        }

        if errors.len() > 0 {
            Err(Error::new(ErrorReason::Multiple(errors)))
        } else {
            let result = self.merge_parts(parallel, output.as_ref());
            match result {
                Ok(()) => self.delete_download_config(output),
                err => err,
            }
        }
    }

    fn download_callback<W: Write>(
        part: u64,
        mut pb: ProgressBar<W>,
        client: Arc<Client>,
        url: Url,
        output: PathBuf,
        length: Option<u64>,
        parallel: u64,
        config: DownloaderConfig,
        scratch: bool,
    ) -> error::Result<()> {
        pb.message("Waiting  : ");

        let (mut file, filelen) = if scratch {
            (FilePart::create(&output, part), 0)
        } else {
            let file = FilePart::load_or_create(&output, part);
            let len = match file.metadata() {
                Ok(data) => data.len(),
                Err(/*f*/ _) => {
                    //self.output.error(&format!("{}", f));
                    //self.output.warn("downloading from byte 0");
                    0
                }
            };
            (file, len)
        };

        let mut request = client.get(url).unwrap();
        if let Some(length) = length {
            let section = length / parallel;
            if section == filelen || (part + 1 == parallel && length - section * part == filelen) {
                // FIXME: does not print correctly when the program is restarted after an interrupted
                //        download
                pb.finish();
                // pb.finish_print(&format!("Completed: {}.part{}", output.display(), part));
                return Ok(());
            }
            let from = filelen + part * section;
            let to = if part + 1 == parallel {
                length
            } else {
                (part + 1) * section
            } - 1;
            request.header(Range::Bytes(vec![ByteRangeSpec::FromTo(from, to)]));
        }

        if let Some(username) = config.username {
            request.header(Authorization(Basic {
                username: username,
                password: config.password,
            }));
        }

        let part = part as usize;
        let result = match request.send() {
            Ok(mut resp) => {
                pb.message("Connected: ");
                // FIXME: is this right/all?
                if resp.status() == StatusCode::Ok || resp.status() == StatusCode::PartialContent {
                    let &ContentLength(length) =
                        resp.headers().get().unwrap_or(&ContentLength(u64::MAX));
                    pb.total = length;
                    // TODO: check accept-ranges or whatever
                    let mut buffer: [u8; 8192] = unsafe { mem::uninitialized() };
                    let mut downloaded = 0;
                    while downloaded < length {
                        match resp.read(&mut buffer) {
                            Ok(n) => {
                                if n == 0 {
                                    break;
                                } else {
                                    downloaded += n as u64;
                                    file.write_all(&buffer[0..n]).unwrap();
                                    pb.add(n as u64);
                                }
                            }
                            Err(f) => return Err(Error::new(ErrorReason::IO(f))),
                        }
                        pb.tick();
                    }
                    pb.finish();
                    // pb.finish_print(&format!("Completed: {}.part", output.display()));
                    Ok(())
                } else {
                    // pb.finish();
                    pb.finish_print(&format!("Failed   : {}.part{}", output.display(), part));
                    Err(Error::new(ErrorReason::HttpErrorCode(resp.status())))
                }
            }
            Err(f) => {
                pb.finish_print(&format!("Failed   : {}.part{}", output.display(), part));
                Err(Error::new(ErrorReason::FailedRequest(f)))
            }
        };

        result
    }

    fn merge_parts<P: AsRef<Path>>(&self, parallel: u64, output_path: P) -> error::Result<()> {
        let file = match OpenOptions::new()
            .write(true)
            .create(true)
            .open(output_path.as_ref())
        {
            Ok(m) => m,
            Err(f) => return Err(Error::new(ErrorReason::IO(f))),
        };

        let mut output = BufWriter::new(file);
        let mut total_size = 0;
        for i in 0..parallel {
            let mut infile = FilePart::open(output_path.as_ref(), i);
            match io::copy(&mut infile, &mut output) {
                Ok(n) => total_size += n as u64,
                Err(f) => return Err(Error::new(ErrorReason::IO(f))),
            }
            infile.delete();
        }
        output.into_inner().unwrap().set_len(total_size).unwrap();

        Ok(())
    }

    fn reload_state<P: AsRef<Path>>(
        &mut self,
        output_path: P,
        given_url: Option<Url>,
    ) -> error::Result<(u64, Url, bool)> {
        match File::open(util::add_path_extension(output_path, "toml")) {
            Ok(mut file) => {
                let mut data = String::new();

                if let Err(f) = file.read_to_string(&mut data) {
                    return Err(Error::new(ErrorReason::IO(f)));
                }

                match toml::from_str::<Value>(&data) {
                    Ok(table) => {
                        let parallel = match table.get("parallel") {
                            Some(n) => match n.as_integer() {
                                Some(num) => num as u64,
                                None => {
                                    return Err(Error::new(ErrorReason::InvalidConfig(
                                        "number of parallel downloads in download \
                                           configuration must be an integer",
                                    )))
                                }
                            },
                            None => {
                                return Err(Error::new(ErrorReason::InvalidConfig(
                                    "could not find number of parallel downloads in \
                                        configuration",
                                )))
                            }
                        };

                        let stored_url = match table.get("url") {
                            Some(url) => match url.as_str() {
                                Some(url_str) => match Url::parse(url_str) {
                                    Ok(url) => url,
                                    Err(f) => return Err(Error::new(ErrorReason::InvalidUrl(f))),
                                },
                                None => {
                                    return Err(Error::new(ErrorReason::InvalidConfig(
                                        "URL in download configuration must be a \
                                             string",
                                    )))
                                }
                            },
                            None => {
                                return Err(Error::new(ErrorReason::InvalidConfig(
                                    "could not find URL for download in \
                                          configuration",
                                )))
                            }
                        };

                        Ok((parallel, given_url.unwrap_or(stored_url), false))
                    }

                    Err(f) => Err(Error::new(ErrorReason::InvalidToml(f))),
                }
            }

            Err(ref f) if f.kind() == io::ErrorKind::NotFound => match given_url {
                Some(url) => Ok((self.parallel, url, true)),
                None => Err(Error::new(ErrorReason::MissingUrl)),
            },

            Err(f) => Err(Error::new(ErrorReason::IO(f))),
        }
    }

    fn create_download_config<P: AsRef<Path>>(
        &self,
        output: P,
        url: Url,
        parallel: u64,
    ) -> Result<(), String> {
        #[derive(Serialize)]
        struct DownloadConfig {
            url: String,
            parallel: u64,
        }

        let config = DownloadConfig {
            url: url.to_string(),
            parallel: parallel,
        };

        match File::create(util::add_path_extension(output, "toml")) {
            Ok(mut file) => {
                file.write_all(toml::to_string(&config).unwrap().as_bytes())
                    .unwrap();
                Ok(())
            }
            Err(f) => Err(format!("{}", f)),
        }
    }

    fn delete_download_config<P: AsRef<Path>>(&self, output: P) -> error::Result<()> {
        match fs::remove_file(util::add_path_extension(output, "toml")) {
            Ok(()) => Ok(()),
            Err(f) => Err(Error::new(ErrorReason::IO(f))),
        }
    }

    fn get_length(&self, client: Arc<Client>, url: Url) -> Option<u64> {
        let mut request = client.get(url).unwrap();
        if let Some(ref username) = self.config.username {
            request.header(Authorization(Basic {
                username: username.to_owned(),
                password: self.config.password.to_owned(),
            }));
        }

        match request.send() {
            Ok(resp) => {
                if resp.status() == StatusCode::Ok {
                    match resp.headers().get() {
                        Some(&ContentLength(length)) => Some(length),
                        None => None,
                    }
                } else {
                    None
                }
            }
            Err(_) => None,
        }
    }
}
