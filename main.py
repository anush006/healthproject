from flask import Flask
from flask_cors import CORS
from google import genai
from google.genai.types import Part
import PIL.Image
import re


# Flask and CORS setup
app = Flask(__name__)
CORS(app)

# Add API Key here
GOOGLE_API_KEY = ""


@app.route('/nutrition')
def nutrition():

    image_path = ""  # Path of image for which nutriets are to be checked

    image = PIL.Image.open(image_path)

    # Prompt description. Change accordingly for desired output
    prompt = """
    Upon receipt of an image, execute a comprehensive nutritional analysis and generate a structured JSON response. The analysis should encompass the identification of food items, estimation of caloric content, and provision of relevant nutritional data.

    Response Specifications:

    The output must adhere strictly to JSON format, utilizing the following keys:

    food_detected: A list of food items identified within the image.
    calories: An estimated caloric value for the depicted food.
    nutritional_info: A nested JSON object containing:
        carbs: Estimated carbohydrate content (expressed in grams).
        proteins: Estimated protein content (expressed in grams).
        fats: Estimated fat content (expressed in grams).
    health_warnings: A concise statement outlining potential health considerations associated with the food's 
    nutritional profile.
    alternatives: Recommendations for nutritionally superior alternatives to the depicted food.
    """

    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[prompt,image])

        return clean_json(response.text)
    except:
        return "Unknown error occured"


@app.route('/report-analysis')
def report_analysis():

    file_path = ""   # Path of file to be analysed

    # Checking if the file is a pdf or image
    ispdf = ''
    try:
        with open(file_path, "rb") as file:
            ispdf =  (file.read(4) == b"%PDF")
    except:
        pass

    # Converting pdf/image to appropriate format
    
    if(ispdf):
        with open(file_path, "rb") as f:
            document = Part.from_file(f, mime_type="application/pdf")
    else:
        document = PIL.Image.open(file_path)


    # Prompt description. Change accordingly for desired output
    prompt = """
    Analyze the provided medical data from a PDF or JPEG image and output a JSON summary with:

    name: Patient's name.
    age: Patient's age.
    height: Height (with units).
    weight: Weight (with units).
    blood_pressure: BP reading and classification.
    sugar_level: Sugar level and classification.
    cholesterol: Cholesterol level and classification.
    health_risk: Summary of health risks.
    doctor_recommendation: Doctor's advice.

    Classify vital signs. Example: BP 140/90 = '140/90 (Pre-hypertension)'.

    Example Input: PDF or JPEG containing: Name: John Doe, Age: 45, Height: 170cm, Weight: 75kg, 
    Blood Pressure: 140/90, Sugar Level: 140, Cholesterol: 190.
    """

    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[prompt,document])

        return clean_json(response.text)

    except:
        return "Unknown error occured"


@app.route('/recipie')
def recipie():


    # Prompt description. Change accordingly for desired output
    prompt = """
    Analyze the provided JSON medical report to identify potential health conditions or risk factors. 
    Based on these findings, suggest a suitable south indian food recipe that addresses the user's dietary needs. 
    The recipe should be presented in JSON format with the following keys:, strictly follow the given format

    
    recipe_name: The name of the recommended recipe.
    ingredients: A list of ingredients required for the recipe.
    calories: An estimated calorie count per serving.
    diet_friendly: Any relevant dietary classifications (e.g., "Low Sodium," "Low Sugar," "High Fiber").
    Instructions: Step-by-step instructions for preparing the recipe.
    health_benefits: A brief explanation of how the recipe's ingredients and nutritional profile benefit the user's 
    health based on their analyzed medical report.
    """

    data = ""   # Pass data about user's health condition here
    
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[prompt,data])

        return clean_json(response.text)

    except:
        return "Unknown error occurred"
    

@app.route('/chatbot')
def chatbot():

    user_query = ""   # Queries from user
    user_info = ""    # Information regarding user's health

    # Prompt description. Change accordingly for desired output
    prompt = """
    Role:
        You are a chatbot that helps answer user's query regarding a nutrition based application. Answer to the user 
        related to this. If the user asks anything else, ask them to ask a question based on this. Refer to user's health
        data to answer their questions.Do not answer any question out of scope.
    """

    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[prompt,user_query,user_info])

        return response.text

    except:
        return "Unknown error occurred"



def clean_json(markdown_json_string):
   
   # Cleaning json content

    json_content = re.search(r'```json\n(.*?)```', markdown_json_string, re.DOTALL)
    if json_content:
        json_text = json_content.group(1)
    else:
        raise ValueError("Could not extract JSON from the input string")

    return json_text





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)