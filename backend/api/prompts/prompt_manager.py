from typing import Dict, Any, List, Optional
import os
import json
from pathlib import Path
from loguru import logger

class PromptManager:
    """Manages RetellAI agent prompts with template support"""
    
    def __init__(self):
        self.prompts_dir = Path(__file__).parent / "templates"
        self.prompts_dir.mkdir(exist_ok=True)
        self._prompts_cache = {}
    
    def get_prompt(self, prompt_name: str, variables: Optional[Dict[str, Any]] = None) -> str:
        """Get a prompt by name with optional variable substitution"""
        try:
            if prompt_name not in self._prompts_cache:
                self._load_prompt(prompt_name)
            
            prompt_template = self._prompts_cache[prompt_name]["template"]
            
            if variables:
                return self._substitute_variables(prompt_template, variables)
            
            return prompt_template
            
        except Exception as e:
            logger.error(f"Error getting prompt {prompt_name}: {str(e)}")
            raise
    
    def list_prompts(self) -> List[Dict[str, Any]]:
        """List all available prompts"""
        prompts = []
        
        for prompt_file in self.prompts_dir.glob("*.json"):
            try:
                with open(prompt_file, 'r') as f:
                    prompt_data = json.load(f)
                    prompts.append({
                        "name": prompt_file.stem,
                        "title": prompt_data.get("title", prompt_file.stem),
                        "description": prompt_data.get("description", ""),
                        "variables": prompt_data.get("variables", []),
                        "category": prompt_data.get("category", "general")
                    })
            except Exception as e:
                logger.error(f"Error loading prompt {prompt_file}: {str(e)}")
        
        return prompts
    
    def save_prompt(self, name: str, prompt_data: Dict[str, Any]) -> bool:
        """Save a prompt to disk"""
        try:
            prompt_file = self.prompts_dir / f"{name}.json"
            
            with open(prompt_file, 'w') as f:
                json.dump(prompt_data, f, indent=2)
            
            # Update cache
            self._prompts_cache[name] = prompt_data
            
            logger.info(f"Saved prompt: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving prompt {name}: {str(e)}")
            return False
    
    def delete_prompt(self, name: str) -> bool:
        """Delete a prompt"""
        try:
            prompt_file = self.prompts_dir / f"{name}.json"
            
            if prompt_file.exists():
                prompt_file.unlink()
                
                # Remove from cache
                if name in self._prompts_cache:
                    del self._prompts_cache[name]
                
                logger.info(f"Deleted prompt: {name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting prompt {name}: {str(e)}")
            return False
    
    def get_prompt_info(self, name: str) -> Dict[str, Any]:
        """Get detailed information about a prompt"""
        try:
            if name not in self._prompts_cache:
                self._load_prompt(name)
            
            return self._prompts_cache[name]
            
        except Exception as e:
            logger.error(f"Error getting prompt info {name}: {str(e)}")
            raise
    
    def _load_prompt(self, name: str) -> None:
        """Load a prompt from disk into cache"""
        prompt_file = self.prompts_dir / f"{name}.json"
        
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt '{name}' not found")
        
        with open(prompt_file, 'r') as f:
            self._prompts_cache[name] = json.load(f)
    
    def _substitute_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """Substitute variables in a prompt template"""
        result = template
        
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            result = result.replace(placeholder, str(value))
        
        return result
    
    def create_from_retell_agent(self, agent_name: str, retell_prompt: str, 
                                description: str = "", category: str = "retell") -> str:
        """Create a prompt template from a RetellAI agent"""
        prompt_data = {
            "title": f"{agent_name} Prompt",
            "description": description or f"Prompt for {agent_name} agent",
            "category": category,
            "template": retell_prompt,
            "variables": self._extract_variables(retell_prompt),
            "created_from": "retell_agent",
            "agent_name": agent_name
        }
        
        prompt_name = agent_name.lower().replace(" ", "_").replace("-", "_")
        
        if self.save_prompt(prompt_name, prompt_data):
            return prompt_name
        else:
            raise Exception("Failed to save prompt")
    
    def _extract_variables(self, template: str) -> List[Dict[str, str]]:
        """Extract variable placeholders from a template"""
        import re
        
        # Find all {variable_name} patterns
        variables = re.findall(r'\{(\w+)\}', template)
        
        return [
            {
                "name": var,
                "description": f"Variable: {var}",
                "type": "string",
                "required": True
            }
            for var in set(variables)  # Remove duplicates
        ]

# Create singleton instance
prompt_manager = PromptManager() 