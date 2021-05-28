// This file is part of rget.
//
// Copyright (C) 2016-2017 Arcterus (Alex Lyon) and rget contributors.
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

use reqwest::{self, StatusCode};
use std::any::Any;
use std::fmt::{self, Display, Formatter};
use std::io;
use toml;

pub type Result<T> = ::std::result::Result<T, Error>;

#[derive(Debug)]
#[allow(bare_trait_objects)]
pub enum ErrorReason {
    IO(io::Error),
    MissingUrl,
    HttpErrorCode(StatusCode),
    FailedRequest(reqwest::Error),
    InvalidConfig(&'static str),
    InvalidToml(toml::de::Error),
    InvalidUrl(reqwest::UrlError),
    FailedThread(Box<Any + Send + 'static>),
    Multiple(Vec<Error>),
}

#[derive(Debug)]
pub struct Error {
    reason: ErrorReason,
}

impl Error {
    pub fn new(reason: ErrorReason) -> Error {
        Error { reason: reason }
    }
}

impl ErrorReason {
    fn to_string(&self) -> String {
        match *self {
            ErrorReason::IO(ref err) => format!("{}", err),
            ErrorReason::MissingUrl => {
                "no download configuration found and no valid URL given".to_string()
            }
            ErrorReason::HttpErrorCode(ref status) => format!("received {} from server", status),
            ErrorReason::FailedRequest(ref err) => format!("{}", err),
            ErrorReason::InvalidConfig(msg) => msg.to_string(),
            ErrorReason::InvalidToml(ref err) => {
                format!("invalid data in download configuration: {:?}", err)
            }
            ErrorReason::InvalidUrl(ref err) => format!("{}", err),
            ErrorReason::FailedThread(ref err) => format!("{:?}", err),
            ErrorReason::Multiple(ref errors) => errors
                .iter()
                .fold("".to_string(), |acc, ref err| format!("{}\n{}", acc, err)),
        }
    }
}

impl Display for Error {
    fn fmt(&self, fmt: &mut Formatter) -> fmt::Result {
        write!(fmt, "{}", self.reason.to_string())
    }
}
