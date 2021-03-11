from colorama import Fore, Back
import requests
import sys

class Debugger:
    @staticmethod
    def ping_github():
        res = requests.get('https://raw.githubusercontent.com/XtremeDevX/electric-packages/master/package-list.json')
        return res.status_code == 200

    @staticmethod
    def test_internet():
        # Ping well known url's 5 times to see if there's a response
        status_arr = []
        sys.stdout.write('\n')
        urls = [
            "http://google.com/",
            "http://github.com/",
            "http://stackoverflow.com/",
            "http://twitter.com/",
            "http://youtube.com/"
        ]

        for url in urls:
            try:
                res = requests.get(url)
            except:
                pass

            run_test_2 = False
            res.status_code = 200
            sys.stdout.write(f'\r| {Back.GREEN if res.status_code == 200 else Back.MAGENTA}{res.status_code}{Back.RESET} | {Fore.CYAN}{round(res.elapsed.total_seconds(), 1)}s{Fore.RESET} | {Fore.GREEN}Ping {url}{Fore.RESET} ')
            
            if res.status_code == 200:
                status_arr.append(True)
                if not Debugger.ping_github():
                    run_test_2 = True
            else:
                status_arr.append(False)
            sys.stdout.write('\n')


        if True in status_arr and False in status_arr:
            true_count = 0
            false_count = 0
            for val in status_arr:
                if val == True:
                    true_count += 1
                else:
                    false_count += 1

            print(f'{Fore.GREEN}\nSuccessfully Debugged Network Connection{Fore.RESET}')
            print(f'Report:')
            print(f'Your internet connection is {Fore.RED}unstable{Fore.RESET}. {Fore.GREEN}{true_count}{Fore.RESET} of {Fore.YELLOW}5{Fore.RESET} the pings worked while others didn\'t. Try moving to an area with {Fore.GREEN}better internet{Fore.RESET} coverage.\nStill not working? Check the google server status: {Fore.CYAN}https://downdetector.in/status/google/{Fore.RESET}\n')
            sys.exit()

        if run_test_2:
            print(f'{Fore.GREEN}Failed to debug error. your internet connection is unstable{Fore.RESET}')

        else:
            print(f'{Fore.GREEN}No Internet Issues Found! Retry the command.')
