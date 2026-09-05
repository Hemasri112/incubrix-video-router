from src.generators.base import VideoGenerator


class MockGenerator(VideoGenerator):

    def generate(self, prompt: str, output_path: str) -> dict:
        return {
            "status": "success",
            "generator": "mock",
            "prompt": prompt,
            "output_path": output_path
        }