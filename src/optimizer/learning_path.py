import logging
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import json

logger = logging.getLogger("aithera.learning_path")

class Milestone(BaseModel):
    title: str = Field(..., description="Title of the milestone")
    description: str = Field(..., description="Description of what will be learned")
    estimated_minutes: int = Field(..., description="Estimated time to complete in minutes")
    topics: List[str] = Field(default_factory=list, description="Specific topics covered")

class PracticeTask(BaseModel):
    task_name: str = Field(..., description="Name of the practice task")
    description: str = Field(..., description="What the user needs to do")
    difficulty: str = Field(..., description="Difficulty level of the task")

class Project(BaseModel):
    project_name: str = Field(..., description="Name of the project")
    description: str = Field(..., description="Project description and requirements")
    skills_applied: List[str] = Field(default_factory=list, description="Skills used in this project")

class LearningPath(BaseModel):
    """Structured representation of a complete learning path."""
    topic: str = Field(..., description="The main topic of the learning path")
    target_audience: str = Field(..., description="The intended audience or difficulty level")
    prerequisites: List[str] = Field(default_factory=list, description="Required prior knowledge")
    milestones: List[Milestone] = Field(default_factory=list, description="Sequential learning milestones")
    practice_tasks: List[PracticeTask] = Field(default_factory=list, description="Tasks for practicing concepts")
    projects: List[Project] = Field(default_factory=list, description="Larger projects to apply knowledge")
    recommended_resources: List[str] = Field(default_factory=list, description="External resources for further learning")
    estimated_total_hours: float = Field(0.0, description="Estimated total hours to complete the path")
    difficulty_progression: str = Field(..., description="Description of how difficulty scales")

class LearningPathGenerator:
    """Generates comprehensive learning paths for given topics."""
    
    def generate_path_prompt(self, topic: str, difficulty: str = "beginner") -> str:
        """
        Generates a prompt that asks an LLM to produce a learning path in JSON format.
        
        Args:
            topic: The topic to learn.
            difficulty: The starting difficulty level.
            
        Returns:
            A prompt instructing the generation of a structured learning path.
        """
        prompt = f"""Design a comprehensive learning path for the topic: '{topic}'.
The target audience starting difficulty is '{difficulty}'.

Please structure your response as a JSON object that matches the following schema:
{{
  "topic": "string",
  "target_audience": "string",
  "prerequisites": ["string"],
  "milestones": [
    {{
      "title": "string",
      "description": "string",
      "estimated_minutes": int,
      "topics": ["string"]
    }}
  ],
  "practice_tasks": [
    {{
      "task_name": "string",
      "description": "string",
      "difficulty": "string"
    }}
  ],
  "projects": [
    {{
      "project_name": "string",
      "description": "string",
      "skills_applied": ["string"]
    }}
  ],
  "recommended_resources": ["string"],
  "estimated_total_hours": float,
  "difficulty_progression": "string"
}}

Ensure the progression is logical, starting from basics and moving to advanced concepts. The projects should be realistic and synthesize multiple milestones.
Respond ONLY with valid JSON.
"""
        return prompt

    def parse_path_response(self, response_text: str) -> Optional[LearningPath]:
        """
        Parses the JSON response from an LLM into a LearningPath object.
        
        Args:
            response_text: The raw text response containing JSON.
            
        Returns:
            A populated LearningPath object, or None if parsing fails.
        """
        try:
            # Try to extract JSON if it's wrapped in markdown blocks
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()
                
            data = json.loads(json_str)
            return LearningPath(**data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse learning path JSON: {e}")
            logger.debug(f"Raw response: {response_text}")
            return None
        except Exception as e:
            logger.error(f"Failed to validate learning path model: {e}")
            return None
