from flask import Flask
from flask_restful import Api, Resource
from flask import jsonify
import json

# Create Flask App
app = Flask(__name__)
# Create API
api = Api(app)

class FileQuery(Resource):
	def get(self, file_name : str):
		with open('packages.json') as file:
			files = json.loads(file.read())
		if file_name == 'all':
			return jsonify(files)
		
		return jsonify(files[file_name + '.json'])


# Adding Page-Link For /rapidquery
api.add_resource(FileQuery, '/rapidquery/<string:file_name>')

if __name__ == "__main__":
	# Debug Is True For Auto-Reload
	app.run(debug=True)