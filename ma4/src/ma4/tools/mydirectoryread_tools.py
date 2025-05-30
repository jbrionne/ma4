import os
from typing import Any, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class MyFixedDirectoryReadToolSchema(BaseModel):
    """Input for DirectoryReadTool."""


class MyDirectoryReadToolSchema(MyFixedDirectoryReadToolSchema):
    """Input for DirectoryReadTool."""

    directory: str = Field(..., description="Mandatory directory to list content")


class MyDirectoryReadTool(BaseTool):
    name: str = "List files in directory"
    description: str = (
        "A tool that can be used to recursively list a directory's content."
    )
    args_schema: Type[BaseModel] = MyDirectoryReadToolSchema
    directory: Optional[str] = None

    def __init__(self, directory: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if directory is not None:
            self.directory = directory
            self.description = f"A tool that can be used to list {directory}'s content."
            self.args_schema = MyFixedDirectoryReadToolSchema
            self._generate_description()

    def _run(
        self,
        **kwargs: Any,
    ) -> Any:
        directory = kwargs.get("directory", self.directory)
        if directory[-1] == "/":
            directory = directory[:-1]
        files_list = [
            f"{directory}/{(os.path.join(root.replace(directory, ''), filename).lstrip(os.path.sep))}"
            for root, dirs, files in os.walk(directory)
            for filename in files
        ]
        files = "\n- ".join(files_list)
        return f"- {files}"
