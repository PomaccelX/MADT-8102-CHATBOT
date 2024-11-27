import streamlit as st
import google.generativeai as genai
from google.cloud import bigquery
import plotly.express as px
import json
import db_dtypes
#---------------------------------------------------------------------------------------------------------------------------

# Main Application Title
st.title("ChatBot 0.42 MADT")

# Load secrets securely from Streamlit
gemini_api_key = st.secrets["api_keys"].get("gemini_api_key")
service_account_key = st.secrets["google"].get("service_account_key")
json_file_path = service_account_key

if gemini_api_key and service_account_key:
    st.success("Gemini API Key and Service Account Key loaded successfully!")
else:
    st.error("Failed to load Gemini API Key or Service Account Key. Please check your secrets.")

# Convert service account key into a Python dictionary
try:
    key_dict = json.loads(service_account_key)
except json.JSONDecodeError:
    st.error("Error decoding the Service Account Key. Please check the format.")
    key_dict = None

##--------------------------------------------------------------------------------------
data_dict = """ If  it's a question or requirement or any wording that about retrieving data from a database base on 
                    the table name is 'madt8102-chatbot-final-project.datasets.fact_transaction'

                    | Column Name                       | Data Type   | Description                                 |
                    |-----------------------------------|-------------|---------------------------------------------|
                    | InvoiceNo                         | STRING      | Unique identifier for the invoice.          |
                    | ProductId                         | STRING      | Identifier for the product.                 |
                    | Quantity                          | INT64       | Number of units sold.                       |
                    | ActualPrice                       | FLOAT64     | Actual price of the product sold.           |
                    | StandardPrice                     | FLOAT64     | Standard price of the product.              |
                    | TypeId                            | STRING      | Identifier for the type of product.         |
                    | TypeName                          | STRING      | Name of the product type.                   |
                    | InvoiceDate                       | DATE        | Date of the invoice.                        |
                    | BranchName                        | STRING      | Name of the branch where the sale occurred. |
                    | AccountID                         | STRING      | Account identifier for the customer.        |
                    | AccountName                       | STRING      | Name of the customer account.               |
                    | Country                           | STRING      | Country where the sale occurred.            |
                    | Customer_Category                 | STRING      | Category of the customer.                   |
                    | Latitude                          | FLOAT64     | Geographical latitude of the location.      |
                    | Longitude                         | FLOAT64     | Geographical longitude of the location.     |
                    | ProductDescription                | STRING      | Description of the product.                 |
                    | Material_Type                     | STRING      | Type of material for the product.           |
                    | Lens_Type                         | STRING      | Type of lens, if applicable.                |
                    | ProvinceName                      | STRING      | Name of the province.                       |
                    | ProvinceNameEng                   | STRING      | Name of the province in English.            |
                    | ZoneName                          | STRING      | Name of the zone.                           |
                    | RegionName                        | STRING      | Name of the region.                         |
                    | Discount                          | FLOAT64     | Discount applied to the sale, if any.       |

                    the table name is 'madt8102-chatbot-final-project.datasets.customer_account'
                    | Column Name   | Data Type   | Description                                |
                    |---------------|-------------|--------------------------------------------|
                    | AccountId     | STRING      | Unique identifier for the account.         |
                    | AccountName   | STRING      | Name associated with the account.          |

                    the table name is 'madt8102-chatbot-final-project.datasets.customer_branch'
                    | Column Name        | Data Type   | Description                                                |
                    |--------------------|-------------|------------------------------------------------------------|
                    | BranchID           | STRING      | Unique identifier for the branch.                         |
                    | AccountID          | STRING      | Unique identifier for the associated account.             |
                    | BranchName         | STRING      | Name of the branch.                                       |
                    | Country            | STRING      | Country where the branch is located.                     |
                    | Customer_Category  | STRING      | Category of customers served by the branch.              |
                    | ProvinceID         | STRING      | Identifier for the province where the branch is located. |
                    | Latitude           | FLOAT       | Latitude coordinate of the branch's location.            |
                    | Longitude          | FLOAT       | Longitude coordinate of the branch's location.           |

                    the table name is 'madt8102-chatbot-final-project.datasets.customer_sales_table'
                    | Column Name | Data Type | Description                               |
                    |-------------|-----------|-------------------------------------------|
                    | branchID    | STRING    | Unique identifier for the branch.         |
                    | sales_id    | STRING    | Unique identifier for the sales invoice.  |
                    | regionId    | STRING    | Unique identifier for the sales region.   |

                    the table name is 'madt8102-chatbot-final-project.datasets.date_time'
                    | Column Name   | Data Type   | Description                                                              |
                    |---------------|-------------|--------------------------------------------------------------------------|
                    | Date          | DATE        | The full calendar date in the format 'YYYY-MM-DD'.                      |
                    | Year          | INTEGER     | The year extracted from the date (e.g., 2024).                          |
                    | Quarter       | INTEGER     | The quarter of the year (1 for Jan-Mar, 2 for Apr-Jun, etc.).           |
                    | Month         | INTEGER     | The numerical representation of the month (1 for January, 2 for February). |
                    | MonthName     | STRING      | The full name of the month (e.g., January, February).                   |
                    | WeekOfYear    | INTEGER     | The week number of the year (1 to 53).                                  |
                    | Day           | INTEGER     | The numerical day of the month (1 to 31).                               |
                    | DayOfWeek     | INTEGER     | The numerical representation of the day of the week (1 for Monday to 7).|
                    | DayName       | STRING      | The full name of the day (e.g., Monday, Tuesday).                       |
                    | DayOfYear     | INTEGER     | The day number in the year (1 for January 1, 365/366 for December 31).  |
                    | IsWeekend     | BOOLEAN     | Indicates if the day is a weekend (TRUE for Saturday/Sunday, FALSE otherwise). |

                    the table name is 'madt8102-chatbot-final-project.datasets.product'
                    | Column Name        | Data Type   | Description                                          |
                    |--------------------|-------------|------------------------------------------------------|
                    | ProductId          | STRING      | Unique identifier for the product.                  |
                    | LensType           | STRING      | Type or category of the lens.                       |
                    | Part_Description   | STRING      | Detailed description of the part.                   |
                    | Material_Type      | STRING      | Type of material used for the product.              |
                    | Lens_Type          | STRING      | Specifies the type of lens (e.g., single, bifocal). |
                    | Price              | FLOAT       | Price of the product.                               |               

                     the table name is 'madt8102-chatbot-final-project.datasets.province'
                    | Column Name        | Data Type   | Description                                               |
                    |--------------------|-------------|-----------------------------------------------------------|
                    | ProvinceID         | STRING      | Unique identifier for the province.                      |
                    | Province_Name      | STRING      | Name of the province in the local language.              |
                    | RegionID           | STRING      | Identifier for the region to which the province belongs. |
                    | Province_Name_Eng  | STRING      | Name of the province in English.                         |
                    | ZoneID             | STRING      | Identifier for the zone to which the province belongs.   |

                    the table name is 'madt8102-chatbot-final-project.datasets.region'
                    | Column Name      | Data Type   | Description                                     |
                    |------------------|-------------|-------------------------------------------------|
                    | region_name      | STRING      | Identifier for the sales region_name.                 |
                    | regionId         | STRING      | Identifier for the sales region.   

                    the table name is 'madt8102-chatbot-final-project.datasets.return'
                    | Column Name       | Data Type   | Description                                    |
                    |-------------------|-------------|------------------------------------------------|
                    | reorder_cause_id  | STRING      | Unique identifier for the reorder cause.      |
                    | cause             | STRING      | Description or name of the reorder cause.     |

                    the table name is 'madt8102-chatbot-final-project.datasets.return_transaction'
                    | Column Name        | Data Type   | Description                                      |
                    |--------------------|-------------|--------------------------------------------------|
                    | InvoiceNo          | STRING      | Unique identifier for the invoice.              |
                    | ProductId          | STRING      | Unique identifier for the product.              |
                    | Quantity           | INTEGER     | Number of units of the product in the invoice.   |
                    | TypeId             | STRING      | Identifier for the product type or category.    |
                    | Reorder_Cause_ID   | STRING      | Identifier for the cause of reorder.            |

                    the table name is 'madt8102-chatbot-final-project.datasets.sales_person'
                    | Column Name      | Data Type   | Description                                     |
                    |------------------|-------------|-------------------------------------------------|
                    | sales_id         | STRING      | Unique identifier for the sales transaction.   |
                    | salesperson_name | STRING      | Name of the salesperson involved.              |
                    | zoneId           | STRING      | Identifier for the sales zone.                 |
                    | regionId         | STRING      | Identifier for the sales region. 

                    the table name is 'madt8102-chatbot-final-project.datasets.sell_item_type'
                    | Column Name | Data Type | Description                               |
                    |-------------|-----------|-------------------------------------------|
                    | typeId      | STRING    | Unique identifier for the item type.     |
                    | type_name   | STRING    | Name or description of the item type.    |
                 
                    the table name is 'madt8102-chatbot-final-project.datasets.transaction_detail'
                    | Column Name | Data Type | Description                               |
                    |-------------|-----------|-------------------------------------------|
                    | InvoiceNo   | STRING    | Unique identifier for the invoice.       |
                    | ProductId   | STRING    | Identifier for the product.              |
                    | ActualPrice | FLOAT     | Actual price of the product.             |
                    | Quantity    | INTEGER   | Number of units sold.                    |
                    | TypeId      | STRING    | Identifier for the product type.         |

                     the table name is 'madt8102-chatbot-final-project.datasets.transaction_header'
                    | Column Name   | Data Type   | Description                                |
                    |---------------|-------------|--------------------------------------------|
                    | InvoiceNo     | STRING      | Unique identifier for the invoice.        |
                    | InvoiceDate   | DATE        | The date when the invoice was created.     |
                    | BranchID      | STRING      | Unique identifier for the branch.         |

                    the table name is 'madt8102-chatbot-final-project.datasets.zone'
                    | Column Name   | Data Type   | Description                                          |
                    |---------------|-------------|------------------------------------------------      |
                    | zoneId        | STRING      | Unique identifier for the zone.                      |
                    | zone_name     | STRING      | Name or description of the zone.                     |
                    | regionId      | STRING      | Identifier for the region to which the zone belongs. |

                    ### Relational Database Information
                    The 'ProductId' column in the 'product' table is a                             one-to-many    relationship with the 'transaction_detail' column in the 'ProductId' table. 
                    The 'ProductId' column in the 'return_transcation' table is a                  one-to-many    relationship with the 'transaction_detail' column in the 'ProductId' table. 
                    The 'return_items_cause_id' column in the 'return_transcation' table is a      one-to-one     relationship with the 'return_items_cause_id' column in the 'return_item' table. 
                    The 'InvoiceNo' column in the 'return_transcation' table is a                  one-to-many    relationship with the 'transaction_detail' column in the 'InvoiceNo' table. 
                    The 'typeId' column in the 'sell_item_type' table is a                         one-to-many    relationship with the 'transaction_detail' column in the 'TypeId' table.                   
                    The 'InvoiceNo' column in the 'transcation_header' table is a                  one-to-many    relationship with the 'transaction_detail' column in the 'InvoiceNo' table. 
                    The 'branchID' column in the 'customer_branch' table is a                      one-to-many    relationship with the 'branchID' column in the 'transaction_header' table. 
                    The 'accountId' column in the 'customer_branch' table is a                     one-to-many    relationship with the 'accountId' column in the 'customer_account' table. 
                    The 'branchID' column in the 'customer_sales' table is a                       one-to-one     relationship with the 'branchID' column in the 'customer_branch' table. 
                    The 'branchID' column in the 'customer_sales' table is a                       one-to-many    relationship with the 'branchID' column in the 'transaction_header' table. 
                    The 'sale_id' column in the 'customer_sales' table is a                        one-to-one     relationship with the 'sale_id' column in the 'sales_person' table. 
                    The 'provinceId' column in the 'province' table is a                           one-to-many    relationship with the 'provinceId' column in the 'customer_branch' table.
                    The 'zoneId' column in the 'zone' table is a                                   one-to-many    relationship with the 'zoneId' column in the 'province' table.
                    The 'regionId' column in the 'region' table is a                               one-to-many    relationship with the 'regionId' column in the 'zone' table.
                    
                    """     
#----------------------------------------------------------------------------------------------------------------------

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

#-----------------------------------------------------------------------------------------------------------

# AI System Functions
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
    result_prompt = f"""Take the following structured SQL query result and create a friendly answer result : "{result_data}" """
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

#---------------------------------------------------------------------------------------------------
# Big query system 
## Function to initialize BigQuery client
def init_bigquery_client(json_file_path):
        
    # Check if the JSON file is loaded into the session state
    if "google_service_account_json" in st.session_state:
        try:
            # Initialize BigQuery client
            client = bigquery.Client.from_service_account_info(st.session_state.google_service_account_json)
            #st.success("BigQuery client initialized successfully!")
            return client
        except Exception as e:
            st.error(f"Error initializing BigQuery client: {e}")
            return None
    else:
        st.error("Service account JSON file not loaded. Please provide a valid file.")
        return None

def run_bigquery_query(query):
    client = init_bigquery_client(json_file_path)
    if client and query:
        try:
            # Set up query job and execute
            query_job = client.query(query)
            results = query_job.result()
            df = results.to_dataframe()
            #st.success("Query executed successfully!")
            return df
        except Exception as e:
            st.error(f"Error executing BigQuery query: {e}")
            return None
    else:
        st.error("BigQuery client not initialized or query is empty.")
        return None

#----------------------------------------------------------------------------------------------------------------------
# Sidebar to display user input history as buttons
st.sidebar.title("User Input History")

# Add "Clear History" button in the sidebar
if st.sidebar.button("Clear History"):
    # Clear session state variables to reset chat history
    st.session_state.chat_history = []
    st.session_state.user_input_history = []
    st.session_state.greeted = False
    #st.session_state.rerun_needed = False  # Set flag to trigger a rerun
    user_input = ""  # Clear previous input
    category = ""  # Reset category for new input

# Loop through the user input history and create a button for each one
for i, prompt in enumerate(st.session_state.user_input_history, start=1):
    if st.sidebar.button(f"{i}. {prompt}"):
        # Reset chat history with the selected prompt
        st.session_state.chat_history = [("user", prompt)]
        #st.session_state.rerun_needed = False  # Set flag to trigger a rerun
        user_input = prompt

        # Categorize the input
        category = categorize_task(user_input)
        
        # Check if category is "01" (database query)
        if category == "01":
            try:
                # Agent 2: Generate SQL Query based on user input
                sql_query = generate_sql_query(user_input)
                result_data = run_bigquery_query(sql_query)  

                # Agent 4: Transform SQL Result into Conversational Answer
                conversational_answer = sql_result_to_conversation(result_data)
                #st.chat_message("assistant").markdown(conversational_answer)

                # Agent 5: Generate Python code for plotting based on result data

                graph_code = TF_graph(conversational_answer)
                plot_code = TF_graph(graph_code).replace('```','').replace('python','').strip() 

                # Store responses in session state
                st.session_state.qry = sql_query
                st.session_state.chat_history.append(("assistant", conversational_answer))

            except Exception as e:
                st.error(f"Error processing SQL query: {e}")
        
        # Check if category is "02" (general conversation)
        elif category == "02":
            try:
                # Agent 3: Respond to general conversation
                conversation_response = general_conversation(user_input)

                # Store response in session state
                st.session_state.chat_history.append(("assistant", conversation_response))

            except Exception as e:
                st.error(f"Error in general conversation: {e}")
        
        # Additional logic for other categories if needed
        break  # Exit the loop after processing the first clicked history button

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
                st.session_state.chat_history.append(("assistant", bot_response))
                st.chat_message("assistant").markdown(bot_response)
                # st.write(f"General Conversation Response: {response}")


# Script for test 
# good morning
# i have a pen
# i want to know unique Product Id  
# i want to know sale person name and sale person average round trip hours 
# i want to know Branch Name Latitude Longitude by each country
# i want to know sales person name by each province


# i want to know product lens type and Quantity  of each lens type 
# thank you



