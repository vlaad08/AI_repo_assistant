# CLI AI Repo Assistant

 A cli that helps with questions related to repositories. 

You can ask questions about locally cloned repos.
 ```
   python app.py file -q "What can you tell me about this project"
 ```

It also allows the option to aks about public repos. It creates a temporary folder where it clones the repository. After it prints the response, it deletes the repo. 

```
  python app.py -u "github.com/user/repo" -q "What can you tell me about this repo?"
```

To use, you need to create .env file with the OpenAI API key inside.
