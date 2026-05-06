import os
import google.generativeai as genai
from typing import Optional, List
from PIL import Image

# Initialize Gemini model
MODEL_NAME = "gemini-2.5-flash"

def setup_gemini(api_key: str):
    """Initializes the Gemini API client with the given API key."""
    genai.configure(api_key=api_key)

import json

def generate_social_post(
    topic: str,
    platforms: List[str],
    tone: str,
    image_path: Optional[str] = None
) -> dict:
    """
    Generates social media posts for multiple platforms using Gemini 1.5 Flash.
    Supports multimodal inputs if image_path is provided.
    Returns a dictionary mapping platform name to {"content": str, "optimal_time": str}.
    """
    model = genai.GenerativeModel(MODEL_NAME)
    
    # Platform specific constraints
    constraints = ""
    for platform in platforms:
        if platform == "Twitter":
            constraints += f"- {platform}: Keep it under 280 characters. Use 1-2 relevant hashtags.\n"
        elif platform == "LinkedIn":
            constraints += f"- {platform}: Use a professional structure, potentially with bullet points. Avoid excessive emojis.\n"
        elif platform == "Instagram":
            constraints += f"- {platform}: Write a highly engaging caption. Use 5-10 hashtags at the end.\n"
        elif platform == "Facebook":
            constraints += f"- {platform}: Make it conversational and engaging to encourage comments. Use 2-3 hashtags.\n"

    # Construct prompt
    prompt = [
        "You are an expert social media manager. Your task is to write social media posts for multiple platforms.",
        f"Target Platforms: {', '.join(platforms)}",
        "IMPORTANT: You MUST return the result ONLY as a raw JSON object. Do not wrap in markdown code blocks like ```json. The JSON object should have the platform names as keys. The value for each key must be an object with two fields: 'content' (the post text) and 'optimal_time' (a string suggesting the best time to post, e.g., '14:30').",
    ]
    
    if image_path and os.path.exists(image_path):
        prompt.append(f"Based on the attached image and the topic: '{topic}', write {tone.lower()} social media posts.")
        prompt.append(constraints)
        try:
            img = Image.open(image_path)
            prompt.append(img)
        except Exception as e:
            return {"error": f"Error loading image: {str(e)}"}
    else:
        prompt.append(f"Topic: {topic}")
        prompt.append(f"Write {tone.lower()} social media posts.")
        prompt.append(constraints)
        
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean up markdown code block if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        return json.loads(text)
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
        return {"error": err_msg}
