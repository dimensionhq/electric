use std::env;

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
    let parse: Vec<&str> = typed.split(",").collect();

    if parse.len() == 1 {
        // Command: electric

        for command in commands.iter() {
            println!("{}", command);
        }
    }
}
