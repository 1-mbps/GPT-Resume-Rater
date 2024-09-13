import os
from autogen import AssistantAgent
from autogen.agentchat.agent import Agent
from pydantic._internal._model_construction import ModelMetaclass
from typing import Any, Callable, Dict, List, Union
import yaml
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

with open("llm_config.yaml", "r") as file:
    model_config = yaml.safe_load(file)

client = OpenAI()

class SchemaMakerAgent(AssistantAgent):
    def __init__(self):
        super().__init__(
            name="schema_maker",
            system_message=model_config["schema_maker"]["system_message"],
            llm_config={
                "model": model_config["schema_maker"]["model"],
                "api_key": os.environ["OPENAI_API_KEY"],
                "response_format": {"type": "json_object"}
            }
        )

class ResumeRater(AssistantAgent):
    def __init__(self, schema: Union[ModelMetaclass, dict]):

        self.use_pydantic_schema = False

        # OpenAI structured outputs API supports either or Pydantic BaseModel
        # or a JSON schema like the one below
        # https://platform.openai.com/docs/guides/structured-outputs
        if isinstance(schema, dict):
            schema = {
                "type": "json_schema",
                "json_schema": {
                    "name": "resume_rating_schema",
                    "strict": True,
                    "schema": schema
                }
            }
        elif isinstance(schema, ModelMetaclass):
            self.rating_schema = schema
            self.use_pydantic_schema = True
        else:
            print(type(schema))
            raise Exception("Schema is not a Pydantic BaseModel or a valid JSON object.")
        super().__init__(
            name="resume_rater",
            system_message=model_config["resume_rater"]["system_message"],
            llm_config={
                "model": model_config["resume_rater"]["model"],
                "api_key": os.environ["OPENAI_API_KEY"],
                "response_format": schema
            }
        )

    def generate_reply(self, messages: List[Dict[str, Any]] | None = None, sender: Agent | None = None, **kwargs: Any) -> str | Dict | None:
        if self.use_pydantic_schema:
            # print(f"MESSAGES: {messages}")
            message = messages[-1].get("content")
            # print(f"MESSAGE: {message}")
            completion = client.beta.chat.completions.parse(
                model=self.llm_config["model"],
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": message}
                ],
                response_format=self.rating_schema,
            )
            return {"content": completion.choices[0].message.parsed, "role": "assistant"}
        return super().generate_reply(messages, sender, **kwargs)


# def get_llm_response(old_user_profile, query) -> dict:
    
    # query = user_message.format(old_user_profile=old_user_profile, query=query)
    
    # response = client.beta.chat.completions.parse(
    #     model=MODEL,
    #     messages=[
    #         {"role": "system", "content": system_message},
    #         {"role": "user", "content": query}
    #     ],
    #     response_format=Ratings,
    # )

    # return response.choices[0].message.parsed