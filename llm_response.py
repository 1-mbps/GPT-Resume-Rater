import os
from openai import OpenAI

from json_schema import Score

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

system_message = """
Your job is to update old information.
You will be given a "user profile" and a query from the user.
Your task is to update the user profile with relevant information from the user's query.
Any additions you make must come directly from the user's query. You may not infer, extrapolate, or otherwise include anything that the user did not explicitly say.
You must never delete anything that was previously in the user profile unless, based on the user's query, they are no longer relevant or up to date.
Respond in the JSON format you are provided.
There must not be any overlap between the user_info and the business_info objects.
"""

user_message = """
User profile:

{old_user_profile}

User's query:

{query}

"""

MODEL = "gpt-4o-2024-08-06"

def get_llm_response(old_user_profile, query) -> dict:
    
    query = user_message.format(old_user_profile=old_user_profile, query=query)
    
    response = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": query}
        ],
        response_format=Score,
    )

    return response.choices[0].message.parsed