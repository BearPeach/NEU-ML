from flask import Flask, request, send_file, jsonify, render_template_string
import os
from werkzeug.utils import secure_filename
from car_detector import detect_car

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>汽车检测前端</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px; 
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h2 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .upload-form {
            text-align: center;
            margin-bottom: 20px;
        }
        .file-input {
            margin: 10px;
            padding: 10px;
        }
        .submit-btn {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        .submit-btn:hover {
            background-color: #0056b3;
        }
        .loading {
            text-align: center;
            color: #666;
            font-style: italic;
            margin: 20px 0;
        }
        .result-img {
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-top: 20px;
        }
        .error {
            color: red;
            text-align: center;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>🚗 汽车检测系统</h2>
        <form id="upload-form" class="upload-form">
            <input type="file" id="file-input" name="file" accept="image/*" required class="file-input" />
            <br>
            <button type="submit" class="submit-btn">上传并检测</button>
        </form>
        <div id="loading" class="loading" style="display:none;">🔍 检测中，请稍候...</div>
        <div id="error" class="error" style="display:none;"></div>
        <div id="result" style="text-align: center;">
            <img id="result-img" src="" alt="检测结果" class="result-img" style="display:none;" />
        </div>
    </div>
    
    <script>
        const form = document.getElementById('upload-form');
        const loading = document.getElementById('loading');
        const resultImg = document.getElementById('result-img');
        const errorDiv = document.getElementById('error');
        
        form.onsubmit = async function(e) {
            e.preventDefault();
            loading.style.display = 'block';
            resultImg.style.display = 'none';
            errorDiv.style.display = 'none';
            
            const fileInput = document.getElementById('file-input');
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            
            try {
                const response = await fetch('/detect', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error('检测失败，请检查图片格式或稍后重试');
                }
                
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                resultImg.src = url;
                resultImg.style.display = 'block';
                
            } catch (err) {
                errorDiv.textContent = '检测失败: ' + err.message;
                errorDiv.style.display = 'block';
            } finally {
                loading.style.display = 'none';
            }
        };
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/detect', methods=['POST'])
def detect():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(RESULT_FOLDER, 'result_' + filename)
    
    file.save(input_path)
    
    try:
        detect_car(input_path, output_path)
        return send_file(output_path, mimetype='image/png')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print(" 汽车检测系统启动中...")
    print(" 请在浏览器中访问: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True) 