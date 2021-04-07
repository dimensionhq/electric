use std::env::var;
use std::fs::{read_to_string, File, OpenOptions};
use std::io::Write;
use std::path::Path;
use std::process::Command;

const SETUP: &str = r#"
# Electric Tab Completion
Register-ArgumentCompleter -Native -CommandName electric -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
        [Console]::InputEncoding = [Console]::OutputEncoding = $OutputEncoding = [System.Text.Utf8Encoding]::new()
        $Local:word = $wordToComplete.Replace('"', '""')
        $Local:ast = $commandAst.ToString().Replace('"', '""')
        completer --word="$Local:word" --commandline "$Local:ast" --position $cursorPosition | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
}

# Refresh Environment Variables
function Update-Environment() {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Host -ForegroundColor Green "Sucessfully Refreshed Environment Variables For powershell.exe"
}

Set-Alias refreshenv Update-Environment
"#;

fn main() {
    Command::new("powershell.exe")
        .arg("-c")
        .arg("Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force");

    let userprofile = var("USERPROFILE").unwrap();
    let temp = format!(r"{}\Documents\WindowsPowerShell", userprofile);

    let temploc: &Path = Path::new(temp.as_str());
    if !temploc.exists() {
        std::fs::create_dir(temploc).unwrap();
    }

    let powershell_loc: String = format!(
        r"{}\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1",
        userprofile
    )
    .to_string();

    let powershell_path = Path::new(powershell_loc.as_str());

    if powershell_path.exists() {
        // File Exists
        let current: String = read_to_string(&powershell_loc).unwrap();
        if !current
            .contains("Register-ArgumentCompleter -Native -CommandName electric -ScriptBlock {")
            && !current.contains("function Update-Environment() {")
        {
            let mut file = OpenOptions::new()
                .append(true)
                .open(powershell_loc)
                .unwrap();
            file.write_all(SETUP.as_bytes()).unwrap();
        }
    } else {
        let mut file = File::create(powershell_loc.as_str()).unwrap();
        file.write_all(SETUP.as_bytes()).unwrap();
    }
}
