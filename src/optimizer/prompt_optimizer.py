import re
import logging
from typing import List

logger = logging.getLogger("aithera.prompt_optimizer")

class PromptOptimizer:
    """Optimizes prompts for clarity, conciseness, and effectiveness."""

    def __init__(self):
        # Common redundant phrases
        self.redundant_phrases = [
            r"(?i)\bplease\b",
            r"(?i)\bcan you\b",
            r"(?i)\bwould you\b",
            r"(?i)\bcould you\b",
            r"(?i)\bI want you to\b",
            r"(?i)\bI need you to\b",
            r"(?i)\bmake sure to\b",
            r"(?i)\bit would be great if\b",
            r"(?i)\bas an AI language model\b"
        ]

    def optimize(self, prompt: str) -> str:
        """
        Runs the full optimization pipeline on a prompt.
        
        Args:
            prompt: The original prompt text.
            
        Returns:
            The fully optimized prompt.
        """
        if not prompt or not prompt.strip():
            return prompt

        logger.debug("Optimizing prompt")
        optimized = self.remove_redundancy(prompt)
        optimized = self.improve_readability(optimized)
        optimized = self.normalize_structure(optimized)
        
        return optimized

    def remove_redundancy(self, prompt: str) -> str:
        """Removes conversational filler and redundant phrases."""
        cleaned = prompt
        for phrase in self.redundant_phrases:
            cleaned = re.sub(phrase, "", cleaned)
        
        # Clean up double spaces created by removals
        cleaned = re.sub(r" +", " ", cleaned)
        
        # Remove duplicate sentences (simple exact match)
        sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', cleaned) if s.strip()]
        unique_sentences = []
        seen = set()
        for sentence in sentences:
            # Case-insensitive comparison for duplicates
            lower_s = sentence.lower()
            if lower_s not in seen:
                seen.add(lower_s)
                unique_sentences.append(sentence)
                
        return " ".join(unique_sentences).strip()

    def improve_readability(self, prompt: str) -> str:
        """Improves the readability and educational clarity of the prompt."""
        # Ensure sentences start with capital letters and trim whitespace
        sentences = []
        for s in re.split(r'(?<=[.!?]) +', prompt):
            s = s.strip()
            if s:
                s = s[0].upper() + s[1:]
                sentences.append(s)
        
        return " ".join(sentences).strip()

    def normalize_structure(self, prompt: str) -> str:
        """Standardizes formatting and instruction ordering."""
        # Convert multiple newlines to double newlines
        normalized = re.sub(r'\n{3,}', '\n\n', prompt)
        
        # Ensure lists are properly spaced
        normalized = re.sub(r'([^\n])\n- ', r'\1\n\n- ', normalized)
        normalized = re.sub(r'([^\n])\n\* ', r'\1\n\n* ', normalized)
        
        # Trim leading/trailing whitespace
        return normalized.strip()
