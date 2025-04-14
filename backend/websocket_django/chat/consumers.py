import json
from channels.generic.websocket import WebsocketConsumer
from vertexai.generative_models import GenerationConfig, GenerativeModel, Part, Content
import logging
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from google.cloud import bigquery
import os
import redis
rcache = redis.StrictRedis(host='localhost', port=6379, db=0)

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.language = "english"
        self.accept()
        #------------------------------------------------ big query initialization -------------------------------------------
        self.json_key_path = r"E:\chatbot main\backend\websocket_django\websocket_django\sonata-sarthi-0adb780ba337.json"
        self.credentials = service_account.Credentials.from_service_account_file(self.json_key_path)
        self.bq_client = bigquery.Client(credentials=self.credentials, project=self.credentials.project_id)
        #------------------------------------------------ big query initialization end ---------------------------------------
        self.get_model()

    def disconnect(self, close_code):
        # Leave room group
        self.disconnect()

    

    def receive(self, text_data):
        start_time = datetime.now()
        data = json.loads(text_data)
        message = data['message']
        username = data['username']
        
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
        query_response = self.chat2.send_message([message, "Fild the category and other parameters for it."])
        print("HELLO",type(query_response))
        print("HELLO1",query_response)
        self.query_result =  query_response.text
        print("HELLO2",self.query_result)
        end_time_1 = datetime.now()
        match =  re.search(r'```sql\n(.*?)\n```', self.query_result, re.DOTALL)
        if match:
            self.query_result = match.group(1)
            print("hwalfjdlj",self.query_result)
        print(f"Time taken for response generation by our AI MODEL : {(end_time_1 - start_time_1).total_seconds()} seconds")
        
        # -------------------------------------- executing the query in big data -------------------------------------
        start_time_2 = datetime.now()
        db_results = self.bq_client.query(self.query_result).to_dataframe()
        output =  db_results.head(5).to_html(index=False)
        db_results_1 = db_results.head(5)
        interpreter_input = f"Database results for top 5 results also add a line that says for complete data downloand the file.: {db_results_1.to_json(orient='records')}"
        interpreter_response = self.chat1.send_message([interpreter_input, message])
        ai_response = interpreter_response.text
        print("HELLO \n",type(ai_response))
        end_time_2 = datetime.now()
        print(f"Time taken for response generation by big query: {(end_time_2 - start_time_2).total_seconds()} seconds")
        output = output + "\n\n" + ai_response
            
       
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
            DATE(timestamp) = DATE_SUB(CURRENT_DATE(), INTERVAL 0 DAY)
        LIMIT 100
        """
        try:
            db_question_results = self.bq_client.query(self.query_fetch_question).to_dataframe()
            interpreter_input = f"Database results: {db_question_results.to_json(orient='records')}"
            
            prompt = """
            Objective: Find the top 5 most frequently asked questions into a polite, structured response.
            
            You first have to categorize similar question together. Then, you have to count the frequency of each category
            then you have to return the top 5 categories.
            everything must be in lower case

            Input: A list of questions.
            Output: A formatted string with the questions listed as bullet points top 5. use only this '-' for bullet points also everything must be in lowercase strictly
            
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
        
        prompt_3="""
        You are a SQL and BigQuery expert.
        Your job is to create for BigQuery in SQL.
        STRICTLY CONSIDER PREVIOUS QUESTIONS CONDITIONS AS WELL TO ANSWER CURRENT QUESTION.
        
        Create a BigQuery SQL query for the following user input, using the below instructions.
        Note: Ensure that the answers to each question are influenced by the conditions and results obtained from the preceding questions.
        STRICTLY USE ALL FOLLOWING CONDTIONS PRESENT IN BELOW QUESTIONS.
        The user and the agent have done this conversation so far:
        
        STRICTLY MAKE QUERY FOR WHAT IS ASKED FOR NOTHING ELSE DONT INCLUDE EXTRA INFORMATION.
        STRICTLY DONT GIVE ANY OTHER COLUMNS THAT ARE NOT BEEN ASKED GIVE ONLY THOSE THAT ARE ASKED.
        
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
        self.query_model = GenerativeModel("gemini-1.5-flash-002", system_instruction=prompt_3)
        self.chat1 = self.interpreter_model.start_chat()
        self.chat2 = self.query_model.start_chat()
        
        logger.info("webSocket connection established")
        
        
        

# class ChatConsumerSonata(WebsocketConsumer):
#     def get_model(self):
#         prompt_1 = """
#         You are a helpful chatbot designed to process and present data in a clear and friendly manner. When the user provides a dictionary or a DataFrame as input, your task is to interpret the data and return it in a well-structured, natural-language format that is easy to read and understand. Follow these guidelines:
#         Input Handling:
#             Accept input in the form of a dictionary (e.g., {"name": "Alice", "age": 25, "city": "New York"}) or a DataFrame (e.g., a table with columns and rows).
#             If the input is unclear or malformed, politely ask the user to clarify or provide the data in a valid format.
#         Output Formatting:
#             Transform the data into a conversational, narrative-style response rather than a raw or technical dump.
#             Use complete sentences and proper grammar to describe the data.
#             Organize the information logically, such as grouping related items or summarizing key points.
#             Avoid using code syntax, tables, or bullet points unless the user explicitly requests them—focus on prose instead.
#             Make the tone friendly, engaging, and professional.
#         Examples:
#             For a dictionary like {"name": "Alice", "age": 25, "city": "New York"}, respond with:
#             "It looks like we have some information about a person named Alice. She’s 25 years old and lives in New York, a vibrant and bustling city!"
#             For a DataFrame like {"Name": ["Alice", "Bob"], "Age": [25, 30], "City": ["New York", "London"]}, respond with:
#             "Here’s what I found in the data: Alice is 25 years old and calls New York home, while Bob, who’s 30, resides in London. Two interesting people from two amazing cities!"
#         Edge Cases:
#             If the data is empty (e.g., {} or an empty DataFrame), respond with:
#             "It seems like there’s no data to share yet. Could you provide some details for me to work with?"
#             If the input contains complex nested structures, summarize where appropriate and offer to dive deeper if the user asks.
#             User Interaction:
#             If the user asks for a specific part of the data (e.g., “Tell me about the ages”), focus on that aspect while still keeping the response natural and flowing.
#             If the user requests a different format (e.g., a table or list), adapt the output accordingly while maintaining clarity.
#             Your goal is to make the data feel approachable and interesting, as if you’re telling a story about it. Let’s bring the numbers and facts to life!
#         """
        
#         prompt_3="""You are a SQL and BigQuery expert.
#         Your job is to create and execute a query for BigQuery in SQL.
#         STRICTLY CONSIDER PREVIOUS QUESTIONS CONDITIONS AS WELL TO ANSWER CURRENT QUESTION.
        
#         Create and run a BigQuery SQL query for the following user input, using the below instructions.
#         Note: Ensure that the answers to each question are influenced by the conditions and results obtained from the preceding questions.
#         STRICTLY USE ALL FOLLOWING CONDTIONS PRESENT IN BELOW QUESTIONS.
        
#         Follow these restrictions strictly:
#         - STRICTLY STRICTLY Use only table Customer_Scrub_Account_Botpurpose_Sonata.
#         - DO NOT REFERE ANY OUTSIDE TABLES AND DATA. STRICTLY REFERE ONLT SPECIFIED TABLES AND GENERATE QUERY FOR THAT.
#         - DO NOT USE ANY OTHER COLUMN OUTSIDE FROM TABLE SCHEMA
#         - Only return the result generated from query.
#         - To extract day, month, or year from "Last_Payment_Date" column, use extract method. 
#           e.g. CAST(EXTRACT(YEAR FROM DATEOPENED) AS STRING) = '2022'
#         - While generating any name for column, or result, DO NOT use "'", and Spaces inbetween words. Follow below example while assigning any name.
#             e.g. SELECT COUNT(*) AS Number_of_Loan_Application_ID
#         - In FROM, always use the full table path, using `sonata-sarthi` as project, `Customer_Scrub_Data` as dataset.
#         - Use following syntax to write query -  SELECT COLUMN1,COLUMN2 FROM `sonata-sarthi.Customer_Scrub_Data.Customer_Scrub_Account_raw_csv` as Customer_Scrub_Account_Botpurpose_Sonata WHERE CONDITION; 
#         - STRICTLY use only table Customer_Scrub_Account_raw_csv
#         - Customer_Scrub_Account_Botpurpose_Sonata table stores all loans taken by customers from Sonata in their lifetime.
#         - Strictly use where Credit_Grantor = "SONATA"
        
        
#        Customer_Scrub_Account_raw_csv table's schema explanation:
#             -"Loan_Application_ID" is Unique ID for each loan application.
#             -"Credit_Grantor" is Institution that granted the credit or loan.
#             -"Last_Payment_Date" is Date when the last payment was made.
#             -"Overdue_Amount" is Amount that is overdue on the loan.
#             -"Credit_Report_ID" is Unique ID for each credit report.
#             -"Customer_ID_Member_ID" is Unique customer identifier across reports.
#             -"Branch" is Branch associated with the loan application.
#             -"Kendra" is Group or center under which the customer is categorized.
#             -"Date_Reported" is The date when the credit details were last reported.
#             -"Ownership_Indicator" is Specifies ownership type (individual, joint, etc.).
#             -"Account_Status" is Current status of the account (active, closed, delinquent).
#             -"Disbursement_Date" is Date when the loan amount was disbursed.
#             -"Close_Date" is Date when the account was closed.
#             -"Credit_Limit_Sanctioned_Amount" is Total sanctioned credit limit.
#             -"Disbursed_Amount_High_Credit" is Highest credit utilized or disbursed.
#             -"Installment_Amount" is Monthly/periodic installment amount.
#             -"Current_Balance" is Outstanding balance on the loan or credit account.
#             -"Installment_Frequency" is Frequency of installment payments (monthly, quarterly).
#             -"Write_Off_Date" is Date when the loan was written off as a loss.
#             -"Write_Off_Amount" is Amount written off as a bad debt.
#             -"Asset_Class" is Classification of the asset (standard, NPA, etc.).
#             -"Account_Remarks" is Additional remarks related to the account.
#             -"Linked_Accounts" is Other accounts linked to the customer.
#             -"Reported_Date_Historical" is Historical record of reported dates.
#             -"DPD_Historical" is Days past due history for the account.
#             -"Asset_Class_Historical" is Historical changes in asset classification.
#             -"High_Credit_Historical" is Historical highest credit utilized.
#             -"Current_Balance_Historical" is Historical data of outstanding balances.
#             -"DAS_Historical" is Historical delinquency and settlement records.
#             -"Amount_Overdue_Historical" is History of overdue amounts.
#             -"Amount_Paid_Historical" is History of payments made over time.
#             -"Income" is Reported income of the customer.
#             -"Income_Indicator" is Indicator showing source/type of income.
#             -"Tenure" is Loan repayment tenure in months or years.
#             -"Occupation" is Employment type or profession of the borrower.
#             -"Unnamed_Column_41" is Unidentified or unused column in the dataset.
        
#         """
#         self.interpreter_model = GenerativeModel("gemini-1.5-flash-002", system_instruction=prompt_1)
#         self.query_model = GenerativeModel("gemini-1.5-flash-002", system_instruction=prompt_3)
#         self.chat1 = self.interpreter_model.start_chat()
#         self.chat2 = self.query_model.start_chat()
        
#         logger.info("webSocket connection established")
    
#     def connect(self):
#         self.language = "english"
#         self.accept()
        
#         #------------------------------------------------ big query initialization -------------------------------------------
#         self.json_key_path = r"E:\chatbot main\backend\websocket_django\websocket_django\sonata-sarthi-0adb780ba337.json"
#         self.credentials = service_account.Credentials.from_service_account_file(self.json_key_path)
#         self.bq_client = bigquery.Client(credentials=self.credentials, project=self.credentials.project_id)
#         self.get_model()

#     def disconnect(self, close_code):
#         # Leave room group
#         self.disconnect()

    

#     def receive(self, text_data):
#         start_time = datetime.now()
#         data = json.loads(text_data)
#         message = data['message']
#         username = data['username']
        
        
#         #------------------------------------------------ side bar top question ai generation --------------------------------
#         if message.lower() != "show top questions":
#             print(type(message))
#             query_daily_question = """
#             INSERT INTO `sonata-sarthi.Customer_Scrub_Data.daily_questions` (question, timestamp)
#             VALUES ('{}', '{}')
#             """.format(message, datetime.utcnow().isoformat())
#             query_job = self.bq_client.query(query_daily_question)
#             query_job.result()
            
#         if message.lower() == "show top questions":
#             top_questions = self.get_top_five_questions()
#             print(top_questions)
#             response = json.dumps({
#                 'type': 'top_questions',
#                 'top_questions': top_questions
#             })
#             self.send(response)
#             end_time = datetime.now()
#             logger.info(f"Time taken for top questions response for show top questions : {(end_time - start_time).total_seconds()} seconds")
#             return
        
        
#         # ------------------------------------- download csv for the last stored question -----------------------------------
#         global db_results
#         if message == "download_csv":
#             csv_data = self.generate_csv(db_results.to_dict('records'))
#             response = json.dumps({
#                 'type': 'csv_download',
#                 'csv_data': csv_data,
#                 'filename': f'chat_data_{start_time.strftime("%Y%m%d_%H%M%S")}.csv'
#             })
#             self.send(response)
        
        
#         # --------------------------------------finding query using our ai agent -------------------------------------------
#         start_time_1 = datetime.now()
#         query_response = self.chat2.send_message([message, "Fild the category and other parameters for it."])
#         print("HELLO",type(query_response))
#         print("HELLO1",query_response)
#         self.query_result =  query_response.text
#         print("HELLO2",self.query_result)
#         end_time_1 = datetime.now()
#         match =  re.search(r'```sql\n(.*?)\n```', self.query_result, re.DOTALL)
#         if match:
#             self.query_result = match.group(1)
#             print("hwalfjdlj",self.query_result)
#         print(f"Time taken for response generation by our AI MODEL : {(end_time_1 - start_time_1).total_seconds()} seconds")
        
#         # -------------------------------------- execting the query in big data -------------------------------------
#         start_time_2 = datetime.now()
#         db_results = self.bq_client.query(self.query_result).to_dataframe()
#         output =  db_results.head(5).to_html(index=False)
#         db_results_1 = db_results.head(5)
#         interpreter_input = f"Database results: {db_results_1.to_json(orient='records')}"
#         interpreter_response = self.chat1.send_message([interpreter_input, message])
#         ai_response = interpreter_response.text
#         print("HELLO \n",type(ai_response))
#         end_time_2 = datetime.now()
#         print(f"Time taken for response generation by big query: {(end_time_2 - start_time_2).total_seconds()} seconds")
#         output = output + "\n\n" + ai_response
            
       
#         response = json.dumps({
#             'type': 'chat_message',
#             'message': message,
#             'username': username,
#             'ai_response':output
#         })
#         self.send(response)
#         end_time = datetime.now()
#         print(f"END TIME: {end_time}")
#         print(f"Time taken for response generation: {(end_time - start_time).total_seconds()} seconds")
#         print(f"Total execution time: {(end_time - start_time).total_seconds()} seconds")
        
#     def chat_message(self, event):
#         message = event['message']
#         username = event['username']
#         ai_response = event['ai_response']

#         # Send message to WebSocket
#         self.send(text_data=json.dumps({
#             'message': message,
#             'username': username,
#             'ai_response': ai_response
#         }))
    
#     def generate_csv(self, data):
#         output = io.StringIO()
#         writer = csv.writer(output)
#         if data and len(data)>0:
#             writer.writerow(data[0].keys())
#             for row in data:
#                 writer.writerow(row.values())
#         return output.getvalue()
    
    
#     def get_top_five_questions(self):
#     # Query to get the previous day's questions and their frequency
#         print("Started with the get top 5 questions function")
#         self.query_fetch_question = f"""
#         SELECT 
#             question
#         FROM 
#             `sonata-sarthi.Customer_Scrub_Data.daily_questions`
#         WHERE 
#             DATE(timestamp) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
#         LIMIT 100
#         """
#         try:
#             db_question_results = self.bq_client.query(self.query_fetch_question).to_dataframe()
#             interpreter_input = f"Database results: {db_question_results.to_json(orient='records')}"
            
#             prompt = """
#             Objective: Find the top 5 most frequently asked questions into a polite, structured response.
            
#             You first have to categorize similar question together. Then, you have to count the frequency of each category
#             then you have to return the top 5 categories.
#             everything must be in lower case

#             Input: A list of questions.
#             Output: A formatted string with the questions listed as bullet points top 5. use only this '-' for bullet points also everything must be in lowercase strictly
            
#             STRICTLY GIVE THE POINTS IN THIS FORMAT
#             - LINE 1
#             - LINE 2
#             - LINE 3
#             - LINE 4
#             - LINE 5

#             Example:
#             Input: ["What is my balance?", "How do I pay?", "What is my balance?"] which will 100
#             Output: " - What is my balance?\n- How do I pay? " return top 5 most used
#             """
#             self.top_question_model = GenerativeModel("gemini-1.5-flash-002", system_instruction=prompt)
#             self.chat3 = self.top_question_model.start_chat()
#             interpreter_response = self.chat3.send_message(interpreter_input)
#             ai_response = interpreter_response.text
#             print(ai_response)
#             return ai_response
#         except Exception as e:
#             logger.error(f"Error fetching top questions: {e}")
#             return "Unable to retrieve the top questions due to a system error."