from appJar import *
import subprocess
app = gui("Package downloader", "500x200")
app.setBg("#bd93f9")
app.setFont(18)

def press(button):
    if button == "Cancel":
        app.stop()
    if button == 'Uninstall':
        pkg = app.getEntry("Package Name  ")
        proc = subprocess.Popen(f'electric uninstall {pkg}')
    else:
        pkg = app.getEntry("Package Name  ")
        proc = subprocess.Popen(f'electric install {pkg}')

    output, err = proc.communicate()
    
app.addLabel("title", "Installer GUI")
app.addLabelEntry("Package Name  ")
app.addButtons(["Install", "Uninstall", "Cancel"], press)

app.go()