from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

from typing import Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import subprocess

class MyRunCommandSchema(BaseModel):
    """Input for MyRunCommandTool."""

    command: str = Field(
        ...,
        description="Command to be interpreted",
    )


class MyRunCommandTool(BaseTool):
    name: str = "Direct Command Interpreter"
    description: str = "Interprets bash command strings with a final print statement."
    args_schema: Type[BaseModel] = MyRunCommandSchema
    command: Optional[str] = None  


    def _run(self, **kwargs) -> str:
        command = kwargs.get("command", self.command)
        print(command)
        process = subprocess.run(command, capture_output=True, shell=True) 
        rc = process.returncode
        if rc != 0:
            return f"{process.stdout} {process.stderr}"
        
        return process.stdout