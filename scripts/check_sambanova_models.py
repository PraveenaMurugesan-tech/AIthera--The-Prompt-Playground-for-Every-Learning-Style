import os
import sys
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

async def test_sambanova_models():
    """Test script to fetch available models from SambaNova."""
    api_key = os.getenv("SAMBANOVA_API_KEY")
    if not api_key:
        print("Error: SAMBANOVA_API_KEY is missing from environment variables.")
        sys.exit(1)

    print("Connecting to SambaNova API...")
    
    try:
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.sambanova.ai/v1"
        )
        
        print("\nFetching available models...")
        response = await client.models.list()
        
        models = response.data
        if not models:
            print("No models returned by the API.")
            return

        print(f"\nFound {len(models)} models:")
        print("-" * 50)
        
        valid_models = []
        for model in models:
            print(f"- ID: {model.id}")
            valid_models.append(model.id)
            
        print("-" * 50)
        
        # Recommend default model
        if valid_models:
            recommended = None
            for model in valid_models:
                # Prefer Llama 3 models if available
                if "llama-3" in model.lower():
                    recommended = model
                    break
            
            if not recommended:
                recommended = valid_models[0]
                
            print(f"\nRecommended SAMBANOVA_MODEL: {recommended}")
            print(f"To use it, update your .env file: SAMBANOVA_MODEL={recommended}")
            
    except Exception as e:
        print(f"\nError connecting to SambaNova: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_sambanova_models())
