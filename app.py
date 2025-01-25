import asyncio
import logging
from openai import AsyncOpenAI
import os
import websockets
import time

# Set up API key
api_key = "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"  # Replace with your actual API key
os.environ["OPENAI_API_KEY"] = api_key

# Set timeout duration (in seconds)
TIMEOUT_DURATION = 60  # Change this value to whatever you prefer (e.g., 60 seconds)

async def chat_with_gpt():
    client = AsyncOpenAI(api_key=api_key)

    while True:  # Retry loop for reconnecting
        try:
            print("Attempting to connect to GPT-4...")
            async with client.beta.realtime.connect(model="gpt-4o-realtime-preview") as connection:
                await connection.session.update(session={'modalities': ['text']})

                print("Connected to GPT-4. Start chatting!")

                while True:
                    try:
                        start_time = time.time()  # Start the timer for user input timeout

                        # Get user input with timeout
                        user_input = await asyncio.wait_for(asyncio.to_thread(input, "You: "), timeout=TIMEOUT_DURATION)

                        # If no input within the timeout duration
                        if time.time() - start_time > TIMEOUT_DURATION:
                            print(f"Timeout exceeded: No input within {TIMEOUT_DURATION} seconds.")
                            continue  # Continue the loop to prompt for input again

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

                        # Function to handle the response processing
                        async def process_response():
                            async for event in connection:
                                if event.type == 'response.text.delta':
                                    print(event.delta, flush=True, end="")

                                elif event.type == 'response.text.done':
                                    print()  # Newline when done

                                elif event.type == "response.done":
                                    break  # Exit after response is complete

                        try:
                            # Wait for a response from the model
                            await asyncio.wait_for(process_response(), timeout=TIMEOUT_DURATION)
                        except asyncio.TimeoutError:
                            print(f"Timeout exceeded: No response within {TIMEOUT_DURATION} seconds.")
                            continue  # Continue to retry after timeout

                    except asyncio.TimeoutError:
                        print(f"Timeout exceeded: No input within {TIMEOUT_DURATION} seconds.")
                        continue  # Continue to retry after timeout

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection lost: {e}. Reconnecting...")
            await asyncio.sleep(5)  # Wait before trying to reconnect

        except Exception as e:
            print(f"An error occurred: {e}. Reconnecting...")
            await asyncio.sleep(5)  # Wait before trying to reconnect again

# Run the asyncio event loop
asyncio.run(chat_with_gpt())
