import csv
import io
import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# Data model definition
@dataclass
class Person:
    id: int
    name: str
    age: int
    email: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Person':
        return cls(
            id=int(data.get('id', 0)),
            name=data.get('name', ''),
            age=int(data.get('age', 0)),
            email=data.get('email')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'email': self.email
        }

# Function to parse CSV content
def parse_csv_content(content: str) -> List[Person]:
    people = []
    csv_io = io.StringIO(content)
    reader = csv.DictReader(csv_io)
    
    for row in reader:
        try:
            person = Person.from_dict(row)
            people.append(person)
        except (ValueError, KeyError) as e:
            # Handle parsing errors
            print(f"Error parsing row {row}: {e}")
    
    return people

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_csv():
    if 'csv_file' in request.files:
        file = request.files['csv_file']
        content = file.read().decode('utf-8')
    else:
        content = request.form.get('csv_content', '')
    
    if not content:
        return jsonify({'error': 'No CSV data provided'})
    
    try:
        people = parse_csv_content(content)
        result = [p.to_dict() for p in people]
        return jsonify({'data': result, 'count': len(result)})
    except Exception as e:
        return jsonify({'error': str(e)})

# Create templates directory and HTML file
def create_template():
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    with open('templates/index.html', 'w') as f:
        f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSV to Data Model Converter</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            color: #333;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .tab {
            overflow: hidden;
            border: 1px solid #ccc;
            background-color: #f1f1f1;
        }
        .tab button {
            background-color: inherit;
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 10px 16px;
            transition: 0.3s;
        }
        .tab button:hover {
            background-color: #ddd;
        }
        .tab button.active {
            background-color: #ccc;
        }
        .tabcontent {
            display: none;
            padding: 6px 12px;
            border: 1px solid #ccc;
            border-top: none;
        }
        textarea, input[type="file"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        textarea {
            height: 150px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        #result {
            margin-top: 20px;
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 4px;
            background-color: #f9f9f9;
            display: none;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .error {
            color: red;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>CSV to Data Model Converter</h1>
        <p>Convert CSV data to a structured Person data model.</p>
        
        <div class="tab">
            <button class="tablinks active" onclick="openTab(event, 'upload')">Upload CSV</button>
            <button class="tablinks" onclick="openTab(event, 'paste')">Paste CSV</button>
        </div>
        
        <div id="upload" class="tabcontent" style="display: block;">
            <form id="uploadForm">
                <div class="form-group">
                    <label for="csv_file">Upload CSV File:</label>
                    <input type="file" id="csv_file" name="csv_file" accept=".csv">
                </div>
                <button type="submit">Process CSV</button>
            </form>
        </div>
        
        <div id="paste" class="tabcontent">
            <form id="pasteForm">
                <div class="form-group">
                    <label for="csv_content">Paste CSV Content:</label>
                    <textarea id="csv_content" name="csv_content" placeholder="id,name,age,email
1,John Doe,30,john@example.com
2,Jane Smith,25,jane@example.com"></textarea>
                </div>
                <button type="submit">Process CSV</button>
            </form>
        </div>
        
        <div id="result">
            <h2>Results</h2>
            <div id="resultContent"></div>
        </div>
    </div>

    <script>
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }
        
        document.getElementById('uploadForm').addEventListener('submit', function(e) {
            e.preventDefault();
            processForm(new FormData(this));
        });
        
        document.getElementById('pasteForm').addEventListener('submit', function(e) {
            e.preventDefault();
            processForm(new FormData(this));
        });
        
        function processForm(formData) {
            fetch('/process', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('result');
                const resultContent = document.getElementById('resultContent');
                resultDiv.style.display = 'block';
                
                if (data.error) {
                    resultContent.innerHTML = `<p class="error">${data.error}</p>`;
                    return;
                }
                
                if (data.data && data.data.length > 0) {
                    let tableHTML = `<p>Successfully processed ${data.count} records:</p>
                                    <table>
                                        <thead>
                                            <tr>`;
                    
                    // Generate table headers
                    const headers = Object.keys(data.data[0]);
                    headers.forEach(header => {
                        tableHTML += `<th>${header}</th>`;
                    });
                    
                    tableHTML += `</tr>
                                </thead>
                                <tbody>`;
                    
                    // Generate table rows
                    data.data.forEach(item => {
                        tableHTML += `<tr>`;
                        headers.forEach(header => {
                            tableHTML += `<td>${item[header] !== null ? item[header] : ''}</td>`;
                        });
                        tableHTML += `</tr>`;
                    });
                    
                    tableHTML += `</tbody>
                                </table>`;
                    
                    resultContent.innerHTML = tableHTML;
                } else {
                    resultContent.innerHTML = `<p>No data found or CSV format is incorrect.</p>`;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                const resultDiv = document.getElementById('result');
                const resultContent = document.getElementById('resultContent');
                resultDiv.style.display = 'block';
                resultContent.innerHTML = `<p class="error">An error occurred: ${error}</p>`;
            });
        }
    </script>
</body>
</html>
        """)

if __name__ == '__main__':
    create_template()
    app.run(debug=True)