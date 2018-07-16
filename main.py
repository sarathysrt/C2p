from flask import Flask
from flask import request, jsonify
import pandas as pd
import numpy as np
import C2P_Core as Dm
import json

app = Flask(__name__)

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.route('/postjson', methods = ['POST'])
def postJsonHandler():
    print (request.is_json)
    content = request.get_json()
    data = pd.io.json.json_normalize(content)
    #data.columns=['Record']#['Time','Record']
    # Peak points
    data=np.array(data)
    aDict=Dm.Get_PQRS(data)
    #print (type(content))
    return jsonify(content)#json.dumps(aDict)#jsonify(content)

if __name__ == '__main__':
  app.run()
