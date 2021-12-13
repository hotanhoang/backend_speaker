from flask import Flask,request,jsonify
from core.voice_utils import extra_feature
from core.voice_utils import compare_similarity
app = Flask(__name__)
@app.route('/get_feature',methods = ['POST'])
def get_feature():
    if request.method == 'POST':
        file1 = request.files.get('file1')
        print(file1)
        if file1 is None or file1.filename == "":
            return jsonify({'error':'no file'})
        try:
            """
            Main coding
            """
            result = extra_feature(audio=file1)
            data = {'prediction':result}
            return jsonify(data)
        except:
            return jsonify({'error':'error during get feature'})

            
@app.route('/compare',methods = ['POST'])
def compare():
    if request.method == 'POST':
        feature1 = request.files.get('file1')
        print(feature1)
        if feature1 is None or feature1.filename == "":
            return jsonify({'error':'no file'})
        feature2 = request.files.get('file1')
        print(feature2)
        if feature2 is None or feature2.filename == "":
            return jsonify({'eror':'no file'})
        try:
            """
            Main coding
            """
            result = compare_similarity(filename_1=feature1,filename_2=feature2)
            data = {'prediction':result}
            return jsonify(data)
        except:
            return jsonify({'error':'error during compare'})

if __name__ == "__main__":
    app.run(debug=True)