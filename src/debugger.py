from timeit import default_timer as timer
from colorama import Fore, Back
from halo import Halo
import requests
import sys


class Debugger:
    @staticmethod
    def ping_github():
        try:
            res = requests.get(
                'http://electric-package-manager-api.herokuapp.com/package-list')
        except err:
            res = requests.Response()
            res.status_code = 404
        return res.status_code == 200

    @staticmethod
    def test_internet():
        from subprocess import Popen, PIPE

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
            start = timer()
            try:
                res = requests.get(url)
            except:
                res = requests.Response()
                res.status_code = 404
            end = timer()

            run_test_2 = False

            sys.stdout.write(
                f'\r| {Back.GREEN if res.status_code == 200 else Back.MAGENTA}{res.status_code}{Back.RESET} | {Fore.LIGHTCYAN_EX}{round(end - start, 1)}s{Fore.RESET} | {Fore.LIGHTGREEN_EX}Ping {url}{Fore.RESET} ')

            if res.status_code == 200:
                status_arr.append(True)
                if Debugger.ping_github() == False:
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

            print(
                f'{Fore.LIGHTGREEN_EX}\nSuccessfully Debugged Network Connection{Fore.RESET}')
            print(f'Report:')
            print(f'Your internet connection is {Fore.LIGHTRED_EX}unstable{Fore.RESET}. {Fore.LIGHTGREEN_EX}{true_count}{Fore.RESET} of {Fore.LIGHTYELLOW_EX}5{Fore.RESET} the pings worked while others didn\'t. Try moving to an area with {Fore.LIGHTGREEN_EX}better internet{Fore.RESET} coverage.\nStill not working? Check the google server status: {Fore.LIGHTCYAN_EX}https://downdetector.in/status/google/{Fore.RESET}\n')
            sys.exit()
        elif run_test_2:
            print(
                f' {Fore.LIGHTGREEN_EX}0{Fore.RESET}{Fore.LIGHTRED_EX} of {Fore.RESET}{Fore.LIGHTYELLOW_EX}5{Fore.RESET}{Fore.LIGHTRED_EX} pings successfully went through.{Fore.RESET} Failed to debug error. Your internet connection is unstable.')

        elif False in status_arr:
            print(
                f' {Fore.LIGHTGREEN_EX}0{Fore.RESET}{Fore.LIGHTRED_EX} of {Fore.RESET}{Fore.LIGHTYELLOW_EX}5{Fore.RESET}{Fore.LIGHTRED_EX} pings successfully went through.{Fore.RESET} Debugging error. Your internet connection is unstable.')
            with Halo('Renewing IP Configuration') as h:
                proc = Popen('ipconfig /renew', stdin=PIPE,
                             stdout=PIPE, stderr=PIPE, shell=True)
                output, _ = proc.communicate()
                output = output.decode('utf-8')

                if 'while it has its media disconnected' in output:
                    h.stop()
                    print(
                        f'{Fore.LIGHTGREEN_EX}\nSuccessfully Debugged Network Connection{Fore.RESET}')
                    print('Report:')
                    print(
                        f'You might not have {Fore.LIGHTCYAN_EX}selected{Fore.RESET} any internet to connect to. No external network connections have been {Fore.LIGHTYELLOW_EX}detected{Fore.RESET} as they are {Fore.LIGHTRED_EX}disconnected{Fore.RESET}.\nPlease make sure you {Fore.LIGHTGREEN_EX}connect{Fore.RESET} them and then {Fore.LIGHTMAGENTA_EX}try the command again.{Fore.RESET}')
                elif (
                    'while it has its media connected' in output
                    and 'No operation can be performed on Wi-Fi' not in output
                ):
                    h.stop()
                    print(
                        f'{Fore.LIGHTGREEN_EX}\nSuccessfully Debugged Network Connection{Fore.RESET}')
                    print('Report:')
                    print(
                        f'You might not have {Fore.LIGHTCYAN_EX}plugged in{Fore.RESET} any ethernet cable to connect to. No external network connections have been {Fore.LIGHTYELLOW_EX}detected{Fore.RESET} as they are {Fore.LIGHTRED_EX}disconnected{Fore.RESET}.\nPlease make sure you {Fore.LIGHTGREEN_EX}connect{Fore.RESET} the ethernet cable {Fore.LIGHTMAGENTA_EX}try the command again.{Fore.RESET}')

        elif status_arr == [True, True, True, True, True]:
            print(
                f'{Fore.LIGHTGREEN_EX}No Internet Issues Found. Retry The Command!{Fore.RESET}')
