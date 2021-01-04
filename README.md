# Electric

<img src="https://img.shields.io/github/v/tag/TheBossProSniper/Electric-Windows?color=green&label=electric&sort=semver"> <img src="https://img.shields.io/github/license/TheBossProSniper/Electric-Windows?color=pink"> <img src="https://img.shields.io/tokei/lines/github/TheBossProSniper/Electric-Windows?color=white&label=lines%20of%20code"> <img src="https://img.shields.io/github/languages/top/TheBossProSniper/Electric-Windows?color=%230xfffff"> <img src="https://img.shields.io/github/repo-size/TheBossProSniper/Electric?color=orange">
***

![Installing 7-Zip Through Electric](https://github.com/XtremeDevX/Electric-Windows/blob/dev/assets/installation.gif?raw=true)


A package manager for Windows!

Highly optimized for speed and usability, Electric is anywhere from 200% to 1500% faster than other market competitors for downloading Applications and Packages, and has incredible speeds for concurrent / parallel downloading.

Electric, unlike your average package manager believes in incredible effeciency, and officially supports installing packages concurrently (not one after another).

Built for today's systems and with good support for lower specced systems, Electric runs smoothly even on systems with as little as 2 GB of ram!

IMPORTANT: Since electric is in an alpha phase, it might not be completely stable yet. Feel free to open any issues or bug reports at [issues](https://github.com/TheBossProSniper/electric-windows/issues).

## Installation

IMPORTANT: Currently electric only works on Windows Systems, With Support In Progress For Darwin ( MacOSX ) and Debian Based Systems

#### Steps

1. Download the latest version of the electric Installer from the [Releases Page](https://github.com/TheBossProSniper/electric-windows/releases/tag/v1.0.0-alpha)

2. After completing the download, start the installer (double-click) and follow the simple installation prompts.

NOTE: If you see warnings about the software not being trusted or from an unverified publisher, don't panic, this is a known issue as Electric is not code signed yet.

3. Open your command prompt (cmd.exe) or alternatively powershell (powershell.exe) and type `electric` to get a list of help commands.

4. Yaay! Electric is installed on your system!

#### Tab Completion
When using the official Electric installer, tab completion is setup for you out of the box, however, it is possible to manually add tab completion for electric.
Add the below lines to your powershell profile:
```powershell
    Register-ArgumentCompleter -Native -CommandName electric -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    [Console]::InputEncoding = [Console]::OutputEncoding = $OutputEncoding = [System.Text.Utf8Encoding]::new()
    $Local:word = $wordToComplete.Replace('"', '""')
    $Local:ast = $commandAst.ToString().Replace('"', '""')
    electric complete --word="$Local:word" --commandline "$Local:ast" --position $cursorPosition | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }
}
```
Then, restart your powershell and viola, you've setup tab completion!


## Config In Alpha
A small peek of what's coming up next for electric! `(pssst! don't tell anyone!)`!

![Demonstration](https://github.com/XtremeDevX/Electric-Windows/blob/dev/assets/config-extension.gif?raw=true)
