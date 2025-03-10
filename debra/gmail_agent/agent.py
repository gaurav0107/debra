from gmail_manager.gmail_service import GmailService
from langchain_openai import ChatOpenAI
from .prompt import email_label_prompt, email_label_output_parser
from .config import EMAIL_LABELS, FETCH_MAX_EMAIL
from langchain_core.output_parsers import StrOutputParser


class GmailAgent:
    def __init__(self, email):
        self.email = email
        self.gmail_service = GmailService(email)
        self.llm = ChatOpenAI(model_name="gpt-4")
        self.chain = email_label_prompt | self.llm | email_label_output_parser

    def setup(self, labels):
        self.gmail_service.ensure_labels_exist(labels)
    


    def get_label_to_email(self, sender, subject, body):
        args_to_prompt = { 
            "labels_with_description": EMAIL_LABELS,
            "email_sender": sender,
            "email_subject": subject,
            "email_body": body
        }
        return self.chain.invoke(input=args_to_prompt)
    
    def label_email(self, msg):
        try:
            sender, subject, body = self.gmail_service.get_message_details(msg['id'])
            label = self.get_label_to_email(sender, subject, body)
            label_id = self.gmail_service.get_label_id_from_name(label.value)
            print(subject, label_id)
            self.gmail_service.add_label_to_message(msg['id'], label_id)
        except:
            pass

    def label_emails(self, query='category:primary'):
        # List messages based on the query
        messages = self.gmail_service.list_messages(query=query, fetch_max_email=FETCH_MAX_EMAIL)
        for msg in messages:
            self.label_email(msg)
            
            
    
    def run(self):
        # Define your query and label ID
        print(email_label_prompt)
        print(EMAIL_LABELS)
        self.setup(EMAIL_LABELS.keys())
        args_to_prompt = { 
            "labels_with_description": "",
            "email_sender": "",
            "email_subject": "",
            "email_body": ""
        }
        self.label_emails()
        # chain = self.prompt | self.llm 

if __name__ == "__main__":
    agent = GmailAgent("gauravdubey0907@gmail.com")
    agent.run()