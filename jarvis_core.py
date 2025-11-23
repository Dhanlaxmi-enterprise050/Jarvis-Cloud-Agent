# --- jarvis_core.py IMPORTS SECTION ---

import os
import base64
from io import BytesIO
from PIL import Image

# LangChain specific imports (Explicit paths to fix ImportErrors)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.agent_executor import AgentExecutor
from langchain.agents.structured_chat.base import create_structured_chat_agent
from langchain_core.prompts import ChatPromptTemplate
from browser_use.browser_use import BrowserUse

from dotenv import load_dotenv


async def execute_browser_task(text_prompt: str) -> dict:
    
    # 1. Initialize Tools and Model
    # Use headless=True for the server to avoid visible windows
    browser_use_tool = BrowserUse(
        selenium_url=None, 
        headless=True,
        browser="chromium"
    )
    tools = [browser_use_tool]

    # Model initialization
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.0
    )

    # 2. Define the Prompt (Instructs agent to use the browser and take a screenshot)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are Jarvis, an autonomous web browsing agent. You must use the provided BrowserUse tool to fulfill the user's request. After a successful action or search, always formulate a complete text answer for the user."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    # 3. Create the Agent
    agent = create_structured_chat_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    # 4. Execute the Task
    try:
        result = await agent_executor.ainvoke({"input": text_prompt})
        final_response_text = result.get("output", "Task completed, but no explicit final response was generated.")

        # 5. Capture Visual Proof (This is the key trick)
        screenshot_base64 = ""
        # BrowserUse saves the final screenshot to a specific path when it finishes
        screenshot_path = "browser_use_screenshot.png"

        if os.path.exists(screenshot_path):
            with open(screenshot_path, "rb") as image_file:
                # Convert image binary data to Base64
                screenshot_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Clean up the file
            os.remove(screenshot_path)
            
        return {
            "final_response": final_response_text,
            "screenshot_base64": screenshot_base64
        }
    
    except Exception as e:
        # Return a clean error message to the user
        error_message = f"Jarvis: Error - Task failed due to a system issue: {str(e)}"
        print(error_message)
        return {
            "final_response": error_message,
            "screenshot_base64": ""
        }
