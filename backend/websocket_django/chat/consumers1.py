import json
from channels.generic.websocket import WebsocketConsumer
# from websocket_django.ai import get_ai_response  # Import AI response function

import os
import pandas
#import psycopg2
import json
import redis

# import by understandings
from vertexai.generative_models import GenerationConfig, GenerativeModel, Part, Content
import logging
from datetime import datetime




#imports from my file for better understanding
import json
from channels.generic.websocket import AsyncWebsocketConsumer
#from langchain.memory import ConversationBufferWindowMemory
#from langchain.agents import initialize_agent, AgentType
#from langchain_google_vertexai import ChatVertexAI
from google.cloud import bigquery
import os
#from dotenv import load_dotenv
import redis
import tabulate
# import psycopg2

# Load environment variables
#load_dotenv()
rcache = redis.StrictRedis(host='localhost', port=6379, db=0)

# Database connection (PostgreSQL)
# connection = psycopg2.connect(
#     database=os.getenv("DB_NAME"),
#     user=os.getenv("DB_USER"),
#     password=os.getenv("DB_PASSWORD"),
#     host=os.getenv("DB_HOST"),
#     port=os.getenv("DB_PORT")
# )
# cursor = connection.cursor()

# BigQuery setup
VERTEX_PROJECT = "verdant-lattice-425012-f6"
VERTEX_REGION = "us-central1"
BIGQUERY_DATASET = "Customer_Scrub_Data"
BIGQUERY_PROJECT = "sonata-sarthi"
credentials_path = r"C:\Users\Admin\Downloads\verdant-lattice-425012-f6-189acb3a46c1.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path


# Initialize BigQuery client
from google.oauth2 import service_account
json_key_path = r"E:\chatbot main\backend\websocket_django\websocket_django\sonata-sarthi-0adb780ba337.json"
credentials = service_account.Credentials.from_service_account_file(json_key_path)
bq_client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Vertex AI and LangChain setup (similar to your original code)
import vertexai
vertexai.init(project=VERTEX_PROJECT, location=VERTEX_REGION)
import re

import csv
import io
from channels.generic.websocket import WebsocketConsumer
import json


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class DwsfChatConsumer(WebsocketConsumer):
    def get_model(self):
        prompt_1 = """
        You are a helpful chatbot designed to process and present data in a clear and friendly manner. When the user provides a dictionary or a DataFrame as input, your task is to interpret the data and return it in a well-structured, natural-language format that is easy to read and understand. Follow these guidelines:

        Input Handling:
            Accept input in the form of a dictionary (e.g., {"name": "Alice", "age": 25, "city": "New York"}) or a DataFrame (e.g., a table with columns and rows).
            If the input is unclear or malformed, politely ask the user to clarify or provide the data in a valid format.
        Output Formatting:
            Transform the data into a conversational, narrative-style response rather than a raw or technical dump.
            Use complete sentences and proper grammar to describe the data.
            Organize the information logically, such as grouping related items or summarizing key points.
            Avoid using code syntax, tables, or bullet points unless the user explicitly requests them—focus on prose instead.
            Make the tone friendly, engaging, and professional.
        Examples:
            For a dictionary like {"name": "Alice", "age": 25, "city": "New York"}, respond with:
            "It looks like we have some information about a person named Alice. She’s 25 years old and lives in New York, a vibrant and bustling city!"
            For a DataFrame like {"Name": ["Alice", "Bob"], "Age": [25, 30], "City": ["New York", "London"]}, respond with:
            "Here’s what I found in the data: Alice is 25 years old and calls New York home, while Bob, who’s 30, resides in London. Two interesting people from two amazing cities!"
        Edge Cases:
            If the data is empty (e.g., {} or an empty DataFrame), respond with:
            "It seems like there’s no data to share yet. Could you provide some details for me to work with?"
            If the input contains complex nested structures, summarize where appropriate and offer to dive deeper if the user asks.
            User Interaction:
            If the user asks for a specific part of the data (e.g., “Tell me about the ages”), focus on that aspect while still keeping the response natural and flowing.
            If the user requests a different format (e.g., a table or list), adapt the output accordingly while maintaining clarity.
            Your goal is to make the data feel approachable and interesting, as if you’re telling a story about it. Let’s bring the numbers and facts to life!
        """
        prompt_2 = """
        You are an expert in categorizing SQL queries based on relevant parameters.
        Your job is to categorize query for BigQuery in SQL and extract relevant parameters.
        The following paragraph contains the schema of the table used for a query. It is encoded in JSON format.

        Categorize a BigQuery SQL query for the following user input, using the below instructions.
        STRICTLY USE ALL FOLLOWING CONDTIONS PRESENT IN BELOW QUESTIONS.
        The user and the agent have done this conversation so far

        STEP 1. Categorization: Identify the most relevant category based on the user input.
        STEP 2. Extract Parameters: Determine the required parameters from the input and structure them as key-value pairs.
        STEP 3. Output Format: Return the response in the following JSON-like structure:
        STRICTLY CREATE OUTPUT LIKE THIS -
          "category": "Category Name",
          "Zone": "Zone Name (if applicable)",
          "loan_classification": "Loan Classification (if applicable)",

        STRICTLY CATEGORY SHOULD BE IN ONE OF THIS LIKE (category1, category2, category3, category4, category5, category6, category7, category8, category9, category10, category11)
        STRICTLY GO THROUGH ALL THE CATEGORY THEN SELECT THE MOST RELEVANT ONE FROM THE LIST OF CATEGORIES
        STRICTLY loan_classification can be only one of the following - (NPA, WRITEOFF, GOOD , AR) NOTHING ELSE -- NPA/WRITEOFF IS NOT APPLICABLE IN THIS CONVERSATION
        STRICTLY zone can be only one of the following - (PATNA, PRAYAGRAJ, GORAKHPUR, JABALPUR, MUZAFFARPUR, MORADABAD)
        
        
        GO THROUGH ALL THE CATEGORY DEFINITION AND CHOOSE THE MOST CLOSELY MATCHING CATEGORY FROM THE LIST OF CATEGORIES
        THESE CATEGORY DEFINITION ARE GENERAL ONES
        FOR EG ---> ZONE WISE CUSTOMER COUNT IS SIMILAR TO NUMBER OF CUSTOMERS IN EACH ZONE

        Category List:
        category1:  ZONE WISE CUSTOMER COUNT 
        category2:  ZONE WISE CUSTOMER COUNT WHO ARE IN NPA 
        category3:  TYPE OF CUSTOMER AND THEIR COUNT IN DIFFERENT ZONE 
        category4:- NUMBER OF CUSTOMERS IN PATNA ZONE WHO ARE PAYING TO OTHER BANKS BUT NOT TO SONATA
        category5:  WHAT IS PRINCIPLE OUTSTANDING OF CUSTOMERS IN PATNA ZONE WHO ARE PAYING TO OTHER BANKS BUT NOT TO SONATA   
        category6:  NUMBER OF CUSTOMERS IN PATNA ZONE WHO ARE PAYING TO SONATA BUT NOT TO OTHER BANKS       
        category7:  WHAT IS PRINCIPLE OUTSTANDING OF CUSTOMERS IN PATNA ZONE WHO ARE PAYING TO SONATA BANKS BUT NOT TO OTHER    
        category8:  NUMBER OF CUSTOMERS IN PATNA ZONE WHO ARE IN NPA or WRITEOFF AND PAYING TO SONATA BUT NOT TO OTHER BANKS
        category9:  WHAT IS PRINCIPLE OUTSTANDING OF CUSTOMERS IN PATNA ZONE WHO ARE IN NPA or WRITEOFF AND PAYING TO SONATA BANKS BUT NOT TO OTHER
        category10: NUMBER OF CUSTOMERS IN PATNA ZONE WHO ARE IN NPA or WRITEOFF AND PAYING TO OTHER BANKS BUT NOT TO SONATA BANKS
        category11: WHAT IS PRINCIPLE OUTSTANDING OF CUSTOMERS IN PATNA ZONE WHO ARE IN NPA or WRITEOFF AND PAYING TO OTHER BANKS BUT NOT TO SONATA BANK

        STRICTLY SELECT FROM THE ABOVE CATEGORIES ONLY
        STRICTLY DONT GIVE OTHER AS CATEGORY 

        - STRICTLY Use only table Day_Wise_Summarised_Final_Geography_Hierarchy.
        - TAKE ALL THE NAMES IN ZONE REGION DIVISION IN UPPER CASE LIKE Prayagraj SHOULD BE PRAYAGRAJ.
        - HERE loan classification coulumn contains values as NPA.
        - HERE loan classification coulumn contains values as GOOD.
        - HERE loan classification coulumn contains values as Long_Pending. 
        - HERE loan classification coulumn contains values as AR.

        Follow these restrictions strictly:
        - DO NOT REFER ANY OUTSIDE TABLES AND DATA. STRICTLY REFER ONLY SPECIFIED TABLES AND GENERATE QUERY FOR THAT.
        - DO NOT REFER ANY COLUMN OUTSIDE THE TABLE USE ONLY THE BELOW SCHEMA TO ANSWER


        STRICTLY GIVE THE ouput like this only nothing else should be considered only this 

          "category": "Category Name",
          "Zone": "Zone Name (if applicable)",
          "loan_classification": "Loan Classification (if applicable)",


        Day_Wise_Summarised_Final_Geography_Hierarchy table's schema explanation:
            -Zone
            -DivisionID
            -Division
            -RegionID
            -Region
            -HubID
            -Hub
            -BranchID
            -Branch
            -As_On_Date
            -CustomerInfoID
            -DisbursementID
            -CustomerCode
            -CUSTOMER_ID
            -LOS_APP_ID
            -PERFORM_CNS_SCORE
            -PERFORM_CNS_SCORE_DESCRIPTION
            -Others_Last_Paid_Date
            -Sonata_Last_Paid_Date
            -Last_CREDIT_GRANTOR
            -Predicted
        """
        
        
        
        prompt_3="""
        You are a SQL and BigQuery expert.
        Your job is to create for BigQuery in SQL.
        STRICTLY CONSIDER PREVIOUS QUESTIONS CONDITIONS AS WELL TO ANSWER CURRENT QUESTION.
        
        Create a BigQuery SQL query for the following user input, using the below instructions.
        Note: Ensure that the answers to each question are influenced by the conditions and results obtained from the preceding questions.
        STRICTLY USE ALL FOLLOWING CONDTIONS PRESENT IN BELOW QUESTIONS.
        The user and the agent have done this conversation so far:
        
        STRICTLY MAKE QUERY FOR WHAT IS ASKED FOR NOTHING ELSE DONT INCLUDE EXTRA INFORMATION.
        
        - FOR FINDING CUSTOMERS PAYING TO OTHER BUT NOT SONATA IN PRAYAGRAJ:
             SELECT DISTINCT count(LOS_APP_ID)
             FROM  `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
            WHERE Others_Last_Paid_Date > Sonata_Last_Paid_Date AND ZONE = 'PRAYAGRAJ';

        - FOR FINDING ZONE WISE CUSTOMER COUNT STRICTLY USE THIS:
            SELECT Zone, COUNT(DISTINCT CustomerInfoID) as CustomerCount
            FROM `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
            ORDER BY Zone;

        -FOR FINDING ZONE WISE CUSTOMER COUNT WHO ARE IN NPA USE THIS:
            SELECT Zone, COUNT(DISTINCT CustomerInfoID) as NPACustomerCount 
            FROM `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
            WHERE loan_classification = 'NPA' 
            GROUP BY Zone 
            ORDER BY Zone;

        -FOR FINDING TYPE OF CUSTOMER AND THEIR COUNT IN PATNA ZONE STRICTLY USE THIS:
            SELECT loan_classification, COUNT(DISTINCT CustomerInfoID) as CustomerCount 
            FROM `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
            WHERE Zone = 'PATNA' 
            GROUP BY loan_classification 
            ORDER BY loan_classification;

        - FOR FINDING NUMBER OF CUSTOMERS IN PATNA ZONE WHO ARE PAYING TO OTHER BANKS BUT NOT TO SONATA:
             SELECT DISTINCT count(LOS_APP_ID)
             FROM  `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
            WHERE Others_Last_Paid_Date > Sonata_Last_Paid_Date AND ZONE = 'PATNA';


        - FOR FINDING WHAT IS PRINCIPLE OUTSTANDING OF CUSTOMERS IN PATNA ZONE WHO ARE PAYING TO OTHER BANKS BUT NOT TO SONATA   
              SELECT SUM(principle_outstanding) as PATNAPrincipleOutstanding
              FROM `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
              WHERE Others_Last_Paid_Date > Sonata_Last_Paid_Date AND Zone = 'PATNA';

        - FOR FINDING NUMBER OF CUSTOMERS IN PATNA ZONE WHO ARE PAYING TO SONATA BUT NOT TO OTHER BANKS
              SELECT DISTINCT count(LOS_APP_ID)
              FROM  `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
              WHERE Others_Last_Paid_Date < Sonata_Last_Paid_Date AND ZONE = 'PATNA';

        - FOR FINDING WHAT IS PRINCIPLE OUTSTANDING OF CUSTOMERS IN PATNA ZONE WHO ARE PAYING TO SONATA BANKS BUT NOT TO OTHER    
              SELECT SUM(principle_outstanding) as PATNAPrincipleOutstanding
              FROM `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
              WHERE Others_Last_Paid_Date < Sonata_Last_Paid_Date AND Zone = 'PATNA';

        - FOR FINDING NUMBER OF CUSTOMERS IN PATNA ZONE WHO ARE PAYING TO SONATA BUT NOT TO OTHER BANKS
              SELECT DISTINCT count(LOS_APP_ID)
              FROM  `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
              WHERE Others_Last_Paid_Date < Sonata_Last_Paid_Date AND ZONE = 'PATNA' AND loan_classification = 'NPA';

        - FOR FINDING WHAT IS PRINCIPLE OUTSTANDING OF CUSTOMERS IN PATNA ZONE WHO ARE PAYING TO SONATA BANKS BUT NOT TO OTHER
              SELECT SUM(principle_outstanding) as PATNAPrincipleOutstanding
              FROM `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
              WHERE Others_Last_Paid_Date < Sonata_Last_Paid_Date AND Zone = 'PATNA' AND  loan_classification = 'NPA';

        - FOR FINDING NUMBER OF CUSTOMERS IN PATNA ZONE WHO ARE IN NPA AND ARE PAYING TO OTHER BANKS BUT NOT TO SONATA 
            SELECT DISTINCT count(LOS_APP_ID)
            FROM  `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
            WHERE Others_Last_Paid_Date > Sonata_Last_Paid_Date AND ZONE = 'PATNA' AND loan_classification = 'NPA';

        - FOR FINDING WHAT IS PRINCIPLE OUTSTANDING OF CUSTOMERS IN PATNA ZONE WHO ARE IN NPA AND ARE PAYING TO OTHER BANKS BUT NOT TO SONATA     
               SELECT SUM(principle_outstanding) as PATNAPrincipleOutstanding
               FROM `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
               WHERE Others_Last_Paid_Date > Sonata_Last_Paid_Date AND Zone = 'PATNA' AND  loan_classification = 'NPA';

        - FOR FINDING NUMBER OF CUSTOMERS IN PATNA ZONE WHO ARE IN Writeoff AND ARE PAYING TO OTHER BANKS BUT NOT TO SONATA     
               SELECT DISTINCT count(LOS_APP_ID)
               FROM  `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
               WHERE Others_Last_Paid_Date > Sonata_Last_Paid_Date AND ZONE = 'PATNA' AND loan_classification = 'Long_Pending';

        - FOR FINDING WHAT IS PRINCIPLE OUTSTANDING OF CUSTOMERS IN PATNA ZONE WHO ARE IN Writeoff AND ARE PAYING TO OTHER BANKS BUT NOT TO SONATA
            SELECT SUM(principle_outstanding) as PATNAPrincipleOutstanding
            FROM `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
            WHERE Others_Last_Paid_Date > Sonata_Last_Paid_Date AND Zone = 'PATNA' AND  loan_classification = 'Long_Pending';

        - STRICTLY Use only table Day_Wise_Summarised_Final_Geography_Hierarchy.
        - TAKE ALL THE NAMES IN ZONE IN UPPER CASE LIKE Prayagraj SHOULD BE PRAYAGRAJ.
        - TAKE ALL THE NAMES IN REGION, DIVISION, BRANCH IN FIRST ALPHABET CAPITAL REST SHOULD BE SMALL LIKE Patna, Sitapur.
        - HERE loan classification coulumn contains values as NPA.
        - HERE loan classification coulumn contains values as GOOD.
        - HERE loan classification coulumn contains values as Long_Pending. 
        - HERE loan classification coulumn contains values as AR.
        
        - STRICTLY IF GIVEN A NUMBER TO FIND DETAILS USE THE CUSTOMERINFOID COLUMN THAT TOO IT IS INTEGER
        - DONT GIVE AVERAGE FOR ANY THING GIVE SUM INSTEAD ELSE LEAVE IT AVERAGE IS NOT ACCEPTED.

        Follow these restrictions strictly:
        - DO NOT REFER ANY OUTSIDE TABLES AND DATA. STRICTLY REFER ONLY SPECIFIED TABLES AND GENERATE QUERY FOR THAT.
        - DO NOT REFER ANY COLUMN OUTSIDE THE TABLE USE ONLY THE BELOW SCHEMA TO ANSWER


        Day_Wise_Summarised_Final_Geography_Hierarchy table's schema explanation:
            -Zone : string
            -DivisionID : string
            -Division : string
            -RegionID : string
            -Region : string
            -HubID : string
            -Hub : string
            -BranchID ; INT
            -Branch : string
            -As_On_Date : DATE
            -CustomerInfoID : INT
            -DisbursementID : INT
            -LoanType : INT
            -DisbursementDate : DATE
            -DisbursedAmt : INT
            -CenterID : INT
            -Centercode : string
            -CustomerCode : string
            -CenterName : string
            -ApplicantName : string
            -mobile_no : string
            -ProductName : string
            -UserID : INT
            -CenterMeetingDay : string
            -CenterMeetingTime : string
            -visited_status : string
            -present_status : string
            -pending_emi_date : DATE
            -latest_collected_date : DATE
            -user_dpd_max : INT
            -account_DPD : INT
            -user_arrear_max : INT
            -account_arrear : INT
            -Last_Month_User_DPD : INT
            -Last_Month_User_Arrear : INT
            -Total_Arrear : INT
            -Is_NPA_Before : INT
            -latest_3_emi_npa_flag : INT
            -pending_amount : INT
            -total_outstanding : INT
            -loan_classification : string
            -current_installment_ID : INT
            -current_installment_Amount : INT
            -upcoming_installment_ID
            -upcoming_installment_Amount
            -principle_outstanding : INT
            -principle_arrear
            -moratorium
            -longitude
            -latitude
            -RIC
            -User_Arrear
            -Loan_Recommendation
            -First_Time_Arrear_Clients
            -last_three_installment
            -CUSTOMER_ID
            -LOS_APP_ID
            -PERFORM_CNS_SCORE
            -PERFORM_CNS_SCORE_DESCRIPTION
            -NO_OF_INQUIRIES
            -PRI_NO_OF_ACCTS
            -SEC_NO_OF_ACCTS
            -PRI_ACTIVE_ACCTS
            -SEC_ACTIVE_ACCTS
            -PRI_OVERDU_ACCTS
            -SEC_OVERDUE_ACCTS
            -PRI_CURRENT_BALANCE
            -SEC_CURRENT_BALANCE
            -PRI_SANCTIONED_AMOUNT
            -SEC_SANCTIONED_AMOUNT
            -PRI_DISBURSED_AMOUNT
            -SEC_DISBURSED_AMOUNT
            -PRIMARY_INSTAL_AMT
            -SEC_INSTAL_AMT
            -NEW_ACCTS_IN_LAST_SIX_MONTHS
            -DELINQUENT_ACCTS_IN_LAST_SIX_MONTHS
            -AVERAGE_ACCT_AGE
            -CREDIT_HISTORY_LENGTH
            -Total_Grantor
            -Last_Disb_Date
            -payment_gap
            -Others_Last_Paid_Date
            -Sonata_Last_Paid_Date
            -DISBURSED_AMT
            -CURRENT_BAL
            -OVERDUE_AMT
            -Last_Disb_Amt
            -Last_CREDIT_GRANTOR
            -Remaning_Installments
            -Loan_Closing_Date
            -Other_Active_Accounts
            -Predicted
        """
        self.interpreter_model = GenerativeModel("gemini-1.5-flash-002", system_instruction=prompt_1)
        self.query_model = GenerativeModel("gemini-1.5-flash-002", system_instruction=prompt_2)
        self.chat1 = self.interpreter_model.start_chat()
        self.chat4 = self.query_model.start_chat()
        
        logger.info("webSocket connection established")
    
    def connect(self):
        self.language = "english"
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        self.disconnect()

    def select_category(self, result):
        print(result['ZONE'])
        query_dict = {
            "CATEGORY1": 
                """SELECT Zone, COUNT(DISTINCT CustomerInfoID) as CustomerCount 
                    FROM `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy` 
                    GROUP BY Zone 
                    ORDER BY Zone;""",
            "CATEGORY2": 
                """SELECT Zone, COUNT(DISTINCT CustomerInfoID) as NPACustomerCount 
                    FROM `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
                    WHERE loan_classification = '{}'
                    GROUP BY Zone 
                    ORDER BY Zone;""".format(result['LOAN_CLASSIFICATION']),
            "CATEGORY3": 
                """SELECT loan_classification, COUNT(DISTINCT CustomerInfoID) as CustomerCount 
                    FROM `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
                    WHERE Zone = '{}'
                    GROUP BY loan_classification 
                    ORDER BY loan_classification;""".format(result['ZONE']),
            "CATEGORY4": 
                """SELECT DISTINCT count(LOS_APP_ID)
                    FROM `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
                    WHERE Others_Last_Paid_Date > Sonata_Last_Paid_Date AND ZONE = '{}';""".format(result['ZONE']),
            "CATEGORY5": 
                """SELECT SUM(principle_outstanding) as PrincipleOutstanding
                    FROM `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
                    WHERE Others_Last_Paid_Date > Sonata_Last_Paid_Date AND Zone = '{}';""".format(result['ZONE']),
            "CATEGORY6": 
                """SELECT DISTINCT count(LOS_APP_ID)
                    FROM `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
                    WHERE Others_Last_Paid_Date < Sonata_Last_Paid_Date AND ZONE = '{}';""".format(result['ZONE']),
            "CATEGORY7": 
                """SELECT SUM(principle_outstanding) as Zone_PrincipleOutstanding
                    FROM `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
                    WHERE Others_Last_Paid_Date < Sonata_Last_Paid_Date AND Zone = '{}';""".format(result['ZONE']),
            "CATEGORY8": 
                """SELECT DISTINCT count(LOS_APP_ID)
                    FROM `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
                    WHERE Others_Last_Paid_Date < Sonata_Last_Paid_Date AND Zone = '{}' AND loan_classification = '{}';""".format(result['ZONE'], result['LOAN_CLASSIFICATION']),
            "CATEGORY9": 
                """SELECT SUM(principle_outstanding) as Zone_PrincipleOutstanding
                    FROM `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
                    WHERE Others_Last_Paid_Date < Sonata_Last_Paid_Date AND Zone = '{}' AND loan_classification = '{}';""".format(result['ZONE'], result['LOAN_CLASSIFICATION']),
            "CATEGORY10": 
                """SELECT DISTINCT count(LOS_APP_ID)
                    FROM `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
                    WHERE Others_Last_Paid_Date > Sonata_Last_Paid_Date AND Zone = '{}' AND loan_classification = '{}';""".format(result['ZONE'], result['LOAN_CLASSIFICATION']),
            "CATEGORY11": 
                """SELECT SUM(principle_outstanding) as Zone_PrincipleOutstanding
                    FROM `sonata-sarthi.Customer_Scrub_Data.Day_Wise_Summarised_Final_Geography_Hierarchy`
                    WHERE Others_Last_Paid_Date > Sonata_Last_Paid_Date AND Zone = '{}' AND loan_classification = '{}';""".format(result['ZONE'], result['LOAN_CLASSIFICATION']),
                   
        }
        return query_dict[result['CATEGORY']]

    def receive(self, text_data):
        start_time = datetime.now()
        data = json.loads(text_data)
        message = data['message']
        username = data['username']
        
        #------------------------------------------------ big query initialization -------------------------------------------
        self.json_key_path = r"E:\chatbot main\backend\websocket_django\websocket_django\sonata-sarthi-0adb780ba337.json"
        self.credentials = service_account.Credentials.from_service_account_file(self.json_key_path)
        self.bq_client = bigquery.Client(credentials=self.credentials, project=self.credentials.project_id)
        self.get_model()
        
        #------------------------------------------------ side bar top question ai generation --------------------------------
        if message.lower() != "show top questions":
            print(type(message))
            query_daily_question = """
            INSERT INTO `sonata-sarthi.Customer_Scrub_Data.daily_questions` (question, timestamp)
            VALUES ('{}', '{}')
            """.format(message, datetime.utcnow().isoformat())
            query_job = self.bq_client.query(query_daily_question)
            query_job.result()
            
        if message.lower() == "show top questions":
            top_questions = self.get_top_five_questions()
            print(top_questions)
            response = json.dumps({
                'type': 'top_questions',
                'top_questions': top_questions
            })
            self.send(response)
            end_time = datetime.now()
            logger.info(f"Time taken for top questions response for show top questions : {(end_time - start_time).total_seconds()} seconds")
            return
        
        
        
        
        # ------------------------------------- download csv for the last stored question -----------------------------------
        global db_results
        if message == "download_csv":
            csv_data = self.generate_csv(db_results.to_dict('records'))
            response = json.dumps({
                'type': 'csv_download',
                'csv_data': csv_data,
                'filename': f'chat_data_{start_time.strftime("%Y%m%d_%H%M%S")}.csv'
            })
            self.send(response)
        
        
        # --------------------------------------finding query using our ai agent -------------------------------------------
        start_time_1 = datetime.now()
        query_response = self.chat4.send_message([message, "Fild the category and other parameters for it."])
        print("HELLO",type(query_response))
        print("HELLO1",query_response)
        self.query_result =  query_response.text
        print("HELLO2",self.query_result)
        end_time_1 = datetime.now()
        match =  re.search(r'```sql\n(.*?)\n```', self.query_result, re.DOTALL)
        if match:
            self.query_result = match.group(1)
            print("dwsf chat consumer is working ",self.query_result)
        print(f"Time taken for response generation by our AI MODEL : {(end_time_1 - start_time_1).total_seconds()} seconds")
        
        # -------------------------------------- execting the query in big data -------------------------------------
        
        start_index = self.query_result.find('{')
        end_index = self.query_result.rfind('}') + 1
        json_substring = self.query_result[start_index:end_index]
        objectt = json.loads(json_substring)

        
        uppercase_json = {k.upper(): (v.upper() if isinstance(v, str) else v) for k, v in objectt.items()}
        
        category = uppercase_json['CATEGORY']
        print(category)
        
        if(uppercase_json['CATEGORY'] == 'CATEGORY12'):
            interpreter_response = self.chat1.send_message("no data found")
            ai_response = interpreter_response.text
        else:
            start_time_2 = datetime.now()
            sql_query = self.select_category(uppercase_json)
            print(sql_query)
            if not sql_query:
                ai_response = "Unable to process your request due to an invalid category."
            else:
                db_results = self.bq_client.query(sql_query).to_dataframe()
                print(db_results)
                if db_results is None:
                    ai_response = "Unable to retrieve data due to a system error. Please try again later."
                    print("HELLO \n",ai_response)
                else:
                    db_results_1 = db_results.head(5)
                    interpreter_input = f"Database results: {db_results_1.to_json(orient='records')}"
                    interpreter_response = self.chat1.send_message([interpreter_input, message])
                    ai_response = interpreter_response.text
                    output =  db_results.head(5).to_html(index=False)
                    output = output + "\n\n" + ai_response
                    print("HELLO \n",ai_response)
            end_time_2 = datetime.now()

            print(f"Time taken for response generation by big query: {(end_time_2 - start_time_2).total_seconds()} seconds")
           
        response = json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username,
            'ai_response':output
        })
        self.send(response)
        end_time = datetime.now()
        
 
        
        print(f"END TIME: {end_time}")
        print(f"Time taken for response generation: {(end_time - start_time).total_seconds()} seconds")
        print(f"Total execution time: {(end_time - start_time).total_seconds()} seconds")
        
    def chat_message(self, event):
        message = event['message']
        username = event['username']
        ai_response = event['ai_response']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'ai_response': ai_response
        }))
    
    def generate_csv(self, data):
        output = io.StringIO()
        writer = csv.writer(output)
        if data and len(data)>0:
            writer.writerow(data[0].keys())
            for row in data:
                writer.writerow(row.values())
        return output.getvalue()
    
    
    def get_top_five_questions(self):
    # Query to get the previous day's questions and their frequency
        print("Started with the get top 5 questions function")
        self.query_fetch_question = f"""
        SELECT 
            question
        FROM 
            `sonata-sarthi.Customer_Scrub_Data.daily_questions`
        WHERE 
            DATE(timestamp) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
        LIMIT 100
        """
        try:
            # query_job = self.bq_client.query(query)
            # print(query_job)
            # results = query_job.result()
            # print(results)
            # top_questions = [row.question for row in results]
            
            db_question_results = self.bq_client.query(self.query_fetch_question).to_dataframe()
            # output_question_results =  db_question_results.head(5).to_html(index=False)
            # db_question_results_1 = db_question_results.head(5)
            interpreter_input = f"Database results: {db_question_results.to_json(orient='records')}"
            
            

            # Pass to AI model for formatting
            prompt = """
            Objective: Find the top 5 most frequently asked questions into a polite, structured response.
            
            You first have to categorize similar question together. Then, you have to count the frequency of each category
            then you have to return the top 5 categories.

            Input: A list of questions.
            Output: A formatted string with the questions listed as bullet points top 5. use only this '-' for bullet points.
            
            STRICTLY GIVE THE POINTS IN THIS FORMAT
            - LINE 1
            - LINE 2
            - LINE 3
            - LINE 4
            - LINE 5

            Example:
            Input: ["What is my balance?", "How do I pay?", "What is my balance?"] which will 100
            Output: " - What is my balance?\n- How do I pay? " return top 5 most used
            """
            self.top_question_model = GenerativeModel("gemini-1.5-flash-002", system_instruction=prompt)
            self.chat3 = self.top_question_model.start_chat()
            interpreter_response = self.chat3.send_message(interpreter_input)
            ai_response = interpreter_response.text
            print(ai_response)
            return ai_response
        except Exception as e:
            logger.error(f"Error fetching top questions: {e}")
            return "Unable to retrieve the top questions due to a system error."
            
        
        
    
        
    
        
            
        
   
        
        
