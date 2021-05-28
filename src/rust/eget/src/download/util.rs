// This file is part of rget.
//
// Copyright (C) 2016-2017 Arcterus (Alex Lyon) and rget contributors.
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

use std::ffi::OsStr;
use std::path::{Path, PathBuf};

pub fn add_path_extension<P: AsRef<Path>>(path: P, ext: &str) -> PathBuf {
   let mut file_ext = path.as_ref().extension().unwrap_or(OsStr::new("")).to_os_string();
   file_ext.push(OsStr::new(&format!(".{}", ext)));
   path.as_ref().with_extension(file_ext)
}