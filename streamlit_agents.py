import os
import yaml
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

with open("llm_config.yaml", "r") as file:
    model_config = yaml.safe_load(file)

class SchemaMakerAgent:
    def __init__(self):
        self.model = model_config["schema_maker"]["model"]
        self.system_message = model_config["schema_maker"]["system_message"]
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.messages = [{"role": "system", "content": self.system_message}]

    def respond(self, query: str) -> str:
        self.messages.append({"role": "user", "content": query})
        completion = self.client.chat.completions.create(
            messages=self.messages,
            model=self.model,
            response_format={"type": "json_object"}
        )
        return completion.choices[0].message.content
    

class ResumeRater:
    def __init__(self, schema: dict):
        self.model = model_config["resume_rater"]["model"]
        self.system_message = model_config["resume_rater"]["system_message"]
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.rating_schema = {
            "type": "json_schema",
            "json_schema": {
                "name": "resume_rating_schema",
                "strict": True,
                "schema": schema
            }
        }

    def respond(self, query: str):
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": query}
            ],
            response_format=self.rating_schema,
        )
        return completion.choices[0].message.content