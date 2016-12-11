To run tests, execute this from the project's root directory (where `app.yaml` resides):

```
python api/test/runner.py --test-path=api/test/ <path to your google SDK dir>
```

You'll have to have [Webtest](webtest.pythonpaste.org) as well as the 
[Google Cloud SDK](https://cloud.google.com/sdk/docs/) installed. 