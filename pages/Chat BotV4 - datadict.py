import streamlit as st
import google.generativeai as genai
from google.cloud import bigquery
import plotly.express as px
import json
import db_dtypes

# Main Application Title 
st.title("ChatBot 0.42 MADT")

#---------------------------------------------------------------------------------------------------
# Ai system function 

## Agent 01: Categorize User Input
agent_01 = genai.GenerativeModel("gemini-pro")
def categorize_task(user_input):
    categorize_prompt = f"""Categorize the following user input into one of two categories, you will return only 01 or 02::
                        - "01" : query_question if it's a question or requirement or any wording that about retrieving data from a database base on {data_dict}
                        - "02" : common_conversation if it's a general conversation such as greeting, general question, and anything else.
                        User input: "{user_input}" """
    response = agent_01.generate_content(categorize_prompt)
    bot_response = response.text.strip()
    return bot_response

## Agent 02: Query data from Big query
agent_02 = genai.GenerativeModel("gemini-pro")
def generate_sql_query(user_input):
    sql_prompt = f"""You are an AI assistant that transforms user questions into SQL queries to retrieve data from a BigQuery database.
                  {data_dict} Use this information to generate accurate SQL queries based on user input.
                  Generate a SQL query based on the user's input: '{user_input}'."""
    response = agent_02.generate_content(sql_prompt)
    bot_response = response.text.strip()
    clean_format_sql = bot_response.replace('\n', ' ').replace('sql', '').replace('   ',' ').replace('```','').strip()
    return  clean_format_sql

## Agent 03: Respond to General Conversation
agent_03 = genai.GenerativeModel("gemini-pro")
def general_conversation(user_input):
    conversation_prompt = f"""Respond to this user input in a friendly conversational style: "{user_input}" """
    response = agent_03.generate_content(conversation_prompt)
    bot_response = response.text.strip() 
    return bot_response

# Agent 04: Transform SQL Query Result into Conversational Answer
agent_04 = genai.GenerativeModel("gemini-pro")
def sql_result_to_conversation(result_data):
    result_prompt = f"""Take the following structured SQL query result and create a friendly answer: "{result_data}" """
    response = agent_04.generate_content(result_prompt)
    return response.text.strip()

# Agent 05: Transform Pandas dataframe into python code for plot the chart 
agent_05 = genai.GenerativeModel("gemini-pro")
def TF_graph(result_data):
    result_prompt = f"""Generate Python code to:
    1. Define a Pandas DataFrame named `df` based on the following data structure: {result_data}.
    2. Use plotly express to create a suitable graph based on the DataFrame structure and color by data.
    3. Return only executable Python code without markdown formatting or comments.
    The code should be fully executable in a Python environment and ready to display"""
    response = agent_05.generate_content(result_prompt)
    return response.text.strip()

##--------------------------------------------------------------------------------------

# Initialize session state variables if not already present
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = None

if "google_service_account_josn" not in st.session_state:
    st.session_state.google_service_account_json = None

if "qry" not in st.session_state:
    st.session_state.qry = None # Store SQL qury

# Create Chatbot history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [] # Empty list

# Create user_input history
if "user_input_history" not in st.session_state:
    st.session_state.user_input_history = []

if "qry" not in st.session_state:
    st.session_state.qry = None  # Store SQL query here

# Generate welcome message if gemini key correct
if "greeted" not in st.session_state:
    st.session_state.greeted = False

# Sidebar to display user input history as buttons
st.sidebar.title("User Input History")

# Add "Clear History" button in the sidebar
if st.sidebar.button("Clear History"):
    st.session_state.chat_history = []
    st.session_state.user_input_history = []
    st.session_state.greeted = False
    st.session_state.rerun_needed = False  # Set flag to trigger a rerun

# Loop through the user input history and create a button for each one
for i, prompt in enumerate(st.session_state.user_input_history, start=1):
    if st.sidebar.button(f"{i}. {prompt}"):
        # Reset chat history with the selected prompt
        st.session_state.chat_history = [("user", prompt)]
        st.session_state.rerun_needed = False  # Set flag to trigger a rerun
        user_input = prompt

        try:
            query_prompt = f"""You are an AI assistant that transforms user questions into SQL queries to retrieve data from a BigQuery database. 
            Use the schema information and generate a SQL query based on the user's input: '{user_input}'."""

            response = model.generate_content(query_prompt)
            bot_response = response.text

            st.session_state.qry = bot_response
            st.session_state.chat_history.append(("assistant", bot_response))

        except Exception as e:
            st.error(f"Error generating AI response: {e}")
        break  # Exit the loop after processing the first clicked history button

# Create Upload Panel for upload JSON Key file
upload_file = st.file_uploader("Upload Google Service Account Key JSON", type="json")

## Check status upload json key
if upload_file :
    try:
        # Load the upload JSON File into session state
        st.session_state.google_service_account_json = json.load(upload_file)           # Load file 
        st.success("Google Service Account Key file uploaded successfully!")
    except Exception as e :
        st.error(f"Error reading the uploaded file: {e}")


## Create an type space for GEMINI API KEY

gemini_api_key = 'AIzaSyBgvCcXEPMApduoTr_w8qJBQsrMan8rEDM'
#gemini_api_key = st.text_input("Gemini API key : ", placeholder= "Type your API Key here...", type = 'password')

##--------------------------------------------------------------------------------------
# Big query system 
## Function to initialize BigQuery client
def init_bigquery_client():
    if st.session_state.google_service_account_json:
        try :
            # Initialize BigQuery client using the service account JSON
            client = bigquery.Client.from_service_account_info(st.session_state.google_service_account_json)
            return client
            
        except Exception as e:
            st.error(f"Error initializing BigQuery client: {e}")
            return None
    else:
        st.error("Please upload a valid Google Service Account Key file.")
        return None


def run_bigquery_query(query):
    client = init_bigquery_client()
    if client and query:
        query = query
        job_config = bigquery.QueryJobConfig()
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()

        df = results.to_dataframe()
        return df
#----------------------------------------------------------------------------------------------------------------------
data_dict = """ If  it's a question or requirement or any wording that about retrieving data from a database base on 
                    the table name is 'madt8102-chatbot-final-project.datasets.transaction_detail_view'

                {
                "tables": [
                    {
                    "name": "region",
                    "fields": [
                        { "name": "regionId", "type": "STRING", "mode": "REQUIRED", "description": "Unique identifier for the region." },
                        { "name": "region_name", "type": "STRING", "mode": "NULLABLE", "description": "Name of the region." }
                    ]
                    },
                    {
                    "name": "return",
                    "fields": [
                        { "name": "reorder_cause_id", "type": "STRING", "mode": "REQUIRED", "description": "Unique identifier for the reorder cause."},
                        { "name": "cause", "type": "STRING", "mode": "NULLABLE", "description": "Description of the reorder cause." }
                    ]
                    },
                    {
                    "name": "return_transaction",
                    "fields": [
                        { "name": "InvoiceNo", "type": "STRING", "mode": "REQUIRED", "description": "Unique identifier for the invoice." },
                        { "name": "ProductId", "type": "STRING", "mode": "REQUIRED", "description": "Unique identifier for the product." },
                        { "name": "Quantity", "type": "INTEGER", "mode": "NULLABLE", "description": "Quantity of items returned." },
                        { "name": "TypeId", "type": "STRING", "mode": "NULLABLE", "description": "Type of the transaction." },
                        { "name": "Reorder_Cause_ID", "type": "STRING", "mode": "NULLABLE", "description": "Identifier for the reorder cause associated with the return." }
                    ]
                    },
                    {
                    "name": "sales_person",
                    "fields": [
                        { "name": "sales_id", "type": "STRING", "mode": "REQUIRED", "description": "Unique identifier for the salesperson." },
                        { "name": "salesperson_name", "type": "STRING", "mode": "NULLABLE", "description": "Name of the salesperson." },
                        { "name": "zoneId", "type": "STRING", "mode": "NULLABLE", "description": "Identifier for the zone associated with the salesperson." },
                        { "name": "regionId", "type": "STRING", "mode": "NULLABLE", "description": "Identifier for the region associated with the salesperson." }
                    ]
                    },
                    {
                    "name": "sell_item_type",
                    "fields": [
                        { "name": "typeId", "type": "STRING", "mode": "REQUIRED", "description": "Unique identifier for the item type." },
                        { "name": "type_name", "type": "STRING", "mode": "NULLABLE", "description": "Name or description of the item type." }
                    ]
                    },
                    {
                    "name": "customer_account",
                    "fields": [
                        { "name": "AccountID", "type": "STRING", "mode": "REQUIRED", "description": "Unique identifier for the customer account." },
                        { "name": "AccountName", "type": "STRING", "mode": "NULLABLE", "description": "Name of the customer account." }
                    ]
                    },
                    {
                    "name": "customer_branch",
                    "fields": [
                        { "name": "BranchID", "type": "STRING", "mode": "REQUIRED", "description": "Unique identifier for the customer branch." },
                        { "name": "AccountID", "type": "STRING", "mode": "REQUIRED", "description": "Identifier for the associated customer account." },
                        { "name": "BranchName", "type": "STRING", "mode": "NULLABLE", "description": "Name of the customer branch." },
                        { "name": "Country", "type": "STRING", "mode": "NULLABLE", "description": "Country of the customer branch." },
                        { "name": "Customer_Category", "type": "STRING", "mode": "NULLABLE", "description": "Category or type of the customer." },
                        { "name": "provinceId", "type": "STRING", "mode": "NULLABLE", "description": "Identifier for the associated province." },
                        { "name": "Latitude", "type": "FLOAT", "mode": "NULLABLE", "description": "Latitude coordinate of the branch location." },
                        { "name": "Longitude", "type": "FLOAT", "mode": "NULLABLE", "description": "Longitude coordinate of the branch location." }
                    ]
                    },
                    {
                    "name": "customer_sales_table",
                    "fields": [
                        { "name": "branchID", "type": "STRING", "mode": "REQUIRED", "description": "Unique identifier for the customer branch." },
                        { "name": "sales_id", "type": "STRING", "mode": "REQUIRED", "description": "Identifier for the salesperson associated with the branch." },
                        { "name": "regionId", "type": "STRING", "mode": "NULLABLE", "description": "Identifier for the region associated with the branch." }
                    ]
                    },
                    {
                    "name": "product",
                    "fields": [
                        { "name": "ProductId", "type": "STRING", "mode": "REQUIRED", "description": "Unique identifier for the product." },
                        { "name": "lenstype", "type": "STRING", "mode": "NULLABLE", "description": "Type of lens for the product." },
                        { "name": "Part_Description", "type": "STRING", "mode": "NULLABLE", "description": "Description of the product part." },
                        { "name": "Material_Type", "type": "STRING", "mode": "NULLABLE", "description": "Material used in the product." },
                        { "name": "Lens_Type", "type": "STRING", "mode": "NULLABLE", "description": "Type of lens material or design." },
                        { "name": "price", "type": "FLOAT", "mode": "NULLABLE", "description": "Price of the product." }
                    ]
                    },
                    {
                    "name": "province",
                    "fields": [
                        { "name": "provinceId", "type": "STRING", "mode": "REQUIRED", "description": "Unique identifier for the province." },
                        { "name": "province_name", "type": "STRING", "mode": "NULLABLE", "description": "Name of the province." },
                        { "name": "regionId", "type": "STRING", "mode": "NULLABLE", "description": "Identifier for the region associated with the province." },
                        { "name": "province_name_eng", "type": "STRING", "mode": "NULLABLE", "description": "English name of the province." },
                        { "name": "zoneId", "type": "STRING", "mode": "NULLABLE", "description": "Identifier for the zone associated with the province." }
                    ]
                    },
                    {
                    "name": "transaction_detail",
                    "fields": [
                        { "name": "InvoiceNo", "type": "STRING", "mode": "REQUIRED", "description": "Unique identifier for the invoice." },
                        { "name": "ProductId", "type": "STRING", "mode": "REQUIRED", "description": "Identifier for the product sold in the transaction." },
                        { "name": "Quantity", "type": "INTEGER", "mode": "NULLABLE", "description": "Quantity of items in the transaction." },
                        { "name": "UnitPrice", "type": "FLOAT", "mode": "NULLABLE", "description": "Price per unit of the product." }
                    ]
                    },
                    {
                    "name": "transaction_header",
                    "fields": [
                        { "name": "InvoiceNo", "type": "STRING", "mode": "REQUIRED", "description": "Unique identifier for the invoice." },
                        { "name": "InvoiceDate", "type": "DATE", "mode": "NULLABLE", "description": "Date of the invoice." },
                        { "name": "BranchID", "type": "STRING", "mode": "NULLABLE", "description": "Identifier for the branch where the transaction occurred." }
                    ]
                    },
                    {
                    "name": "zone",
                    "fields": [
                        { "name": "zoneId", "type": "STRING", "mode": "REQUIRED", "description": "Unique identifier for the zone." },
                        { "name": "zone_name", "type": "STRING", "mode": "NULLABLE", "description": "Name of the zone." },
                        { "name": "regionId", "type": "STRING", "mode": "NULLABLE", "description": "Identifier for the region associated with the zone." }
                    ]
                    }
                ]
                }

                    ### Relational Database Information
                    The 'ProductId' column in the 'product' table is a                             one-to-many    relationship with the 'transaction_detail' column in the 'ProductId' table. 
                    The 'ProductId' column in the 'return_transcation' table is a                  one-to-many    relationship with the 'transaction_detail' column in the 'ProductId' table. 
                    The 'return_items_cause_id' column in the 'return_transcation' table is a      one-to-one    relationship with the 'return_items_cause_id' column in the 'return_item' table. 
                    The 'InvoiceNo' column in the 'return_transcation' table is a                  one-to-many    relationship with the 'transaction_detail' column in the 'InvoiceNo' table. 
                    The 'typeId' column in the 'sell_item_type' table is a                         one-to-many    relationship with the 'transaction_detail' column in the 'TypeId' table.                   
                    The 'InvoiceNo' column in the 'transcation_header' table is a                  one-to-many    relationship with the 'transaction_detail' column in the 'InvoiceNo' table. 
                    The 'branchID' column in the 'customer_branch' table is a                      one-to-many    relationship with the 'branchID' column in the 'transaction_header' table. 
                    The 'accountId' column in the 'customer_branch' table is a                     one-to-many    relationship with the 'accountId' column in the 'customer_account' table. 
                    The 'branchID' column in the 'customer_sales' table is a                       one-to-one    relationship with the 'branchID' column in the 'customer_branch' table. 
                    The 'branchID' column in the 'customer_sales' table is a                       one-to-many    relationship with the 'branchID' column in the 'transaction_header' table. 
                    The 'sale_id' column in the 'customer_sales' table is a                        one-to-one    relationship with the 'sale_id' column in the 'sales_person' table. 
                    The 'provinceId' column in the 'province' table is a                           one-to-many    relationship with the 'provinceId' column in the 'customer_branch' table.
                    The 'zoneId' column in the 'zone' table is a                                   one-to-many    relationship with the 'zoneId' column in the 'province' table.
                    The 'regionId' column in the 'region' table is a                               one-to-many    relationship with the 'regionId' column in the 'zone' table.
                    
                    
                    """
                    


#------------------------------------------------------------------------------------------------------------------------
# Check GEMINI API KEY ready to use or not 
if gemini_api_key :
    try :
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-pro")

    except Exception as e:
        st.error(f"Error configuring Gemini API: {e}")
        model = None # Ensure 'model' is None if initialization fails

    # Display previous chat history from user 
    for role, message in st.session_state.chat_history:
        st.chat_message(role).markdown(message)
 
    # Generate greeting if not already greeted
    if not st.session_state.greeted:
        greeting_prompt = "Greet the user as a friendly and knowledgeable data engineer. \
                        Introduce yourself (you are AI assistant) and let the user know you're here to assist with \
                        any questions they may have about transforming user questions into SQL queries to retrieve data from a BigQuery database."

        try:
            response = model.generate_content(greeting_prompt)
            bot_response = response.text.strip()
            st.session_state.chat_history.append(("assistant", bot_response))
            st.chat_message("assistant").markdown(bot_response)
            st.session_state.greeted = True

        except Exception as e:
            st.error(f"Error generating AI greeting: {e}")

  # Create chat box if gemini_api_key is correct  
    if user_input := st.chat_input("Type your message here..."):

        # Append user input to chat history
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.user_input_history.append(user_input)                  # add to user input history
        st.chat_message("user").markdown(user_input)

        # Check Type of user input
        if user_input:
            task_type = categorize_task(user_input)
            # st.write(f'Task type : {task_type}')
            
            if int(task_type) == 1 :
                sql_query = generate_sql_query(user_input)              # Agent 02 Working 
                #st.write(f'Generated SQL Query:\n {sql_query}')                                    #For debug
                try:
 
                    # Generate bot response
                    bot_response = sql_query
                    # Append and display bot response
                    st.session_state.chat_history.append(("assistant", bot_response))
                    st.chat_message("assistant").markdown(bot_response)

                    # Execute the SQL query by chat bot and keep history 
                    result_data = run_bigquery_query(sql_query)                                     # Run big query 
                    #st.session_state.chat_history.append(("assistant",result_data))                # For debug
                    #st.chat_message("assistant").markdown(result_data)                             # For debug
                    #st.write(f'Result Data:\n{result_data}')                                       # For debug
                    
                    # Execute the SQL query by chat bot + conversational human language and keep history
                    # Agent 04 Working 
                    answer = sql_result_to_conversation(result_data)
                    st.session_state.chat_history.append(("assistant",answer))
                    st.chat_message("assistant").markdown(answer)
                    #st.write(f"Conversational Answer:\n{answer}")

                    # Excute The graph 
                    # Agent 05 Working 
                    
                    plot_code = TF_graph(result_data).replace('```','').replace('python','').strip()    
                    #st.write(f"Output from TF_graph: {plot_code}")                                          # For debug
                    #st.session_state.chat_history.append(("assistant",plot_code))                           # For debug
                    #st.chat_message("assistant").markdown(plot_code)                                        # For debug
                    #exec(plot_code)                                                                         # For debug  

                    # Define a local scope to safely execute the plot code
                    local_scope = {}
                    exec(plot_code, {}, local_scope)

                    # Check if the plotly figure is generated
                    if "fig" in local_scope:  # Assuming the generated Plotly figure is stored in a variable named 'fig'
                        plotly_fig = local_scope["fig"]

                        # Display the graph in the chatbot
                        st.chat_message("assistant").markdown("Here is the graph to represent the query:")
                        fig_show = st.plotly_chart(plotly_fig)  # Render the Plotly figure in Streamlit

                    else:
                        # If no figure is found, notify the user
                        st.chat_message("assistant").markdown("The code was executed successfully, but no graph was generated.")
                    

                except Exception as e:
                    # Handle and display any errors during code execution
                    error_message = f"Error executing the plot code: {e}"
                    st.chat_message("assistant").markdown(f"**Error:** {error_message}")

                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                # Agent 03 Working 
                bot_response = general_conversation(user_input)
                st.session_state.chat_history.append(("ai", bot_response))
                st.chat_message("assistant").markdown(bot_response)
                # st.write(f"General Conversation Response: {response}")


# Script for test 
# good morning
# i have a pen
# i want to know unique Product Id  
# i want to know sale person name and sale person average round trip hours top 10 

# i want to know product lens type and Quantity  of each lens type 
# thank you



