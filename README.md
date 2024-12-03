# GPT-Resume-Rater

This is a CLI tool that uses LLM agents to rate resumes, and also generate a rating system based on a job description when required.

When finished running, it generates an Excel file `resume_ratings.xlsx` containing each candidate's name + several rating categories

## Setup

1. Install requirements:
    ```
    pip install requirements.txt
    ```
2. Create a .env file, based on example.env. Fill in your OPENAI_API_KEY.
3. Fill the `resumes` folder with PDF resumes. Filename doesn't matter - the LLM will extract each candidate's name and put it on the Excel sheet.

### Semi-automatic mode

For more control over the rating system.

Setup:

1. Create a file `schema.py`. Create a Pydantic BaseModel class called `Ratings` that defines the resume rating categories. Use this as reference: https://platform.openai.com/docs/guides/structured-outputs/
2. Run
    ```
    python main.py
    ```

### Fully automatic mode

If you want an LLM to generate the resume rating system for you.

Setup:

1. Create a machine-readable file (preferably .txt) containing the job description.
2. Run
    ```
    python main.py --job_description=PATH_TO_JOB_DESCRIPTION_FILE
    ```

    This will first print a resume rating system in the form of a JSON schema, and then ask for your feedback on the CLI.
    If you're satisfied, respond with "exit". If you'd like to change anything, simply tell the LLM on the CLI.

    Once the resume rating system is done (once you press "exit"), wait a while for the LLM to go over all resumes.

Sample output:
![image](https://github.com/user-attachments/assets/0d7a4373-b071-4386-af04-3d50b7781510)


## Modification
You can change the system prompts in `llm_config.yaml`.
Also, if you want to make the program faster (for example, if you have lots of resumes to parse), increase the value of the variable `N_THREADS` on `main.py`.

## Warnings
The model configuration file (`llm_config.yaml`) currently uses GPT-4o for all agents. If you decide to rate lots of resumes, this may burn some of your money.
