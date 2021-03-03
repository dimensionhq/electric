
<p align="center">
  <img src="https://github.com/electric-package-manager/electric/blob/master/assets/electric-icon-transparent-bg.png" />
</p>

<h1 align="center">Electric</h1>
<h4 align="center">A futuristic, powerful and fast package manager for Windows.</h1>
<br>

<p align="center">
  <img src="https://img.shields.io/github/v/tag/electric-package-manager/electric?color=green&label=electric&sort=semver"> <img src="https://img.shields.io/github/license/electric-package-manager/electric?color=pink"> <img src="https://img.shields.io/tokei/lines/github/electric-package-manager/electric?color=white&label=lines%20of%20code"> <img src="https://img.shields.io/github/languages/top/electric-package-manager/electric?color=%230xfffff"> <img src="https://img.shields.io/github/repo-size/electric-package-manager/electric?color=orange">
</p>

![Installing 7-Zip Through Electric](https://github.com/electric-package-manager/electric/blob/master/assets/install-animation.gif?raw=true)

Highly optimized for **speed** and usability, Electric is anywhere from 200% to 1500% faster than other market competitors for downloading Applications and Packages, and has incredible speeds for concurrent / parallel downloading.

Electric believes in incredible **effeciency**, and is the only Windows package manager that officially supports installing packages **concurrently**.

Built for today's systems and with good support for lower specced systems, Electric runs smoothly even on systems with as little as 2 GB of ram!

**Note**: Since electric is in an alpha phase, it might not be completely stable yet. Feel free to open any issues or bug reports at [issues](https://github.com/electric-package-manager/electric/issues).
<br>

## :zap: Installation

First you'll need to set your execution policy to RemoteSigned if not done so:
```powershell
Set-ExecutionPolicy RemoteSigned
```

### Method 1: Install Using Powershell
Run the following command on your powershell window:

```powershell
iwr -useb https://raw.githubusercontent.com/XtremeDevX/electric/dev/bin/electricInstall.ps1 | iex
```

### Method 2: Install Using Official Installer
#### Steps

1. Download the latest version of the electric Installer from the [Releases Page](https://github.com/electric-package-manager/electric/releases/)

2. After completing the download, start the installer (double-click) and follow the simple installation prompts.

**NOTE**: If you see warnings about the software not being trusted or from an unverified publisher, don't panic, this is a known issue as Electric is not code signed yet.

3. Open your command prompt (cmd.exe) or alternatively powershell (powershell.exe) and type `electric` to get a list of help commands.

4. Electric is installed on your system!

### Method 3: Build From Source
Prerequisites: **Git**, **Python 3.x**

1. Clone the github repository using the Github CLI.
```powershell
git clone https://www.github.com/electric-package-manager/electric
```

2. Change to the electric directory.
```powershell
cd electric
```

3. Install it locally using the Python package manager (`pip`)
```powershell
pip install --editable .
```

4. Register [Tab Completion](https://github.com/electric-package-manager/electric#tab-completion)

5. Type `electric` to get a help menu of commands.


## :clap: Supporters
[![Stargazers repo roster for @electric-package-manager/electric](https://reporoster.com/stars/electric-package-manager/electric)](https://github.com/electric-package-manager/electric/stargazers)

[![Forkers repo roster for @electric-package-manager/electric](https://reporoster.com/forks/electric-package-manager/electric)](https://github.com/electric-package-manager/electric/network/members)

## :hammer: Build Status
| Feature                            | Build Status   |
|------------------------------------|----------------|
| Installation                       | ✅            |
| Portable Installation              | ❌            |
| Uninstallation                     | ✅            |
| Update                             | ✅            |
| Show                               | ✅            |
| List                               | ✅            |
| Search                             | ✅            |
| Code Editor Extension Installation | ❌            |
| Python Package Installation        | ✅            |
| NodeJS Package Installation        | ✅            |
| Configuration Management           | ❌            |
| Cleanup                            | ✅            |
| Tab Completion                     | ✅            |

<br>

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
Then, restart your powershell and you've setup tab completion!

<br>

## Config In Alpha
A small peek of what's coming up next for electric! `(pssst! don't tell anyone!)`!

![Demonstration](https://github.com/XtremeDevX/Electric-Windows/blob/dev/assets/config-extension.gif?raw=true)
