from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, function_tool
from agents.run import RunConfig
from dotenv import load_dotenv
import os
import requests
import chainlit as cl

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

external_client = AsyncOpenAI(
    api_key = gemini_api_key,
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai",
)

model = OpenAIChatCompletionsModel(
    model = "gemini-2.0-flash",
    openai_client = external_client,
)

config = RunConfig(
    model = model,
    model_provider = external_client,
    tracing_disabled = True,  
)

@function_tool
def get_product():

    """Get a product from an external API. fectches product data from a API endpoint."""

    url = "https://template6-six.vercel.app/api/products"

    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to fetch product data.")
    

shopping_agent = Agent(
    name = "ShoppingAgent",
    instructions = "you are a helpful Shopping Agent. You can search for products and provide recommendations based on user queries.",
    tools = [get_product],
    
)
# Chainlit setup

@cl.on_chat_start

async def start_massage():
    await cl.Message(content="""
                     🛒🛍 Welcome to the AI Shopping Agent! 🚀 Let's get started..
                     """).send()

#----------------

@cl.on_message

async def my_message(msg: cl.Message):
    user_input = msg.content 

    response = Runner.run_sync(
        shopping_agent,
        user_input,
        run_config = config
    )
    await cl.Message(
        content = response.final_output
    ).send()