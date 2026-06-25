import asyncio
import sys
import time
from src.providers.sambanova_client import SambaNovaClient
from src.providers.base_provider import ProviderConfig

async def test_sambanova_live():
    """Live test script for SambaNova provider."""
    print("Testing SambaNova live connection...")

    config = ProviderConfig(
        provider_name="SambaNova",
        role="creator",
        enabled=True
    )
    
    try:
        client = SambaNovaClient(config)
    except Exception as e:
        print(f"Failed to initialize SambaNovaClient: {str(e)}")
        sys.exit(1)

    print(f"Using model: {client.get_model_name()}")
    print("Sending prompt: 'Explain the concept of quantum entanglement briefly.'\n")

    start_time = time.time()
    try:
        response = await client.generate_response(
            prompt="Explain the concept of quantum entanglement briefly."
        )
        latency = time.time() - start_time
        
        print("=" * 50)
        print("SAMBANOVA RESPONSE:")
        print("=" * 50)
        print(response["choices"][0]["message"]["content"])
        print("=" * 50)
        print(f"Latency: {latency:.2f} seconds")
        print(f"Tokens Used: {response.get('usage', {}).get('total_tokens', 'N/A')}")
        print("Live test successful!")
        
    except Exception as e:
        print(f"\nAPI Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_sambanova_live())
