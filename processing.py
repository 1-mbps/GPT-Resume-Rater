from autogen import UserProxyAgent
from pydantic import BaseModel
import json
import os
import re

from agents import ResumeRater
from streamlit_agents import ResumeRater as StreamlitResumeRater
from file_utils import convert_pdf_to_text

def process_chunk(chunk, resume_rater: ResumeRater, user: UserProxyAgent, ratings_list: list):
    """
    Function to process a chunk of the list of resumes.
    """
    for resume_path in chunk:
        resume_path = "resumes/"+resume_path
        print(f"Processing {resume_path}...")
        if not os.path.exists(resume_path):
            print(f"Error: Resume file '{resume_path}' not found.")
            continue

        resume_text = convert_pdf_to_text(resume_path)
        if resume_text:
            # silent - response does not show up in console
            # clear history - clear past resumes from agent's memory
            chat_result = user.initiate_chat(resume_rater, message=resume_text, max_turns=1, silent=True, clear_history=True)
            try:
                ratings_str = chat_result.chat_history[-1]["content"]
                if isinstance(ratings_str, BaseModel):
                    ratings_dict = ratings_str.model_dump()
                else:
                    ratings_dict = json.loads(ratings_str)
                ratings_list.append(ratings_dict)
            except Exception as e:
                print(f"Failed to parse ratings - {e}")
        else:
            print(f"Failed to process {resume_path}.")

def process_chunk_streamlit(chunk, resume_rater: StreamlitResumeRater, ratings_list: list):
    """
    Function to process a chunk of the list of resumes.
    """
    for filename, resume_bytes in chunk:
        resume_text = convert_pdf_to_text(resume_bytes)
        if resume_text:
            chat_result = resume_rater.respond(resume_text)
            try:
                ratings_dict = json.loads(chat_result)
                ratings_list.append(ratings_dict)
            except Exception as e:
                print(f"Failed to parse ratings - {e}")
        else:
            print(f"Failed to process {filename}.")

def convert_to_sentence(s):
    """
    Convert a category from the LLM JSON output (usually in snake or camel case)
    into normal text (sentence case)
    """
    # Check for snake_case
    if '_' in s:
        # Replace underscores with spaces and capitalize first letter
        sentence = s.replace('_', ' ').capitalize()
    else:
        # Check for camelCase
        # Use regex to insert spaces before capital letters and then capitalize first letter
        sentence = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', s).capitalize()
    
    return sentence

def format_properties(json_data: str):
    """
    Formats the rating system JSON produced by an agent into a nice Markdown string
    """
    properties = json_data.get('properties', {})
    required_fields = json_data.get('required', [])
    
    formatted_string = []
    
    for prop, details in properties.items():
        # convert property name to sentence case (looks better)
        prop_formatted = convert_to_sentence(prop)

        # say if required
        is_required = " (required)" if prop in required_fields else ""

        # build string for property
        formatted_string.append(f"**{prop_formatted}**{is_required}: {details['description']}")

    return "\n\n".join(formatted_string)