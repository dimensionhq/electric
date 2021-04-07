fn main() {
    let commands: Vec<&str> = vec![
        "install",
        "uninstall",
        "update",
        "bundle",
        "search",
        "new",
        "config",
        "sign",
        "show",
        "find",
        "list",
    ];

    // ["C:\\Users\\xtrem\\Desktop\\Electric\\electric\\src\\rust\\completer\\target\\release\\completer.exe", "--word=in", "--commandline", "electric in", "--position", "11"]
    let args: Vec<String> = std::env::args().collect();
    let typed = &args[3];
    let parse: Vec<&str> = typed.split(" ").collect();

    if parse.len() == 1 {
        // Command: electric

        for command in commands.iter() {
            println!("{}", command);
        }
    } else if parse.len() == 2 {
        // Command: electric install | Command: electric in

        let command = &parse[1];

        if commands.contains(command) {
            // Complete Package Name Or Flags
        } else {
            // Complete Command
            for cmd in commands.iter() {
                if cmd.contains(command) {
                    println!("{}", &cmd);
                }
            }
        }
    }
}
