def index_html(api_root):
    return (
        """<!DOCTYPE html>
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
            max-width: 1000px;
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
        .image-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 20px;
        }
        .image-container img, .image-container .svg-container {
            margin: 0 10px;
            display: block;
        }
        #result {
            margin-top: 20px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            background-color: #fafafa;
            position: relative;
            font-family: monospace, 'Consolas', 'Courier New', Courier;
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
        #error-message {
            color: red;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Typress: Typst Math Expressions OCR</h1>
        <input type="file" id="file-input" accept="image/*">
        <div id="result" onclick="copyToClipboard()">
            <span id="copy-msg">Copied!</span>
            <p id="result-text">Upload or paste an image to see the result here...</p>
        </div>
        <div class="image-container">
            <img id="uploaded-image" src="" alt="Uploaded Image" style="display:none;">
            <div id="formula-render" class="svg-container"></div>
        </div>
        <div id="error-message"></div>
    </div>
    <script type="module" src="https://cdn.jsdelivr.net/npm/@myriaddreamin/typst.ts/dist/esm/contrib/all-in-one-lite.bundle.js" id="typst"></script>
    <script>
        const API_ROOT = '"""
        + api_root
        + """';
        let typstInitialized = false;

        async function initializeTypst() {
            if (!typstInitialized) {
                $typst.setCompilerInitOptions({
                    getModule: () =>
                        'https://cdn.jsdelivr.net/npm/@myriaddreamin/typst-ts-web-compiler/pkg/typst_ts_web_compiler_bg.wasm',
                });
                $typst.setRendererInitOptions({
                    getModule: () =>
                        'https://cdn.jsdelivr.net/npm/@myriaddreamin/typst-ts-renderer/pkg/typst_ts_renderer_bg.wasm',
                });
                typstInitialized = true;
            }
        }

        document.addEventListener('DOMContentLoaded', (event) => {
            initializeTypst();
        });
        
        document.getElementById('file-input').addEventListener('change', async (event) => {
            const file = event.target.files[0];
            if (file) {
                displayImage(file);
                await recognizeImage(file);
            }
        });

        document.addEventListener('paste', async (event) => {
            const items = (event.clipboardData || window.clipboardData).items;
            for (let i = 0; i < items.length; i++) {
                if (items[i].type.indexOf('image') !== -1) {
                    const file = items[i].getAsFile();
                    if (file) {
                        displayImage(file);
                        await recognizeImage(file);
                    }
                }
            }
        });

        function displayImage(file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = document.getElementById('uploaded-image');
                img.src = e.target.result;
                img.style.display = 'block';
                adjustLayout();
            };
            reader.readAsDataURL(file);
        }

        async function recognizeImage(file) {
            const formData = new FormData();
            formData.append('image', file);

            try {
                const response = await fetch(`${API_ROOT}/api/formula`, {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                if ("formula" in data) {
                    document.getElementById('result-text').textContent = data.formula;
                    await renderFormula(data.formula);
                } else {
                    showError(data.error || 'Invalid response from server.');
                }
            } catch (error) {
                showError('An error occurred.');
            }
        }

        async function renderFormula(formula) {
            try {
                await initializeTypst();

                const svg = await $typst.svg({ mainContent: 
`#set page(width: auto, height: auto, margin: (x: 5pt, y: 5pt))
//#show math.equation: set text(26pt)
$ ${formula} $` 
                });
                console.log(`rendered! SvgElement { len: ${svg.length} }`);
                const renderDiv = document.getElementById('formula-render');
                renderDiv.innerHTML = svg;
                renderDiv.style.display = 'block';
                document.getElementById('error-message').textContent = '';
                adjustLayout();
            } catch (error) {
                showError(`Error rendering formula: ${error}`);
            }
        }

        function showError(message) {
            document.getElementById('error-message').textContent = message;
        }

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

        function adjustLayout() {
            const img = document.getElementById('uploaded-image');
            const svgContainer = document.getElementById('formula-render');
            const container = document.querySelector('.image-container');

            if (img.style.display === 'none' || svgContainer.style.display === 'none') {
                return;
            }

            const imgHeight = img.naturalHeight;
            const imgWidth = img.naturalWidth;
            
            const containerWidth = container.clientWidth;

            const svgElement = svgContainer.querySelector('svg');
            if (!svgElement) return;
            
            const svgViewBox = svgElement.viewBox.baseVal;
            const svgAspectRatio = svgViewBox.width / svgViewBox.height;

            const svgHeight = imgHeight;
            const svgWidth = svgHeight * svgAspectRatio;

            svgElement.setAttribute('height', svgHeight);
            svgElement.setAttribute('width', svgWidth);

            const totalWidth = imgWidth + svgWidth + 20;

            if (totalWidth <= containerWidth) {
                img.style.height = `${imgHeight}px`;
                img.style.width = `${imgWidth}px`;

                svgElement.setAttribute('height', svgHeight);
                svgElement.setAttribute('width', svgWidth);

                img.style.maxWidth = 'none';
                svgContainer.style.maxWidth = 'none';

                container.style.flexDirection = 'row';
                container.style.justifyContent = 'center';
            } else {
                const scale = containerWidth / totalWidth;

                const newImgWidth = imgWidth * scale;
                const newSvgWidth = svgWidth * scale;

                img.style.height = `${imgHeight * scale}px`;
                img.style.width = `${newImgWidth}px`;

                svgElement.setAttribute('height', svgHeight * scale);
                svgElement.setAttribute('width', newSvgWidth);

                container.style.flexDirection = 'row';
                container.style.justifyContent = 'center';

                img.style.maxWidth = '50%';
                svgContainer.style.maxWidth = '50%';
            }
        }
    </script>
</body>
</html>
"""
    )