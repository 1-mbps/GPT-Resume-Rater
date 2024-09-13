import argparse
from autogen import UserProxyAgent
import json
import sys
import os

from agents import SchemaMakerAgent, ResumeRater
from file_utils import convert_pdf_to_text, build_csv_string, csv_to_excel

user = UserProxyAgent(name="user", code_execution_config=False)

def main():
    parser = argparse.ArgumentParser(description="Process job description file.")
    parser.add_argument("--job_description", type=str, help="Path to the job description file")
    
    args = parser.parse_args()

    resume_rater = None
    
    if args.job_description:
        try:
            with open(args.job_description, 'r') as file:
                job_desc = file.read()
        except FileNotFoundError:
            print(f"Error: File '{args.job_description}' not found.")
            sys.exit(1)
        except IOError:
            print(f"Error: Unable to read file '{args.job_description}'.")
            sys.exit(1)

        schema_maker = SchemaMakerAgent()
        chat_result = user.initiate_chat(schema_maker, message=job_desc)

        try:
            json_string_schema = chat_result.chat_history[-1]["content"]

            # Convert to dict
            rating_schema = json.loads(json_string_schema)
        except Exception as e:
            print("Error in parsing rating schema.")
            sys.exit(1)

        # Initialize resume rater agent
        resume_rater = ResumeRater(schema=rating_schema)

    else:
        try:
            # You can replace this with your own Pydantic BaseModel ratings class
            from schema import Ratings
            resume_rater = ResumeRater(schema=Ratings)
        except Exception as e:
            print("Error: Ratings class not found")
            sys.exit(1)

    if not isinstance(resume_rater, ResumeRater):
        print("Resume rater not initialized properly.")
        sys.exit(1)

    ratings_list = []

    # Iterate over each file in the folder "resumes"
    for resume_path in os.listdir("resumes"):
        resume_path = "resumes/"+resume_path
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
                ratings_dict = json.loads(ratings_str)
                ratings_list.append(ratings_dict)
            except Exception as e:
                print("Failed to parse ratings.")
        else:
            print("Failed to process resume.")

    csv_string = build_csv_string(ratings_list)
    csv_to_excel(csv_string, "resume_ratings.xlsx")

if __name__ == "__main__":
    main()