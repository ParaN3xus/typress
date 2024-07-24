def index_html(api_root="http://127.0.0.1:5000/"):
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Typress Formula OCR</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            color: #333;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }
        h1 {
            text-align: center;
            margin-bottom: 20px;
        }
        input[type="file"] {
            display: block;
            margin: 20px auto;
        }
        #result {
            margin-top: 20px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            background-color: #fafafa;
            position: relative;
        }
        #result:hover {
            cursor: pointer;
            background-color: #f0f0f0;
        }
        #copy-msg {
            position: absolute;
            top: -20px;
            right: 10px;
            background-color: #4caf50;
            color: #fff;
            padding: 5px 10px;
            border-radius: 4px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Typress Formula OCR</h1>
        <input type="file" id="file-input" accept="image/*">
        <div id="result" onclick="copyToClipboard()">
            <span id="copy-msg">Copied!</span>
            <p id="result-text">Upload an image to see the result here...</p>
        </div>
    </div>
    <script>
        const API_ROOT = '""" + api_root + """';

        document.getElementById('file-input').addEventListener('change', async (event) => {
            const file = event.target.files[0];
            if (file) {
                const formData = new FormData();
                formData.append('image', file);

                try {
                    const response = await fetch(`${API_ROOT}/api/formula`, {
                        method: 'POST',
                        body: formData
                    });
                    const data = await response.json();
                    document.getElementById('result-text').textContent = data.formula || 'Failed to recognize the formula.';
                } catch (error) {
                    document.getElementById('result-text').textContent = 'An error occurred.';
                }
            }
        });

        function copyToClipboard() {
            const resultText = document.getElementById('result-text').textContent;
            navigator.clipboard.writeText(resultText).then(() => {
                const copyMsg = document.getElementById('copy-msg');
                copyMsg.style.display = 'block';
                setTimeout(() => {
                    copyMsg.style.display = 'none';
                }, 2000);
            });
        }
    </script>
</body>
</html>
"""
