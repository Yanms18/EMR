from patient0 import create_patient0
import os

# Verify that the API key and base URL are loaded
XPC_API_KEY = os.environ.get("XPC_API_KEY")
XPC_FHIR_API_BASE_URL = os.environ.get("XPC_FHIR_API_BASE_URL")

if not XPC_API_KEY or not XPC_FHIR_API_BASE_URL:
    raise ValueError("API key or base URL not found. Please check your .env file.")

# Input the details
firstname = "Paulius"
lastname = "Biday"
age = 37
sex = "M"  # Options: F, M, OTH, UNK
gender = "male"  # Options: female, male, other, unknown

# Create patient
response = create_patient0(firstname, lastname, age, sex, gender)

print("Patient creation response:")
print("Response Body:", response)

