from agents import Agent ,Runner, OpenAIChatCompletionsModel,AsyncOpenAI,RunConfig
# from openai.types import ResponseTextDeltaEvent
import os
import chainlit  as cl
from dotenv import load_dotenv
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
    )

run_config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True,
)
agent = Agent(
    name="Frontend Expert"
)

@cl.on_chat_start
async def handle_chat_start():
    cl.user_session.set("history", [])
    await cl.Message(content="Welcome to the Frontend Expert Chat!").send()



@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history", [])
    history.append({ "role": "user", "content": message.content })

    msg = cl.Message(content="")
    await msg.send()
    

    result =  Runner.run_streamed(
        agent,
        input=history,
        run_config=run_config,
    )

    assistant_content = ""
    async for event in result.stream_events():
        if event.type == "raw_response_event":
            token = getattr(event.data, "delta", "")
            await msg.stream_token(token)
            assistant_content += token

    if assistant_content:
        history.append({ "role": "assistant", "content": assistant_content })
        cl.user_session.set("history", history)