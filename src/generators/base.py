from abc import ABC, abstractmethod


class VideoGenerator(ABC):

    @abstractmethod
    def generate(self, prompt: str, output_path: str) -> dict:
        pass