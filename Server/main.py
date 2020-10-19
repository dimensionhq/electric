from flask import Flask
from flask_restful import Api, Resource
from flask import jsonify
import json
from getpass import getuser

FILE_PATH = f'C:\\Users\\{getuser()}\\Desktop\\electric\\Server\\Packages\\'

# Create Flask App
app = Flask(__name__)
# Create API
api = Api(app)

class FileQuery(Resource):
	def get(self, file_name : str):
<<<<<<< HEAD
		data = None
		with open(FILE_PATH + file_name + '.json') as f:
			data = f.read()
		return jsonify(data)

=======
		with open('packages.json') as file:
			files = json.loads(file.read())
		if file_name == 'all':
			return jsonify(files)

		return jsonify(files[file_name + '.json'])
>>>>>>> 7753ad477796971e396b571e8ef8baceaad71e8d



# Adding Page-Link For /rapidquery
api.add_resource(FileQuery, '/rapidquery/<string:file_name>')

if __name__ == "__main__":
	# Debug Is True For Auto-Reload
	app.run(debug=True)
