import asyncio
import traceback
import sys
from src.council.live_council import LiveCouncil
from src.models.prompt_request import PromptRequest

async def test_image():
    with open("test_image_flow_output.txt", "w", encoding="utf-8") as f:
        try:
            council = LiveCouncil()
            req = PromptRequest(
                topic="test topic",
                learning_style="visual",
                difficulty="beginner",
                image_data="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
                task_type="learning",
                intent="learn"
            )
            setattr(req, "modality", "image")
            result = await council.execute(req)
            f.write(f"Success: {result}")
        except Exception as e:
            f.write("Error encountered!\n")
            f.write(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_image())
