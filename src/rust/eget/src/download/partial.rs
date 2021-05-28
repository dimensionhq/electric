// This file is part of rget.
//
// Copyright (C) 2016-2017 Arcterus (Alex Lyon) and rget contributors.
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

use crate::download::util;
use std::fs::{self, File, Metadata, OpenOptions};
use std::io::{self, Read, Seek, SeekFrom, Write};
use std::path::{Path, PathBuf};
//use std::io::{BufReader, BufWriter};

pub struct FilePart {
    file: File,
    path: PathBuf,
}

impl FilePart {
    pub fn create<P: AsRef<Path>>(output: P, num: u64) -> FilePart {
        let path = FilePart::add_part_extension(output, num);
        FilePart {
            file: File::create(&path).unwrap(),
            path: path,
        }
    }

    pub fn load_or_create<P: AsRef<Path>>(output: P, num: u64) -> FilePart {
        let path = FilePart::add_part_extension(output, num);
        let mut file = OpenOptions::new()
            .write(true)
            .create(true)
            .open(&path)
            .unwrap();
        file.seek(SeekFrom::End(0)).unwrap();
        FilePart {
            file: file,
            path: path,
        }
    }

    pub fn open<P: AsRef<Path>>(input: P, num: u64) -> FilePart {
        let path = FilePart::add_part_extension(input, num);
        FilePart {
            file: File::open(&path).unwrap(),
            path: path,
        }
    }

    pub fn delete(self) {
        drop(self.file);
        fs::remove_file(self.path).unwrap();
    }

    pub fn metadata(&self) -> io::Result<Metadata> {
        self.file.metadata()
    }

    fn add_part_extension<P: AsRef<Path>>(path: P, num: u64) -> PathBuf {
        util::add_path_extension(path, &format!("part{}", num))
    }
}

impl Write for FilePart {
    fn write(&mut self, buf: &[u8]) -> io::Result<usize> {
        self.file.write(buf)
    }

    fn flush(&mut self) -> io::Result<()> {
        self.file.flush()
    }
}

impl Read for FilePart {
    fn read(&mut self, buf: &mut [u8]) -> io::Result<usize> {
        self.file.read(buf)
    }
}
