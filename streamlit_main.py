import streamlit as st
import dotenv
import threading
import os
import json
from io import BytesIO

from streamlit_agents import SchemaMakerAgent, ResumeRater
from processing import process_chunk_streamlit, format_properties
from file_utils import build_csv_string, csv_to_excel

dotenv.load_dotenv()

st.title("GPT Resume Rater")
st.session_state.N_THREADS = 8
st.session_state.curr_agent = 0

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

st.session_state.schema_maker = SchemaMakerAgent(messages=st.session_state.messages)

st.session_state.ratings_list = []
st.session_state.files = []
st.session_state.RATINGS_FILE = "resume_ratings.xlsx"
st.session_state.ratings_ready = False


# Step 1: Upload Resumes
uploaded_files = st.file_uploader("Upload resumes", accept_multiple_files=True, type="pdf")

if uploaded_files:
    for uploaded_file in uploaded_files:
        # read in each PDF as bytes
        bytes_data = uploaded_file.read()

        # save to memory
        st.session_state.files.append((uploaded_file.name, BytesIO(bytes_data)))
    st.success("Resumes uploaded successfully!")

# Step 2: Prompt for Job Description
job_description = st.text_area("Please enter the job description:", height=150)

if st.button("Submit Job Description"):
    if job_description:
        try:
            st.session_state.rating_schema = json.loads(st.session_state.schema_maker.respond(job_description))
        except Exception as e:
            st.error(f"Unspecified error in creating the initial rating system. Please try again later: {e}")
        st.success("Job description submitted successfully!")
        st.session_state['job_description'] = job_description
        st.session_state['chat_active'] = True
    else:
        st.error("Please enter a job description before submitting.")

# Step 3: Chatbot Interface
if 'chat_active' in st.session_state and st.session_state['chat_active'] and "rating_schema" in st.session_state and st.session_state.files:

    rating_schema_str = format_properties(st.session_state.rating_schema)
    st.markdown("---")
    st.markdown(f"### Rating System\n{rating_schema_str}")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] != "system":
                content = message['content']
                if content.strip()[0] == '{':
                    json_dict = json.loads(content)
                    response = format_properties(json_dict)
                    st.session_state.rating_schema = json_dict
                else:
                    response = content
                st.markdown(response)
        
    if prompt := st.chat_input("Give feedback on the rating system, or type 'done' to continue to resume rating."):
        
        # If done making rating schema, ask to upload resumes, then move to
        # resume rater agent
        if st.session_state.curr_agent == 0 and prompt == "done":
            st.session_state.curr_agent = 1
        
        # ELSE, we're not done making the schema
        # so let the user have a conversation with the AI to improve it
        else:
            # Save and display user message
            # st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get response from agent
            schema_maker_response = st.session_state.schema_maker.respond(prompt)

            print(f"RESPONSE: {schema_maker_response}")

            # Save and display message
            if schema_maker_response.strip()[0] == '{':
                json_dict = json.loads(schema_maker_response)
                response = format_properties(json_dict)
                st.session_state.rating_schema = json_dict
            else:
                response = schema_maker_response

            # st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("ai"):
                st.markdown(response)
    
    # Step 4: Rate resumes
    if st.session_state.curr_agent == 1:
        resume_rater = ResumeRater(schema=st.session_state.rating_schema)

        # Prepare to use multithreading to quickly go over resumes
        chunk_size = len(st.session_state.files) // st.session_state.N_THREADS

        # Create and start threads
        threads = []
        for i in range(st.session_state.N_THREADS):
            start_index = i * chunk_size
            end_index = start_index + chunk_size if i < st.session_state.N_THREADS - 1 else None
            chunk = st.session_state.files[start_index:end_index]
            
            thread = threading.Thread(target=process_chunk_streamlit, args=(chunk,resume_rater,st.session_state.ratings_list))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Convert st.session_state.ratings_list into a CSV string, which can easily be turned into Excel
        csv_string = build_csv_string(st.session_state.ratings_list)
        csv_to_excel(csv_string, st.session_state.RATINGS_FILE)
        st.session_state.ratings_ready = True

    # Step 4: Download the ratings file
    if os.path.exists(st.session_state.RATINGS_FILE) and st.session_state.ratings_ready:
        # Read the file as bytes
        with open(st.session_state.RATINGS_FILE, "rb") as file:
            btn = st.download_button(
                label="Download resume ratings",
                data=file,
                file_name="resume_ratings.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )