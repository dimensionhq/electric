from appJar import *
import os
app = gui("Package downloader", "400x200")
app.setBg("orange")
app.setFont(18)

def press(button):
    if button == "Cancel":
        app.stop()
    else:
      pkg = app.getEntry("Package Name")
      os.system('electric install ' + pkg)
app.addLabel("title", "Installer GUI")
app.addLabelEntry("Package Name")
app.addButtons(["Get", "Cancel"], press)

app.go()
