import streamlit as st
import uuid
from dotenv import load_dotenv
from src.graph import app

# Load environment variables from.env file
load_dotenv()

# --- Streamlit UI Configuration ---
st.set_page_config(page_title="Autonomous Research Agent", page_icon="🤖", layout="wide")
st.title("Autonomous Research Agent")

# --- Session State Management ---
# This ensures that each user session has a unique thread_id
# and that the message history is maintained across reruns.
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
    # FIX 1: Initialize with an empty list
    st.session_state.messages =[]

# Display the chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Main Application Logic ---
if prompt := st.chat_input("What topic should I research for you?"):
    # Add user's message to session state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare to display the agent's response
    with st.chat_message("assistant"):
        # Use a status container to show the agent's progress
        with st.status("Researching...", expanded=True) as status:
            final_report = ""
            
            # LangGraph configuration for the specific session
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            # FIX 2: Initialize summaries with an empty list
            initial_state = {"topic": prompt, "summaries":[]}

            # Stream events from the LangGraph agent
            for event in app.stream(initial_state, config=config):
                for key, value in event.items():
                    if key == "search":
                        status.write("Searching for relevant articles...")
                    elif key == "scrape_and_evaluate":
                        if value.get("scraped_content"):
                            url = value['scraped_content'].get('url', 'Unknown URL')
                            is_relevant = value['scraped_content'].get('is_relevant', 'Unknown')
                            status.write(f"Evaluating URL: {url} - Relevant: {is_relevant}")
                    elif key == "summarize":
                        status.write("Summarizing relevant content...")
                    elif key == "compile_report":
                        status.write("Compiling the final report...")
                        if value.get("report"):
                            final_report = value["report"]
            
            # Update the status to "complete" when done
            status.update(label="Research complete!", state="complete", expanded=False)
        
        # Display the final report
        st.markdown(final_report)

    # Add the final report to the session state
    st.session_state.messages.append({"role": "assistant", "content": final_report})