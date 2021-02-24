#   -cf, --configuration
#   -pl, --plugin

from timeit import default_timer as timer
from subprocess import Popen, PIPE
from colorama import Fore
import os

os.system('electric uninstall sublime-text-3')
os.system('electric uninstall sublime-text-3 --portable')
os.system('electric uninstall atom')
os.system('cls')

start = timer()
ec1 = os.system('electric install sublime-text-3 --portable')
ec2 = os.system('electric uninstall sublime-text-3 --portable')
if ec1 == 0 and ec2 == 0:
    print(f'{Fore.GREEN}✅ Passed Portable Check ✅{Fore.RESET}')
else:
    print(f'{Fore.RED}❌ Failed Portable Check ❌{Fore.RESET}')

ec1 = os.system('electric show sublime-text-3')
ec2 = os.system('electric search sublime-text-3')

if ec1 == 0 and ec2 == 0:
    print(f'{Fore.GREEN}✅ Show And Search Check ✅{Fore.RESET}')
else:
    print(f'{Fore.RED}❌ Show And Search Check ❌{Fore.RESET}')

ec1 = os.system('electric install sublime-text-3')
ec2 = os.system('electric uninstall sublime-text-3')

if ec1 == 0 and ec2 == 0:
    print(f'{Fore.GREEN}✅ Basic Installation And Uninstallation Check ✅{Fore.RESET}')
else:
    print(f'{Fore.RED}❌ Basic Installation And Uninstallation Check ❌{Fore.RESET}')

ec1 = os.system('electric install sublime-text-3 --verbose')
ec2 = os.system('electric uninstall sublime-text-3 --verbose')

if ec1 == 0 and ec2 == 0:
    print(f'{Fore.GREEN}✅ Verbose Installation And Uninstallation Check ✅{Fore.RESET}')
else:
    print(f'{Fore.RED}❌ Verbose Installation And Uninstallation Check ❌{Fore.RESET}')

ec1 = os.system('electric install sublime-text-3 --debug')
ec2 = os.system('electric uninstall sublime-text-3 --debug')

if ec1 == 0 and ec2 == 0:
    print(f'{Fore.GREEN}✅ Debug Installation And Uninstallation Check ✅{Fore.RESET}')
else:
    print(f'{Fore.RED}❌ Debug Installation And Uninstallation Check ❌{Fore.RESET}')

ec1 = os.system('electric install sublime-text-3 --debug --verbose')
ec2 = os.system('electric uninstall sublime-text-3 --debug --verbose')

if ec1 == 0 and ec2 == 0:
    print(f'{Fore.GREEN}✅ Debug + Verbose Installation And Uninstallation Check ✅{Fore.RESET}')
else:
    print(f'{Fore.RED}❌ Debug + Verbose Installation And Uninstallation Check ❌{Fore.RESET}')

ec1 = os.system('electric install atom --nightly')
ec2 = os.system('electric uninstall atom')

if ec1 == 0 and ec2 == 0:
    print(f'{Fore.GREEN}✅ Nightly / Prerelease Installation And Uninstallation Check ✅{Fore.RESET}')
else:
    print(f'{Fore.RED}❌ Nightly / Prerelease Installation And Uninstallation Check ❌{Fore.RESET}')

ec1 = os.system('electric install atom --version 1.52.0')
ec2 = os.system('electric uninstall atom')

if ec1 == 0 and ec2 == 0:
    print(f'{Fore.GREEN}✅ Specific Version Installation And Uninstallation Check ✅{Fore.RESET}')
else:
    print(f'{Fore.RED}❌ Specific Version Installation And Uninstallation Check ❌{Fore.RESET}')

ec1 = os.system('electric install sublime-text-3 --no-progress')
ec2 = os.system('electric uninstall sublime-text-3')

if ec1 == 0 and ec2 == 0:
    print(f'{Fore.GREEN}✅ No-Progress Installation And Uninstallation Check ✅{Fore.RESET}')
else:
    print(f'{Fore.RED}❌ No-Progress Installation And Uninstallation Check ❌{Fore.RESET}')

ec1 = os.system('electric install sublime-text-3 --no-color')
ec2 = os.system('electric uninstall sublime-text-3 --no-color')

if ec1 == 0 and ec2 == 0:
    print(f'{Fore.GREEN}✅ No-Color Installation And Uninstallation Check ✅{Fore.RESET}')
else:
    print(f'{Fore.RED}❌ No-Color Installation And Uninstallation Check ❌{Fore.RESET}')

ec1 = os.system(r'electric install sublime-text-3 --log-output C:\Users\xtrem\Desktop\electric-log.txt')
ec2 = os.system(r'electric uninstall sublime-text-3 --log-output C:\Users\xtrem\Desktop\electric-log.txt')


if ec1 == 0 and ec2 == 0:
    print(f'{Fore.GREEN}✅ Logging Installation And Uninstallation Check ✅{Fore.RESET}')
else:
    print(f'{Fore.RED}❌ Logging Installation And Uninstallation Check ❌{Fore.RESET}')

ec1 = os.system(r'electric install sublime-text-3 --install-dir "C:\Users\xtrem\Desktop\NewFolder"')
ec2 = os.system(r'electric uninstall sublime-text-3')

if ec1 == 0 and ec2 == 0:
    print(f'{Fore.GREEN}✅ Custom Installation Directory Installation And Uninstallation Check ✅{Fore.RESET}')
else:
    print(f'{Fore.RED}❌ Custom Installation Directory Installation And Uninstallation Check ❌{Fore.RESET}')

ec1 = os.system(r'electric install sublime-text --yes')
ec2 = os.system(r'electric uninstall sublime-text --yes')

if ec1 == 0 and ec2 == 0:
    print(f'{Fore.GREEN}✅ No-Prompt Installation And Uninstallation Check ✅{Fore.RESET}')
else:
    print(f'{Fore.RED}❌ No-Prompt Installation And Uninstallation Check ❌{Fore.RESET}')

proc = Popen('electric install sublime-text-3 --silent', stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
output, err = proc.communicate()
if output == b'' and err == b'' and proc.returncode == 0:
    print(f'{Fore.GREEN}✅ Silent Installation Check ✅{Fore.RESET}')
else:
    print(f'{Fore.GREEN}❌ Silent Installation Check ❌{Fore.RESET}')

ec1 = os.system('electric install sublime-text-3 --rate-limit 2000')
ec2 = os.system('electric uninstall sublime-text-3 --rate-limit 2000')

if output == b'' and err == b'' and proc.returncode == 0:
    print(f'{Fore.GREEN}✅ Rate Limit Check ✅{Fore.RESET}')
else:
    print(f'{Fore.GREEN}❌ Rate Limit Check ❌{Fore.RESET}')

proc = Popen('electric uninstall sublime-text-3 --silent', stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
output, err = proc.communicate()
if output == b'' and err == b'' and proc.returncode == 0:
    print(f'{Fore.GREEN}✅ Silent Uninstallation Check ✅{Fore.RESET}')
else:
    print(f'{Fore.GREEN}❌ Silent Uninstallation Check ❌{Fore.RESET}')

ec1 = os.system('electric install aaron-bond.better-comments --vscode')
ec2 = os.system('electric uninstall aaron-bond.better-comments --vscode')

if ec1 == 0 and ec2 == 0:
    print(f'{Fore.GREEN}✅ Visual Studio Code Extension Installation And Uninstallation Check ✅{Fore.RESET}')
else:
    print(f'{Fore.RED}❌ Visual Studio Code Extension Installation And Uninstallation Check ❌{Fore.RESET}')

ec2 = os.system('electric uninstall requests --python')
ec1 = os.system('electric install requests --python')

if ec1 == 0 and ec2 == 0:
    print(f'{Fore.GREEN}✅ Python Package Installation And Uninstallation Check ✅{Fore.RESET}')
else:
    print(f'{Fore.RED}❌ Python Package Installation And Uninstallation Check ❌{Fore.RESET}')

ec1 = os.system('electric install express --node')
ec2 = os.system('electric uninstall express --node')

if ec1 == 0 and ec2 == 0:
    print(f'{Fore.GREEN}✅ Node Package Installation And Uninstallation Check ✅{Fore.RESET}')
else:
    print(f'{Fore.RED}❌ Node Package Installation And Uninstallation Check ❌{Fore.RESET}')

ec1 = os.system('electric install sublime-text-3 --force')
ec2 = os.system('electric uninstall sublime-text-3')

if ec1 == 0 and ec2 == 0:
    print(f'{Fore.GREEN}✅ Force Package Installation Check ✅{Fore.RESET}')
else:
    print(f'{Fore.RED}❌ Force Package Installation Check ❌{Fore.RESET}')

# TODO: Add Multi-Threading Downloading

ec1 = os.system('electric install sublime-text-3 --reduce')
ec2 = os.system('electric uninstall sublime-text-3')

if ec1 == 0 and ec2 == 0:
    print(f'{Fore.GREEN}✅ Reduce Installation And Uninstallation Check ✅{Fore.RESET}')
else:
    print(f'{Fore.RED}❌ Reduce Installation And Uninstallation Check ❌{Fore.RESET}')

end = timer()
print(f'{Fore.GREEN}Execution Completed In {end - start}s {Fore.RESET}')
