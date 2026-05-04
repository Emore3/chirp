import os
import google.generativeai as genai
from typing import Optional, List
from PIL import Image

# Initialize Gemini model
MODEL_NAME = "gemini-2.5-flash"

def setup_gemini(api_key: str):
    """Initializes the Gemini API client with the given API key."""
    genai.configure(api_key=api_key)

def generate_social_post(
    topic: str,
    platform: str,
    tone: str,
    image_path: Optional[str] = None
) -> str:
    """
    Generates a social media post using Gemini 1.5 Flash.
    Supports multimodal inputs if image_path is provided.
    """
    model = genai.GenerativeModel(MODEL_NAME)
    
    # Platform specific constraints
    constraints = ""
    if platform == "Twitter":
        constraints = "Keep it under 280 characters. Use 1-2 relevant hashtags."
    elif platform == "LinkedIn":
        constraints = "Use a professional structure, potentially with bullet points. Avoid excessive emojis."
    elif platform == "Instagram":
        constraints = "Write a highly engaging caption. Use 5-10 hashtags at the end."
    elif platform == "Facebook":
        constraints = "Make it conversational and engaging to encourage comments. Use 2-3 hashtags."

    # Construct prompt
    prompt = [
        "You are an expert social media manager. Your task is to write a social media post.",
        "IMPORTANT: Return ONLY the final post content. Do NOT include any introductory text, conversational filler (e.g., 'Here is your post'), or placeholders like '[Attached Image]'.",
    ]
    
    if image_path and os.path.exists(image_path):
        prompt.append(f"Based on the attached image and the topic: '{topic}', write a {tone.lower()} social media post for {platform}.")
        prompt.append(constraints)
        try:
            img = Image.open(image_path)
            prompt.append(img)
        except Exception as e:
            return f"Error loading image: {str(e)}"
    else:
        prompt.append(f"Topic: {topic}")
        prompt.append(f"Write a {tone.lower()} social media post for {platform}.")
        prompt.append(constraints)
        
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        available_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name.replace('models/', ''))
        except:
            pass
        
        err_msg = f"AI Generation Error: {str(e)}"
        if available_models:
            err_msg += f"\n\nAvailable models on your key: {', '.join(available_models)}"
        return err_msg
