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
    first_name: str
    last_name: str
    age: int
    gender: str
    sex: str
    appointment_type: str
    appointment_date: datetime
    appointment_time: datetime
    physician: str
    reason_for_visit: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age,
            'gender': self.gender,
            'sex': self.sex,
            'appointment_type': self.appointment_type,
            'appointment_date': self.appointment_date.strftime('%Y-%m-%d') if isinstance(self.appointment_date, datetime) else self.appointment_date,
            'appointment_time': self.appointment_time.strftime('%H:%M:%S') if isinstance(self.appointment_time, datetime) else self.appointment_time,
            'physician': self.physician,
            'reason_for_visit': self.reason_for_visit
        }

def split_name(full_name: str) -> (str, str):
    parts = full_name.split()
    if len(parts) == 2:
        return parts[0], parts[1]
    elif len(parts) > 2:
        return parts[0], ' '.join(parts[1:])
    else:
        return full_name, ''

# Function to parse the CSV file - detects and handles different formats
def parse_medical_csv(file_content: str) -> List[Patient]:
    patients = []
    
    # Read CSV into memory
    csv_io = io.StringIO(file_content)
    reader = list(csv.reader(csv_io))
    
    # If file is empty
    if not reader:
        raise ValueError("CSV file is empty")
    
    # Detect CSV format
    # Format 1: Field names in first column, patients in columns 3+
    # Format 2: Field names in first row, patients in rows 2+
    
    format_type = detect_csv_format(reader)
    
    if format_type == "column_based":
        # Original format: fields in first column
        return parse_column_based_csv(reader)
    else:
        # New format: fields in first row
        return parse_row_based_csv(reader)

def detect_csv_format(reader):
    """
    Detects if the CSV has field names in first column (column-based) or first row (row-based)
    """
    # Check first rows/columns for clues
    if not reader or len(reader) < 2 or len(reader[0]) < 2:
        return "unknown"
    
    # Look at first column for standard field names
    first_column_fields = [row[0].strip().lower() for row in reader if row and len(row) > 0]
    field_name_matches = sum(1 for field in ['name', 'age', 'gender', 'appointment'] if field in first_column_fields)
    
    # Look at first row for standard field names
    first_row_fields = [cell.strip().lower() for cell in reader[0] if cell]
    header_matches = sum(1 for field in ['name', 'age', 'gender', 'appointment'] if field in first_row_fields)
    
    # Decide based on matches
    if field_name_matches >= 3:  # At least 3 field names found in first column
        return "column_based"
    elif header_matches >= 3:  # At least 3 field names found in first row
        return "row_based"
    else:
        # Default to row-based if can't determine
        return "row_based"

def parse_date_time(date_str, time_str):
    """
    Helper function to parse dates and times with multiple format support
    """
    appointment_date = None
    if date_str:
        try:
            # Try multiple date formats
            date_formats = ['%m/%d/%y', '%m/%d/%Y', '%Y-%m-%d']
            for fmt in date_formats:
                try:
                    appointment_date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            if not appointment_date:
                # Just keep as string if parsing fails
                appointment_date = date_str
        except Exception:
            appointment_date = date_str
    
    appointment_time = None
    if time_str:
        try:
            # Try multiple time formats
            time_formats = ['%I:%M %p', '%H:%M:%S %p', '%H:%M:%S', '%H:%M']
            for fmt in time_formats:
                try:
                    appointment_time = datetime.strptime(time_str, fmt)
                    break
                except ValueError:
                    continue
            if not appointment_time:
                # Just keep as string if parsing fails
                appointment_time = time_str
        except Exception:
            appointment_time = time_str
    
    return appointment_date, appointment_time

def parse_column_based_csv(reader):
    """
    Parse CSV where field names are in first column and patient data is in columns
    """
    patients = []
    
    # Extract field names from first column (skipping empty cells)
    field_names = []
    for row in reader:
        if row and row[0].strip():
            field_names.append(row[0].strip())
    
    # Determine how many patients we have (columns with data starting from the 3rd column)
    patient_columns = []
    for col_index in range(2, len(reader[0])):
        # Check if this column has a name (usually in first row with data)
        if any(row[col_index].strip() for row in reader):
            patient_columns.append(col_index)
    
    # Create a patient for each data column
    for col_index in patient_columns:
        patient_data = {}
        
        # Extract data for each field
        for row_index, row in enumerate(reader):
            if row_index < len(field_names) and col_index < len(row):
                field = field_names[row_index].lower().replace(' ', '_')
                patient_data[field] = row[col_index]
        
        try:
            first_name, last_name = split_name(patient_data.get('name', ''))
            # Parse dates and times
            # appointment_date, appointment_time = parse_date_time(
            #     patient_data.get('appointment_date', ''),
            #     patient_data.get('appointment_time', '')
            # )
            
            # Create patient object
            patient = Patient(
                first_name=first_name,
                last_name=last_name,
                age=int(patient_data.get('age', 0)) if patient_data.get('age', '').strip().isdigit() else 0,
                gender=patient_data.get('gender', ''),
                sex=patient_data.get('sex', ''),
                appointment_type=patient_data.get('type_of_appointment', ''),
                appointment_date=patient_data.get('appointment_date', ''),
                appointment_time=patient_data.get('appointment_time', ''),
                physician=patient_data.get('physician', ''),
                reason_for_visit=patient_data.get('reason_for_visit', '')
            )
            
            patients.append(patient)
            
        except Exception as e:
            print(f"Error parsing patient data in column-based format: {e}")
            continue
    
    return patients

def parse_row_based_csv(reader):
    """
    Parse CSV where field names are in first row and each patient is a row
    """
    patients = []
    
    if len(reader) < 2:
        raise ValueError("CSV file doesn't have enough rows")
    
    # Get field names from first row
    headers = [h.strip() for h in reader[0]]
    
    # Process each row (starting from second row)
    for row_index in range(1, len(reader)):
        row = reader[row_index]
        
        # Skip empty rows
        if not any(cell.strip() for cell in row):
            continue
            
        # Map data to field names
        patient_data = {}
        for col_index, header in enumerate(headers):
            if col_index < len(row):
                if header:  # Only process if header exists
                    patient_data[header.lower().replace(' ', '_')] = row[col_index].strip()
        
        try:
            first_name, last_name = split_name(patient_data.get('name', ''))
            # Handle special fields (name, age, type of appointment)
            name = patient_data.get('name', '')
            
            # Age needs to be an integer
            age_str = patient_data.get('age', '0')
            try:
                age = int(age_str)
            except ValueError:
                print(f"Invalid age value: {age_str}, defaulting to 0")
                age = 0
                
            # Parse dates and times
            # appointment_date, appointment_time = parse_date_time(
            #     patient_data.get('appointment_date', ''),
            #     patient_data.get('appointment_time', '')
            # )
            
            # Create patient object
            patient = Patient(
                firstname=first_name,
                lastname=last_name,
                age=age,
                gender=patient_data.get('gender', ''),
                sex=patient_data.get('sex', ''),
                appointment_type=patient_data.get('type_of_appointment', ''),
                 appointment_date=patient_data.get('appointment_date', ''),
                appointment_time=patient_data.get('appointment_time', ''),
                physician=patient_data.get('physician', ''),
                reason_for_visit=patient_data.get('reason_for_visit', '')
            )
            
            patients.append(patient)
            
        except Exception as e:
            print(f"Error parsing patient data in row-based format: {e}")
            continue
    
    return patients

# Mock function to simulate API call (would be replaced with actual API integration)
# def send_to_external_api(patient_data: Dict[str, Any]) -> Dict[str, Any]:
#     # This is where you would call your third-party API
#     # For now, we'll just simulate a successful response
#     return {
#         "success": True,
#         "message": "Patient data successfully sent to external system",
#         "patient_id": f"P{hash(patient_data['first_name']) % 10000}"  # Generate a fake patient ID
#     }

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_csv():
    if 'csv_file' not in request.files:
        return jsonify({'error': 'No file provided'})
    
    file = request.files['csv_file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    
    try:
        content = file.read().decode('utf-8')
        patients = parse_medical_csv(content)
        
        if not patients:
            return jsonify({'error': 'No patient data found in CSV'})
        
        result = []
        for patient in patients:
            patient_dict = patient.to_dict()
            
            firstname = patient.first_name
            lastname = patient.last_name
            age = 97
            sex = patient.sex  # Options: F, M, OTH, UNK
            gender = patient.gender  # Options: female, male, other, unknown

            # Create patient
            patient_response = create_patient0(firstname, lastname, age, sex, gender)

            # Input the appointment details
            patient_name = f"{patient.first_name} {patient.last_name}"
            practitioner_name = patient.physician
            appointment_date = patient.appointment_date  # YYYY-MM-DD format
            appointment_time = patient.appointment_time    # HH:MM:SS format
            reason_text = patient.reason_for_visit
            appointment_type_display = patient.appointment_type  # Options: Home Visit, Telemedicine, Office Visit, Lab Visit, Phone Call
            
            # Simulate API call (if send_api is checked)
            if request.form.get('send_api') == 'true':
                # Combine date and time into a single datetime object
                start_datetime = datetime.strptime(f"{appointment_date}T{appointment_time}", "%Y-%m-%dT%H:%M:%S")

                # Calculate end time by adding 1 hour to start time
                end_datetime = start_datetime + timedelta(hours=1)

                # Format start and end times in the required format
                start_time = start_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                end_time = end_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z")

                # Search for the practitioner ID based on their name
                try:
                    patient_id = search_patient_by_name(patient_name)
                    print(f"Found patient ID: {patient_id} for patient name: {patient_name}")
                except Exception as e:
                    print(f"Error finding patient: {e}")
                    patient_id = None

                try:
                    practitioner_id = search_practitioner_by_name(practitioner_name)
                    print(f"Found practitioner ID: {practitioner_id} for practitioner name: {practitioner_name}")
                except Exception as e:
                    print(f"Error finding practitioner: {e}")
                    practitioner_id = None

                if not practitioner_id:
                    raise ValueError("Failed to find practitioner. No practitioner ID returned.")

                # Create appointment
                appointment_response = create_appointment(
                    patient_id, practitioner_id, reason_text, start_time, end_time, appointment_type_display
                )
                result.append({
                    'patient_response': patient_response,
                    'appointment_response': appointment_response,
                    'patient': patient_dict
                })
        
        return jsonify({
            'success': True,
            'data': result,
            'count': len(result)
        })
    
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
    <title>XPC Medical Data Processor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        input[type="file"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
            background-color: #fff;
        }
        .checkbox-group {
            margin-top: 15px;
        }
        button {
            background-color: #3498db;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #2980b9;
        }
        #result {
            margin-top: 30px;
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 4px;
            background-color: #fff;
            display: none;
        }
        .patient-card {
            background-color: #f1f1f1;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 4px;
            border-left: 4px solid #3498db;
        }
        .patient-detail {
            margin-bottom: 8px;
        }
        .patient-detail strong {
            display: inline-block;
            width: 150px;
        }
        .api-result {
            margin-top: 15px;
            padding: 10px;
            background-color: #e8f4fc;
            border-radius: 4px;
        }
        .error {
            color: #e74c3c;
            font-weight: bold;
            padding: 10px;
            background-color: #fadbd8;
            border-radius: 4px;
        }
        .loader {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 2s linear infinite;
            display: none;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .csv-format {
            margin-top: 20px;
            padding: 15px;
            background-color: #eaf2f8;
            border-radius: 4px;
        }
        .format-tabs {
            display: flex;
            margin-bottom: 10px;
        }
        .format-tab {
            padding: 8px 16px;
            background-color: #ddd;
            cursor: pointer;
            border-radius: 4px 4px 0 0;
            margin-right: 5px;
        }
        .format-tab.active {
            background-color: #3498db;
            color: white;
        }
        .format-content {
            display: none;
        }
        .format-content.active {
            display: block;
        }
        pre {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }
        .note {
            margin-top: 20px;
            padding: 10px;
            background-color: #fdebd0;
            border-left: 4px solid #f39c12;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>XPC Medical Data Processor</h1>
        <p>Upload a CSV file containing patient data and convert it to structured data models.</p>
        
        <div class="csv-format">
            <h3>Supported CSV Formats:</h3>
            
            <div class="format-tabs">
                <div class="format-tab active" onclick="showFormat(0)">Format A: Column-based</div>
                <div class="format-tab" onclick="showFormat(1)">Format B: Row-based</div>
            </div>
            
            <div class="format-content active">
                <p>Fields in first column, patients in columns:</p>
                <pre>
,,,
Name,,Ben Smith,Mary Smith
,,,
Age,,37,25
Gender,,Male,Female
Sex,,Male,Female
Type of appointment,,Office visit,Phone call
Appointment date,,2/10/25,3/2/2025
Appointment time,,2:00 PM,1:00:00 PM
Physician,,"Paulius Mui, MD","Paulius Mui, MD"
Reason for visit,,cough,Flu</pre>
            </div>
            
            <div class="format-content">
                <p>Fields in first row, patients in rows:</p>
                <pre>
Name,Age,Gender,Sex,Type of appointment,Appointment date,Appointment time,Physician,Reason for visit
John Doe,34,male,Male,Phone call,3/21/2025,11:00:00 AM,Wits,Cold
Ben Smith,37,Male,Male,Office visit,2/10/25,2:00 PM,"Paulius Mui, MD",cough
Mary Smith,25,Female,Female,Phone call,3/2/2025,1:00:00 PM,"Paulius Mui, MD",Flu</pre>
            </div>
        </div>
        
        <div class="note">
            <strong>Note:</strong> The system will automatically detect your CSV format.
        </div>
        
        <form id="uploadForm">
            <div class="form-group">
                <label for="csv_file">Upload Medical CSV File:</label>
                <input type="file" id="csv_file" name="csv_file" accept=".csv" required>
            </div>
            
            <div class="form-group checkbox-group">
                <input type="checkbox" id="send_api" name="send_api" value="true">
                <label for="send_api" style="display:inline;">Simulate sending to external API</label>
            </div>
            
            <button type="submit">Process Data</button>
        </form>
        
        <div class="loader" id="loader"></div>
        
        <div id="result">
            <h2>Results</h2>
            <div id="resultContent"></div>
        </div>
    </div>

    <script>
        function showFormat(index) {
            const tabs = document.querySelectorAll('.format-tab');
            const contents = document.querySelectorAll('.format-content');
            
            // Remove active class from all tabs and contents
            tabs.forEach(tab => tab.classList.remove('active'));
            contents.forEach(content => content.classList.remove('active'));
            
            // Add active class to selected tab and content
            tabs[index].classList.add('active');
            contents[index].classList.add('active');
        }
        
        document.getElementById('uploadForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const loader = document.getElementById('loader');
            const resultDiv = document.getElementById('result');
            const resultContent = document.getElementById('resultContent');
            
            loader.style.display = 'block';
            resultDiv.style.display = 'none';
            
            const formData = new FormData(this);
            formData.append('send_api', document.getElementById('send_api').checked ? 'true' : 'false');
            
            fetch('/process', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                loader.style.display = 'none';
                resultDiv.style.display = 'block';
                
                if (data.error) {
                    resultContent.innerHTML = `<div class="error">${data.error}</div>`;
                    return;
                }
                
                if (data.success && data.data && data.data.length > 0) {
                    let html = `<p>Successfully processed ${data.count} patient records:</p>`;
                    
                    data.data.forEach((item, index) => {
                        const patient = item.patient;
                        html += `
                            <div class="patient-card">
                                <h3>Patient ${index + 1}: ${patient.first_name} ${patient.last_name}</h3>
                                <div class="patient-detail"><strong>Age:</strong> ${patient.age}</div>
                                <div class="patient-detail"><strong>Gender:</strong> ${patient.gender}</div>
                                <div class="patient-detail"><strong>Sex:</strong> ${patient.sex}</div>
                                <div class="patient-detail"><strong>Appointment Type:</strong> ${patient.appointment_type}</div>
                                <div class="patient-detail"><strong>Appointment Date:</strong> ${patient.appointment_date}</div>
                                <div class="patient-detail"><strong>Appointment Time:</strong> ${patient.appointment_time}</div>
                                <div class="patient-detail"><strong>Physician:</strong> ${patient.physician}</div>
                                <div class="patient-detail"><strong>Reason for Visit:</strong> ${patient.reason_for_visit}</div>
                                
                                ${item.api_result ? `
                                <div class="api-result">
                                    <strong>API Response:</strong><br>
                                    Status: ${item.api_result.success ? 'Success' : 'Failed'}<br>
                                    Message: ${item.api_result.message}<br>
                                    Patient ID: ${item.api_result.patient_id}
                                </div>` : ''}
                            </div>
                        `;
                    });
                    
                    resultContent.innerHTML = html;
                } else {
                    resultContent.innerHTML = `<div class="error">No patient data found or processing error occurred.</div>`;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                loader.style.display = 'none';
                resultDiv.style.display = 'block';
                resultContent.innerHTML = `<div class="error">An error occurred: ${error}</div>`;
            });
        });
    </script>
</body>
</html>
        """)

if __name__ == '__main__':
    create_template()
    app.run(debug=True)