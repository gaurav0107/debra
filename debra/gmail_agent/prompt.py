from langchain.prompts import PromptTemplate
#from langchain_core.output_parsers import EnumOutputParser
from langchain.output_parsers.enum import EnumOutputParser

from .util import EmailCategory

email_label_output_parser = EnumOutputParser(enum=EmailCategory)


email_label_prompt = PromptTemplate(
            input_variables=["labels_with_description", "email_sender", "email_subject", "email_body"],
            partial_variables={"format_instructions": email_label_output_parser.get_format_instructions()},
            template="""
            You are an AI assistant responsible for analyzing email content and assigning appropriate labels based on the given categories. 
            Your goal is to accurately understand the email's intent, context, and subject matter to classify it correctly.
            here are the list of lables with there description:
            {labels_with_description}

            Email Content is as Follows:

            Email Sender: {email_sender}
            
            Subject: {email_subject}    

            Content: {email_body}

            Classify the email with the Labels prvided above, if you cannot decide return UNKNOWN  

            Strictly Use wither Lables shared above or UNKNOWN

            {format_instructions}

            """,

        )