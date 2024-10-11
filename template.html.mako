<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sonar Report</title>
    <!-- Compiled and minified CSS -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">
    <!-- Compiled and minified JavaScript -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>
    <style>
        .highlighted {
            background-color: rgba(236, 45, 45, 0.8);
        }
        details {
            margin-bottom: 1em;
        }
        summary {
            font-weight: bold;
            cursor: pointer;
        }
        pre {
            background: #2d2d2d;
            color: white;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="center-align">Sonar Report</h1>
        <ul class="collection">
            % for file_path, highlighted_content in files.items():
            <li class="collection-item">
                <details>
                    <summary class="collection-header">${file_path}</summary>
                    <pre><code class="language-python">${highlighted_content | n}</code></pre>
                </details>
            </li>
            % endfor
        </ul>
    </div>
</body>
</html>