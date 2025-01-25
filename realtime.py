import asyncio
import logging
from openai import AsyncOpenAI
import os
import websockets

# Set up API key
api_key = "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"  # Replace with your actual API key
os.environ["OPENAI_API_KEY"] = api_key


async def chat_with_gpt():
    client = AsyncOpenAI(api_key=api_key)


    async with client.beta.realtime.connect(model="gpt-4o-realtime-preview") as connection:
        await connection.session.update(session={'modalities': ['text']})

        print("Connected to GPT-4. Start chatting!")

        while True:
            # Get user input
            user_input = input("You: ")

            # Exit if user types 'exit'
            if user_input.lower() == 'exit':
                print("Ending the conversation.")
                await connection.conversation.item.create(
                    item={
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "exit"}],
                    }
                )
                await connection.response.create()
                break

            # Send user input to the model
            await connection.conversation.item.create(
                item={
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": user_input}],
                }
            )
            await connection.response.create()

            # Process responses from the model in real-time
            async for event in connection:
                if event.type == 'response.text.delta':
                    print(event.delta, flush=True, end="")

                elif event.type == 'response.text.done':
                    print()  # Newline when done

                elif event.type == "response.done":
                    break  # Exit after response is complete

# Run the asyncio event loop
asyncio.run(chat_with_gpt())
