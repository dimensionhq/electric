// This file is part of rget.
//
// Copyright (C) 2016-2017 Arcterus (Alex Lyon) and rget contributors.
//
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

use term::{self, StdoutTerminal, StderrTerminal};

pub trait OutputManager {
   fn info(&mut self, msg: &str);
   fn warn(&mut self, msg: &str);
   fn error(&mut self, msg: &str);
}

pub struct StdOutputManager {
   stdout: Box<StdoutTerminal>,
   stderr: Box<StderrTerminal>
}

impl StdOutputManager {
   pub fn new() -> StdOutputManager {
      StdOutputManager {
         stdout: term::stdout().unwrap(),
         stderr: term::stderr().unwrap()
      }
   }
}

impl OutputManager for StdOutputManager {
   fn info(&mut self, msg: &str) {
      self.stdout.fg(term::color::GREEN).unwrap();
      writeln!(self.stdout, "info: {}", msg).unwrap();
      self.stdout.reset().unwrap();
   }

   fn warn(&mut self, msg: &str) {
      self.stdout.fg(term::color::YELLOW).unwrap();
      writeln!(self.stdout, "warn: {}", msg).unwrap();
      self.stdout.reset().unwrap();
   }

   fn error(&mut self, msg: &str) {
      self.stderr.fg(term::color::RED).unwrap();
      writeln!(self.stderr, "error: {}", msg).unwrap();
      self.stderr.reset().unwrap();
   }
}