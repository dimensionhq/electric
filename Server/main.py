from flask import Flask
from flask_restful import Api, Resource
from flask import send_file, jsonify
from getpass import getuser
from sys import platform
import json

# Create Flask App
app = Flask(__name__)
# Create API
api = Api(app)


files = {
	"sublime-text-3.json" :
	{
		"package-name": "Sublime Text 3",
		"win32": "https://download.sublimetext.com/Sublime%20Text%20Build%203211%20Setup.exe",
		"win64": "https://download.sublimetext.com/Sublime%20Text%20Build%203211%20x64%20Setup.exe",
		"darwin": "https://download.sublimetext.com/Sublime%20Text%20Build%203211.dmg",
		"debian": "https://download.sublimetext.com/sublime_text_3_build_3211_x64.tar.bz2",
		"source": "https://www.google.com",
		"type": ".exe",
		"switches": ["/VERYSILENT", "/NORESTART"]
	},
	"atom.json":
	{
		"package-name": "Atom",
		"win32": "https://atom.io/download/windows",
		"win64": "https://atom.io/download/windows_x64",
		"darwin": "https://atom.io/download/macos",
		"debian": "https://github.com/atom/atom/releases/download/v1.51.0/atom-amd64.deb",
		"source": "https://atom.io/",
		"type": ".exe",
		"switches": ["--silent"]
	},
	"vscode.json":
	{
		"package-name": "Visual Studio Code",
		"win32": "https://aka.ms/win32-x64-user-stable",
		"win64": "https://aka.ms/win32-x64-user-stable",
		"darwin": "https://go.microsoft.com/fwlink/?LinkID=620882",
		"debian": "https://go.microsoft.com/fwlink/?LinkID=760868",
		"source": "https://code.visualstudio.com/",
		"type": ".exe",
		"switches": ["/VERYSILENT", "/NORESTART", "/MERGETASKS=!runcode"]
	},
	"android-studio.json":
	{
		"package-name": "Android Studio",
		"win32": "",
		"win64": "https://redirector.gvt1.com/edgedl/android/studio/install/4.0.2.0/android-studio-ide-193.6821437-windows.exe",
		"darwin": "https://redirector.gvt1.com/edgedl/android/studio/install/4.0.2.0/android-studio-ide-193.6821437-mac.dmg",
		"debian": "https://redirector.gvt1.com/edgedl/android/studio/ide-zips/4.0.2.0/android-studio-ide-193.6821437-linux.tar.gz",
		"source": "https://developer.android.com/",
		"type": ".exe",
		"switches": ["/S"]
	},
	"virtualbox.json":
	{
		"package-name": "VirtualBox",
		"win32": "https://download.virtualbox.org/virtualbox/6.1.14/VirtualBox-6.1.14-140239-Win.exe",
		"win64": "https://download.virtualbox.org/virtualbox/6.1.14/VirtualBox-6.1.14-140239-Win.exe",
		"darwin": "https://download.virtualbox.org/virtualbox/6.1.14/VirtualBox-6.1.14-140239-OSX.dmg",
		"debian": "https://download.virtualbox.org/virtualbox/6.1.14/virtualbox-6.1_6.1.14-140239~Ubuntu~eoan_amd64.deb",
		"source": "https://www.virtualbox.org/wiki/Downloads",
		"type": ".exe",
		"switches": ["--silent"]
	},
	"blender.json":
	{
		"package-name": "Blender",
		"win32": "https://ftp.nluug.nl/pub/graphics/blender/release/Blender2.90/blender-2.90.1-windows64.msi",
		"win64": "https://ftp.nluug.nl/pub/graphics/blender/release/Blender2.90/blender-2.90.1-windows64.msi",
		"darwin": "https://www.blender.org/download/Blender2.90/blender-2.90.1-macOS.dmg/",
		"debian": "https://www.blender.org/download/Blender2.90/blender-2.90.1-linux64.tar.xz/",
		"source": "https://www.blender.org/",
		"type": ".msi",
		"switches": ["/passive"],
	},
	"ziptest.json":
	{
		"package-name": "Test",
		"win32": "https://az764295.vo.msecnd.net/stable/2af051012b66169dde0c4dfae3f5ef48f787ff69/VSCode-win32-x64-1.49.3.zip",
		"win64": "https://az764295.vo.msecnd.net/stable/2af051012b66169dde0c4dfae3f5ef48f787ff69/VSCode-win32-x64-1.49.3.zip",
		"source": "test.org",
		"type": ".zip",
		"switches": [""],
	}
}

class FileQuery(Resource):
	def get(self, file_name : str):
		# return send_file(f"C:\\Users\\roopa\\Desktop\\Coding\\electric\\Data\\{file_name}.exe", as_attachment=True)
	# def get(self, file_name : str):
		return jsonify(files[file_name + '.json'])


# Adding Page-Link For /rapidquery
api.add_resource(FileQuery, '/rapidquery/<string:file_name>')

if __name__ == "__main__":
	# Debug Is True For Auto-Reload
	app.run(debug=True)

