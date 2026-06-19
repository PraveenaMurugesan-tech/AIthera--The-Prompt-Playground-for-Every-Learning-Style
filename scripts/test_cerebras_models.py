import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

async def main():
    load_dotenv()
    
    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key:
        print("CEREBRAS_API_KEY not found in environment.")
        return

    client = AsyncOpenAI(
        base_url="https://api.cerebras.ai/v1",
        api_key=api_key
    )

    print("Fetching available Cerebras models...")
    try:
        models = await client.models.list()
        print("\nAvailable models:")
        for model in models.data:
            print(f"- {model.id}")
            
    except Exception as e:
        print(f"Error fetching models: {e}")

if __name__ == "__main__":
    asyncio.run(main())
