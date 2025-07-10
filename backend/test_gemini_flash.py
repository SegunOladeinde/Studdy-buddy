import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("AIzaSyBgeVmZYE2_bJT49IbeX_hGhhi5U0oouIE"))

# Use the correct model
model = genai.GenerativeModel('gemini-1.5-flash')

# Test prompt
response = model.generate_content("Explain photosynthesis in simple terms.")

print("📬 Response from Gemini Flash:", response.text)