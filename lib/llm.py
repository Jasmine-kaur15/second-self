"""Wrapper for the Groq API (Llama 3). Handles classification prompts, RAG answering, and API error/retry logic."""

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def get_groq_client():
    # Attempt to load from Streamlit secrets first, then fallback to environment variables
    api_key = None
    try:
        import streamlit as st
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        pass

    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
        
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is missing. Please set it in your .env file or Streamlit secrets.")
    return Groq(api_key=api_key)

def classify_content(content: str) -> dict:
    """
    Prompts Llama 3 to classify the content into PARA, extract tags, and summarize.
    Returns a dictionary with keys: 'para', 'tags', 'summary', 'confidence'.
    """
    client = get_groq_client()
    
    prompt = f"""
    You are an intelligent knowledge librarian applying the PARA methodology. 
    Classify the following text into exactly one of these categories:
    
    - Projects: Active work with a defined goal. (e.g. SecondSelf, TrustAI, Building a chatbot, Internship tasks)
    - Areas: Long-term responsibilities with no end date. (e.g. Health, Fitness, Career, Personal Finance, University)
    - Resources: Information kept for future reference. (e.g. Wikipedia articles, Documentation, Tutorials, PDFs, Notes)
    - Archives: Completed or inactive material. (e.g. Old projects, Finished internship notes, Outdated documents)
    
    You must extract:
    1. The single best PARA category ("para")
    2. A brief 1-2 sentence summary ("summary")
    3. A list of relevant tags (max 5) ("tags")
    4. A confidence percentage (e.g. "95%") ("confidence")

    Example 1
    Input: "I am building SecondSelf using Groq and Streamlit."
    Output: {{"para":"Projects", "summary":"Building the SecondSelf knowledge management application.", "tags":["SecondSelf","Groq","Streamlit"], "confidence":"99%"}}
    
    Example 2
    Input: "Python documentation for pathlib."
    Output: {{"para":"Resources", "summary":"Reference documentation for pathlib.", "tags":["Python","Documentation"], "confidence":"95%"}}
    
    Example 3
    Input: "Workout routine for shoulders."
    Output: {{"para":"Areas", "summary":"Shoulder workout plan.", "tags":["Fitness","Health"], "confidence":"90%"}}
    
    Example 4
    Input: "My completed DBMS mini project from 2024."
    Output: {{"para":"Archives", "summary":"Completed DBMS project.", "tags":["DBMS","Completed Project"], "confidence":"100%"}}
    
    Output strictly as JSON. Do not default everything to Archives.
    
    Text:
    {content[:8000]}
    """

    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a JSON assistant. Always output valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            result = response.choices[0].message.content.strip()
            data = json.loads(result)
            
            return {
                "para": data.get("para", "Resources"),
                "tags": data.get("tags", []),
                "summary": data.get("summary", "No summary provided."),
                "confidence": data.get("confidence", "Unknown")
            }
        except Exception as e:
            if attempt == 1:
                print(f"Failed to classify content after retry: {e}")
                return {
                    "para": "Resources",
                    "tags": [],
                    "summary": "Classification failed.",
                    "confidence": "0%",
                    "classification_failed": True
                }
