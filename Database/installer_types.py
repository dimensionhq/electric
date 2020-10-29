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
    InstallShield = {}
    Ghost = {}
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
    Wise = {}
