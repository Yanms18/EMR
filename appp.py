import csv
import io
import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from flask import Flask, request, render_template, jsonify
from patient0 import create_patient0
from appointment import search_patient_by_name, search_practitioner_by_name, create_appointment

app = Flask(__name__)

# Patient data model
@dataclass
class Patient:
    firstname: str
    lastname: str
    age: int
    sex: str
    gender: str
    practitioner_name: str
    appointment_date: str
    appointment_time: str
    reason_text: str
    appointment_type_display: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'firstname': self.firstname,
            'lastname': self.lastname,
            'age': self.age,
            'sex': self.sex,
            'gender': self.gender,
            'practitioner_name': self.practitioner_name,
            'appointment_date': self.appointment_date,
            'appointment_time': self.appointment_time,
            'reason_text': self.reason_text,
            'appointment_type_display': self.appointment_type_display
        }

def parse_csv(file_content: str) -> List[Patient]:
    patients = []
    csv_reader = csv.DictReader(io.StringIO(file_content))
    for row in csv_reader:
        patient = Patient(
            firstname=row.get('firstname', ''),
            lastname=row.get('lastname', ''),
            age=int(row.get('age', 0)) if row.get('age') else 0,
            sex=row.get('sex', ''),
            gender=row.get('gender', ''),
            practitioner_name=row.get('practitioner_name', ''),
            appointment_date=row.get('appointment_date', ''),
            appointment_time=row.get('appointment_time', ''),
            reason_text=row.get('reason_text', ''),
            appointment_type_display=row.get('appointment_type_display', '')
        )
        patients.append(patient)
    return patients

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_csv():
    if 'csv_file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['csv_file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if file:
        content = file.read().decode('utf-8')
        patients = parse_csv(content)
        
        result = []
        for patient in patients:
            # Create patient
            patient_response = create_patient0(patient.firstname, patient.lastname, patient.age, patient.sex, patient.gender)
            patient_name = f"{patient.firstname} {patient.lastname}"
            
            # Combine date and time into a single datetime object
            start_datetime = datetime.strptime(f"{patient.appointment_date}T{patient.appointment_time}", "%Y-%m-%dT%H:%M:%S")
            end_datetime = start_datetime + timedelta(hours=1)
            start_time = start_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            end_time = end_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            
            # Search for the patient and practitioner ID based on their name
            try:
                patient_id = search_patient_by_name(patient_name)
            except Exception as e:
                patient_id = None
            
            try:
                practitioner_id = search_practitioner_by_name(patient.practitioner_name)
            except Exception as e:
                practitioner_id = None
            
            if not practitioner_id:
                return jsonify({'error': f"Failed to find practitioner: {patient.practitioner_name}"})
            
            # Create appointment
            appointment_response = create_appointment(
                patient_id, practitioner_id, patient.reason_text, start_time, end_time, patient.appointment_type_display
            )
            
            result.append({
                'patient_response': patient_response,
                'appointment_response': appointment_response
            })
        
        return jsonify(result)

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
    <title>XPC Medical Data Processor</title>
</head>
<body>
    <div class="container">
        <h1>Upload CSV File</h1>
        <form action="/process" method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label for="csv_file">CSV File:</label>
                <input type="file" id="csv_file" name="csv_file" accept=".csv">
            </div>
            <button type="submit">Upload and Process</button>
        </form>
        <div id="result"></div>
    </div>
    <script>
        document.querySelector('form').addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(event.target);
            fetch('/process', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = JSON.stringify(data, null, 2);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    </script>
</body>
</html>
        """)

if __name__ == '__main__':
    create_template()
    app.run(debug=True)