from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai import LLM



from ma4.tools.custom_command_tool import MyRunCommandTool
from ma4.tools.myfilewriter_tools import MyFileWriterTool
from ma4.tools.myfileread_tools import MyFileReadTool
from ma4.tools.mydirectoryread_tools import MyDirectoryReadTool
from ma4.tools.youtubeloader_tool  import MyYoutubeLoaderTool

import warnings

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
from crewai.telemetry import Telemetry

def noop(*args, **kwargs):
    # with open("./logfile.txt", "a") as f:
    #     f.write("Telemetry method called and noop'd\n")
    pass


for attr in dir(Telemetry):
    if callable(getattr(Telemetry, attr)) and not attr.startswith("__"):
        setattr(Telemetry, attr, noop)


# import litellm
# litellm._turn_on_debug() # 👈 this is the 1-line change you need to make
import json
def my_custom_logging_fn(model_call_dict):
    print("XXXXXXXXXX " + model_call_dict['log_event_type'])
    if "pre_api_call" == model_call_dict['log_event_type']:
        print("curl --location \"https://api.mistral.ai/v1/chat/completions\"  --header 'Content-Type: application/json' --header 'Accept: application/json' --header \"Authorization: Bearer $MISTRAL_API_KEY\" -d '{ \"model\": \"mistral-large-latest\", \"messages\":" + json.dumps(model_call_dict['input']).replace("'","'\\\''") + ", \"temperature\": 0, \"top_p\": 1, \"stop\": [\"\\nObservation:\"] }' | jq . ")


myRunCommandTool = MyRunCommandTool()
myFileWriterTool = MyFileWriterTool()
myFileReadTool = MyFileReadTool()
myDirectoryReadTool = MyDirectoryReadTool()
myYoutubeLoaderTool = MyYoutubeLoaderTool()


from pydantic import BaseModel

class Note(BaseModel):
    title: str
    evaluation: str
    score: str
    theme: str


@CrewBase
class Ma4ProgramGenYoutube():    

    def task_resume(self, output_filename: str) -> Task:
        task = Task(
            description="""Create the summary with the text after the example with following key elements:

0. Set the url video at the beginning of the file : {video_url}
1. Introduction: Briefly present the topic and its importance.
2. Objectives: State the objectives of the presentation.
3. Key Points: The main points covered in the presentation. Keep the critical or important information.
4. Methodology: Briefly describe the methods or technologies used.
5. Results: Highlight important results or conclusions.
6. Conclusion: End with a conclusion that summarizes the impact or implications of the results.

The summary must be in french.
Please analyze the summary. If any elements are missing, improve the summary. The summary must be in french.


### Example ###

{video_url}

**Introduction** : <Introduction>

**Objectifs** : <The Objectives>

**Points Clés** :
- <Key point 1>
- <Key point 2>
- <Key point X>

**Méthodologie** : <The Methodology>

**Résultats** : <The Results>

**Conclusion** : <The Conclusion>

### End Example ###

{input_file}
---------

{input_content}


""",
            expected_output="""The summary of the presentation""",
            agent=self.agent_expert(),
            output_file=output_filename
        )
        return task


    @agent
    def agent_expert(self) -> Agent:
        return Agent(
            role="Information technology expert",
            goal="""Resume technical presentation.""",
            backstory="You are an information technology expert.",
            allow_delegation=False,
            verbose=True,       
            llm = LLM(
                model="mistral/mistral-large-latest",
                temperature=0,
                top_p=1,
                logger_fn=my_custom_logging_fn
            )
        )


    @crew
    def crew(self, output_filename: str) -> Crew:  
        return Crew(
            agents=self.agents,
            tasks=[self.task_resume(output_filename)],
            process=Process.sequential,
            verbose=True,
            memory=False,
            max_rpm=7
        )


@CrewBase
class Ma4ProgramGenYoutubeSummary():


    def task_resume(self, output_filename: str) -> Task:
        task = Task(
            description="""You are an information technology expert tasked with evaluating the significance of a technical presentation summary. Assign a score out of 30.
Be very critical and demanding. Focus on evaluating technical content. Penalizes presentations that are too superficial on concepts. 
Explain your evaluation in french with text example and return the final score out of 30 as a json. 

Use the following scale:
- 0 to 5: The presentation introduces basic technical concepts but lacks depth and engagement. Key points are missing or poorly explained.
- 6 to 10: The presentation is competent, addressing relevant topics with some level of detail, though explanations may be unclear or lack thoroughness.
- 11 to 15: The presentation demonstrates a good understanding of technical concepts, providing adequate examples, but some sections could benefit from additional clarity.
- 16 to 20: The presentation is strong, showcasing comprehensive coverage and insightful analysis of relevant topics, with clear examples that enhance understanding.
- 21 to 25: The presentation is very strong, featuring expert-level insights and a well-structured approach that engages the audience effectively.
- 26 to 30: The presentation is exceptional, offering in-depth analysis, innovative concepts, and thorough explanations that provoke discussion and significantly enhance audience engagement.


Add also the theme of technical presentation of the list:

- Architecture
- Data & IA
- Deployment
- Development
- Front-end
- Java & Languages
- Mind the Geek
- People & Culture
- Security
- Server Side

Example:

```
{
"title" : "{input_file}"
"evaluation": "<The one sentence evaluation in french>",
"score": "<the final score out of 30, only the score like :  16 >"
"theme": "<the theme of the list. Respect the list>"
}
```

{input_file}
---------

{input_content}
""",
            expected_output="""Json of the evaluation""",
            agent=self.agent_expert(),
            output_json=Note,
            output_file=output_filename
        )
        return task


    @agent
    def agent_expert(self) -> Agent:
        return Agent(
            role="Information technology expert",
            goal="""Evaluate the significance of a technical presentation summary.""",
            backstory="You are an information technology expert.",
            allow_delegation=False,
            verbose=True,      
            llm = LLM(
                model="mistral/mistral-large-latest",
                temperature=0,
                top_p=1,
                logger_fn=my_custom_logging_fn
            )
        )


    @crew
    def crew(self, output_filename: str) -> Crew:    
        return Crew(
            agents=self.agents,
            tasks=[self.task_resume(output_filename)],
            process=Process.sequential,
            verbose=True,
            memory=False,
            max_rpm=7
        )

@CrewBase
class Ma4ProgramGen():


    @agent
    def coding_agent(self) -> Agent:
        coding_agent = Agent(
            role="Python Code Specialist",
            goal="Write Python code that is clean, efficient, and well-documented. Ensure the code adheres to best practices, including proper indentation, meaningful variable names, and modular design. The code should be optimized for performance and maintainability. Include comprehensive comments and docstrings to explain the purpose and functionality of the code. The final output should be a complete, executable Python script that meets the specified requirements of the task. Write Python Code. You cas execute pip install command. Following the example: \n\npip install -r requirements.txt\n\nYou can execute pytest command.",
            backstory="""You have extensive experience in software development, with a particular focus on Python programming. Over the years, you have honed your skills by working on a variety of projects, from simple scripts to complex applications. Your journey in Python began with writing small automation scripts, which eventually led to developing large-scale web applications and data analysis tools.
You are known for your ability to write clean, efficient, and well-documented code. You believe that code readability and maintainability are as important as functionality. You have a deep understanding of Python's syntax and best practices, and you always strive to optimize your code for performance.
Your approach to coding is methodical and structured. You start by understanding the requirements and then break down the problem into smaller, manageable tasks. You write modular code, ensuring that each function or class has a single responsibility. You are meticulous about including comprehensive comments and docstrings, making your code easy to understand and maintain.
You have a strong commitment to continuous learning and staying updated with the latest developments in Python. You regularly participate in coding challenges and contribute to open-source projects, which has further enhanced your skills and knowledge.
In your role as a Python Code Specialist, you have consistently delivered high-quality code that meets the needs of the project. Your experience and expertise make you a valuable asset to any development team.""",
            allow_delegation=False,
            allow_code_execution=False,
            verbose=True,
            tools=[myFileReadTool, myDirectoryReadTool],
            llm = LLM(
                model="mistral/codestral-latest",
                temperature=0,
                top_p=1,
                logger_fn=my_custom_logging_fn
            )
        )
        return coding_agent


    def agent_writer_task(self, output_filename: str) -> Task:
        # Define your task
        task = Task(
           description="""Generate only the html page code which display all the different ranking:
- ./classement_.json

The entries in ranking (classement_.json) have the json structure :

```
  {
    "title": "summary_kubernetes-in-2025-alain-regnier-kubo-labs.md",
    "evaluation": "La présentation est exceptionnelle, offrant une analyse approfondie, des concepts innovants, et des explications exhaustives qui stimulent la discussion et améliorent considérablement l'engagement du public. Par exemple, la présentation couvre des sujets techniques avancés comme les CRD, les opérateurs, Kubectl Debug, la Gateway API, le CSI, l'EBPF, le CEL, le partage de GPU, les Image Volumes, les requests et limites au niveau du pod, les files d'attente, les applications stateful, le templating avec Customize, les stacks d'observabilité, la Cluster API, le CRO, le Secret Store CSI Driver et KubeStellar, avec des démonstrations en direct et des exemples de code.",
    "score": "28",
    "theme": "Deployment"
  },
```

Transform the json into html. Add link for each entry to the corresponding summary. example:

```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rankings</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { text-align: center; }
        .ranking { margin-bottom: 20px; }
        .ranking h2 { margin-bottom: 10px; }
        .entry { margin-bottom: 10px; }
        .entry a { text-decoration: none; color: #007BFF; }
        .entry a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Rankings</h1>
    <div class="ranking">
        <h2>Conference</h2>
        <div class="entry">
            <a href="./summary_kubernetes-in-2025-alain-regnier-kubo-labs.md">summary_kubernetes-in-2025-alain-regnier-kubo-labs.md</a>
            <p>Score: 28</p>
            <p>Theme: Deployment</p>
        </div>
        ...
    </div>
    <div class="ranking">
        <h2>English Talks</h2>
        <div class="entry">
        ....
        </div>
    </div>
...
</body>
</html>

```        

Write the raw html output without additionnal information like "```html"
""",
           expected_output="""Html page""",
            agent=self.coding_agent(),
           output_file=output_filename
        )
        return task



    @crew
    def crew(self, output_filename: str) -> Crew:    
        return Crew(   
            agents=self.agents,
            tasks=[self.agent_writer_task(output_filename)],
            process=Process.sequential,
            verbose=True,
            memory=False,
            max_rpm=7
        )


import unicodedata
import re
def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')




if __name__ == "__main__":

    # 0. Which YouTube video playlist would you like to create summaries and rankings for? (ex: playlist id: PLTbQvx84FrAQ_SahOOqxsB9nH3FbuxiKe )
    import os
    playlist_id = os.environ.get('PLAYLIST_ID')
    if not playlist_id:
        print("No PLAYLIST_ID in environment variable")
        exit(1)

    # 1. Get all videos ids of the playlist
    listVideosOutput = myRunCommandTool._run(command="""yt-dlp --flat-playlist --print '{"title":"%(title)s","url":"%(id)s"}'  https://www.youtube.com/watch?list=""" + playlist_id)
    lstDictVideo = listVideosOutput.splitlines()

    print(lstDictVideo)

    for dictVideo in lstDictVideo:
        element = json.loads(dictVideo)
        element["title"] = slugify(element["title"])
        element["url"] = "https://www.youtube.com/watch?v=" + element["url"]
        try:

            # 2. Get the transcript of videos
            content=myYoutubeLoaderTool._run(url=element["url"], language="fr")
            myFileWriterTool._run(filename=element["title"], directory = "./", overwrite="False", content=content)
           
            # 3. Create summaries
            input_content = myFileReadTool._run(file_path="./" + element["title"])
            summary_file = 'summary_' + element["title"] + '.md'
            datasets = { 'input_file' : element["title"], 'video_url' :   element["url"], 'input_content' :  input_content}
            Ma4ProgramGenYoutube().crew(summary_file).kickoff(inputs=datasets)

            # 4. Give notes on summaries
            input_content = myFileReadTool._run(file_path="./" + summary_file)
            if not input_content.startswith("Error:"):
                datasets = { 'input_file' : summary_file, 'input_content' :  input_content}
                Ma4ProgramGenYoutubeSummary().crew('note_' + element["title"] + '.json').kickoff(inputs=datasets)
        
        except Exception as e:
            print(e)

    # 5. Ranking
    print(myRunCommandTool._run(command="""jq -s '.|{"notes":map(.)}' *.json | jq '.notes|sort_by(.score|tonumber)|reverse' > classement_.json"""))

    # 6. Generate html
    Ma4ProgramGen().crew('index.html').kickoff(inputs={})