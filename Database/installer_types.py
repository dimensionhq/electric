import enum


class Installer(enum.Enum):
    NullSoft = {
        "install-switches":
        [
            '/S'
        ],
        "uninstall-switches": [
            '/S'
        ],
        "dir-spec": "/D="
    }
    InnoSetup = {
        "install-switches":
        [
            '/SP-',
            '/VERYSILENT',
            '/SUPPRESSMSGBOXES',
            '/NOCANCEL',
            '/NORESTART',
            '/FORCECLOSEAPPLICATIONS',
        ],
        "uninstall-switches": [
            '/VERYSILENT',
            '/SUPPRESSMSGBOXES',
            '/NORESTART',
        ],
        "dir-spec": "/DIR="
    }
    InstallAware = {
        "install-switches":
        [
            '/s'
        ],
        "uninstall-switches": [
            '/s'
        ],
        "dir-spec": ""
    }
    #TODO: Fix For InstallShield
    InstallShield = {
        "install-switches":
            [
                '/s',
                '/v',

            ],
        "uninstall-switches": [
            '/s',
            '/uninst'
        ],
        "dir-spec": ""
    }
    Ghost = {
        "install-switches":
            [
                '-s'
            ],
        "uninstall-switches": [
                '-u',
                '-s'
            ],
        "dir-spec": ""
    }
    Squirrel = {
        "install-switches":
        [
            '-s'
        ],
        # Can move the atom file to a different directory : (
        "uninstall-switches":
        [
            '-s'
        ],
        "dir-spec": "",
    }
    Wise = {
        "install-switches":
            [
                '/S'
            ],
        "uninstall-switches":
            [
                '/S'
            ],
        "dir-spec": "",
    }
    QtInstaller = {
        "install-switches": [],
        "uninstall-switches": [],
        "dir-spec": "",
    }
    BitRockInstaller = {
        "install-switches": [
            '--mode unattended'
        ],
        "uninstall-switches": [
            '--mode unattended',
            '--unattendedmodeui none'
        ],
        "dir-spec": "",
    }
    CustomInstaller = {
        "install-switches": [
            '/S'
        ],
        "uninstall-switches": [
            '/S',
        ],
        "dir-spec": "",
    }
    InstallForJInstaller = {
        "install-switches": [
            '-q'
        ],
        "uninstall-switches": [
            '/S',
        ],
        "dir-spec": "-dir ",
    }
    PackageForTheWebInstaller = {
        "install-switches": [
            '/S'
        ],
        "uninstall-switches": [
            '/S',
        ],
        "dir-spec": "",
    }
    Msi = {
        "install-switches": [
            '/passive',
            '/quiet',
            '/norestart'
        ],
        "uninstall-switches": [
            '/passive',
            '/quiet',
            '/norestart'
        ],
        "dir-spec": "TARGETDIR=",
    }
    WindowsUpdateInstaller = {
        "install-switches": [
            '/norestart',
            '/quiet'
        ]
    }

