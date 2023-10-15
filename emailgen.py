import os
import openai
import dotenv
from typing import List

from langchain.chains import LLMMathChain
from langchain.utilities import SerpAPIWrapper
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.tools import BaseTool, StructuredTool, Tool, tool

from rag import get_tool, create_query_tool

GPT_VERSION = "gpt-3.5-turbo"

dotenv.load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")
print(openai.api_key)

class EmailGenerator:
    def __init__(self, num_iterations, initial_prompt, company_name, company_kb_id, customer_name, customer_url: List[str]):
        # company_points: list[str] = get_company_info(company)
        # customer_points: list[str] = get_customer_info(customer)
        
        
        company_tool = create_query_tool(f"{company_name} website", f"Get info about {company_name} by asking ACTUAL QUESTIONS, e.g. 'What is ChatGPT for Enterprise' instead of 'ChatGPT for enterprise'", company_kb_id)
        
        
        # company_tool = get_tool(
        #     title=f"{company_name} website",
        #     description=f"Get info about {company_name} by asking ACTUAL QUESTIONS, e.g. 'What is ChatGPT for Enterprise' instead of 'ChatGPT for enterprise'",
        #     url_list=company_url_list
        # )
        company_llm = initialize_agent(
            [company_tool], ChatOpenAI(model_name=GPT_VERSION, temperature=0.9, max_tokens=1000), agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose = False
        )
        
        customer_tool = get_tool(f"{customer_name} website", f"Get info about {customer_name} by asking ACTUAL QUESTIONS, e.g. 'What is ChatGPT for Enterprise' instead of 'ChatGPT for enterprise'", customer_url)
        customer_llm = initialize_agent(
            [customer_tool], ChatOpenAI(model_name=GPT_VERSION, temperature=0.9, max_tokens=1000), agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose = False
        )
        
        
        company_points = company_llm.run(f"Explain who {company_name} is in detail. Then, generate a list of points about the solutions that {company_name} provides. Write in second person.")
        customer_points = customer_llm.run(f"Explain who {customer_name} is in detail. Then, generate a list of points about the problems that {customer_name} has. Write in second person.")
        # company_points = """
        # 1. OpenAI makes state-of-the-art language models
        # 2. OpenAI provides easy-to-use APIs to call out
        # """

        # customer_points = """
        
        # """
        self.customerAgent = CustomerAgent(customer_points, customer_llm)
        self.salesAgent = SalesAgent(company_points, company_llm)

        self.num_iterations = num_iterations
        self.initial_prompt = initial_prompt

        self.email = self._generate_initial(company_points, customer_points)

        print("INIT: finished init")

    def generate(self):

        for _ in range(self.num_iterations):
            print("EMAIL: iteration")
            customer_feedback = self.customerAgent.critique(self.email)
            sales_feedback = self.salesAgent.critique(self.email)

            self.email = self._refine(customer_feedback, sales_feedback)
            print("EMAIL: ", self.email)

        return self.email
    
    def _generate_initial(self, company_points, customer_points):
        message=[{"role": "user", "content": f"""
            Information about your company: {company_points}
            Information about your client: {customer_points}
        """}, {"role": "system", "content": self.initial_prompt}]
        response = openai.ChatCompletion.create(
            model=GPT_VERSION,
            messages = message,
            temperature=0.9,
            max_tokens=1000
        )
        print("EMAIL: generated initial email", response)
        return response

    def _refine(self, customer_feedback, sales_feedback) -> str:
        print("refine")
        prompt = f"""
        Here is your original email:
        {self.email}
        
        The customer has provided the following feedback:
        {customer_feedback}

        The sales team has provided the following feedback:
        {sales_feedback}

        Please rewrite the email according to these suggestions.
        """
        message=[{"role": "user", "content": prompt}, {"role": "system", "content": self.initial_prompt}]
        response = openai.ChatCompletion.create(
            model=GPT_VERSION,
            messages = message,
            temperature=0.7,
            max_tokens=1000
        )
        content = response["choices"][0]["message"]["content"]
        return content


class CustomerAgent:
    def __init__(self, initial_prompt, customer_llm):
        self.initial_prompt = initial_prompt # what the customer is
        self.customer_llm = customer_llm
    
    def critique(self, draft):
        """
        OpenAI API Call
        """
        prompt = f" Here is an email you receive: \n\n{draft}.\n\nPlease give a thorough critique on the above email. Explain exactly why the solutions the company provides are useless to you. Please number your critiques and classify each as MAJOR or MINOR."
        message=[{"role": "user", "content": prompt}, {"role": "system", "content": self.initial_prompt}]
        
        return self.customer_llm.run(message)


class SalesAgent:
    def __init__(self, initial_prompt, company_llm):
        self.initial_prompt = initial_prompt
        self.company_llm = company_llm
    
    def critique(self, draft):
        """
        OpenAI API Call
        """
        prompt = f" Here is an email your subordinate has sent: \n\n{draft}.\n\nPlease give a thorough critique on the above email. Explain exactly why the email does or does not represent the solutions the company can actually provide. Please number your critiques and classify each as MAJOR or MINOR."
        message=[{"role": "user", "content": prompt}, {"role": "system", "content": self.initial_prompt}]
        
        return self.company_llm.run(message)


if __name__ == "__main__":
    
    # company_url_list = [
    #     "https://glean.com/"
    #     "https://glean.com/product/overview/",
    #     "https://glean.com/product/workplace-search-ai",
    #     "https://glean.com/product/assistant",
    #     "https://glean.com/product/platform",
    #     "https://glean.com/product/knowledge-management"
    # ]
    company_kb_id = "f1970b8b-408b-4aa2-aefa-e0a1efa3bdbc"
    
    email_gen = EmailGenerator(
        num_iterations=3,
        initial_prompt="""
        You are an email-writing assistant that writes
        first-contact emails to potential clients.
        """,
        company_name="Glean",
        company_kb_id=company_kb_id,
        customer_name="Jane Street",
        customer_url=["https://www.janestreet.com/"]
    )


    msg = email_gen.generate()

    print(msg)
