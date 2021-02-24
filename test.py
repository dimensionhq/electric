#   -v, --version
#   --nightly, --pre-release
#   -p, --portable, --non-admin  
#   -vb, --verbose               
#   -d, --debug                  
#   -np, --no-progress           
#   -nc, --no-color              
#   -l, --log-output        
#   -dir, --install-dir     
#   -vc, --virus-check           
#   -y, --yes                    
#   -s, --silent                 
#   -vs, --vscode                
#   -sb, --sublime               
#   -ato, --atom                 
#   -py, --python                
#   -npm, --node                 
#   -nocache, --no-cache
#   -sc, --sync
#   -rd, --reduce
#   -rl, --rate-limit INTEGER
#   -f, --force
#   -cf, --configuration      
#   -pl, --plugin                
#   -h, --help               

from colorama import Fore
import os

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

