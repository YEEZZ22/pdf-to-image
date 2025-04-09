import os
import zipfile
import uuid
from flask import Flask, request, render_template_string, send_file, redirect, url_for
from pdf2image import convert_from_path
from datetime import datetime

# Poppler 路徑（請依你的電腦調整）
POPPLER_PATH = r"D:/User/user/Release-24.08.0-0/poppler-24.08.0/Library/bin"

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <title>PDF 圖片擷取器</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container py-5">
        <h2 class="mb-4 text-center">📄 PDF 每頁轉圖片工具</h2>
        {% if message %}
            <div class="alert alert-{{ 'success' if success else 'danger' }}">{{ message }}</div>
        {% endif %}
        <form method="POST" enctype="multipart/form-data">
            <div class="mb-3">
                <label for="pdf" class="form-label">選擇 PDF 檔案：</label>
                <input type="file" class="form-control" name="pdf" accept="application/pdf" required>
            </div>
            <button type="submit" class="btn btn-primary">開始轉換</button>
        </form>
        {% if download_url %}
            <hr>
            <p>✅ 轉換完成：<a href="{{ download_url }}" class="btn btn-success">下載圖片 ZIP</a></p>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def upload():
    message = None
    success = False
    download_url = None

    if request.method == 'POST':
        pdf_file = request.files.get('pdf')
        if pdf_file:
            try:
                # 儲存上傳的 PDF
                session_id = uuid.uuid4().hex
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{session_id}_{timestamp}.pdf"
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                pdf_file.save(save_path)

                # 建立輸出圖片資料夾
                output_path = os.path.join(OUTPUT_FOLDER, session_id)
                os.makedirs(output_path, exist_ok=True)

                # PDF 轉圖片
                images = convert_from_path(save_path, poppler_path=POPPLER_PATH)
                for i, img in enumerate(images):
                    img.save(os.path.join(output_path, f"page_{i+1}.png"))

                # 壓縮成 ZIP
                zip_path = os.path.join(OUTPUT_FOLDER, f"{session_id}.zip")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for img_name in os.listdir(output_path):
                        img_path = os.path.join(output_path, img_name)
                        zipf.write(img_path, arcname=img_name)

                download_url = url_for('download_file', filename=f"{session_id}.zip")
                message = "轉換成功！"
                success = True

            except Exception as e:
                message = f"轉換過程中發生錯誤：{e}"
                success = False

    return render_template_string(HTML_TEMPLATE, message=message, success=success, download_url=download_url)

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
