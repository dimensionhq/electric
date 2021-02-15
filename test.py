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
