# ma4

ma4 = multiagent for ...:

- Summarize the technical conferences from a playlist, create a ranking, and display it as an HTML page.

## Run

Prerequisites: docker and docker-compose

Create the ".env" file on the model ".env_example" in ./ma4 and change the value of OPENAI_API_KEY and MISTRAL_API_KEY with your mistral api key ( https://console.mistral.ai/ )

Run the program with the targeted playlist id (PLAYLIST_ID):

```
USER_ID=$(id -u) GROUP_ID=$(id -g) PLAYLIST_ID=PLTbQvx84FrAQ_SahOOqxsB9nH3FbuxiKe docker compose up --build  
```

Warning: Be aware of rights and licences !