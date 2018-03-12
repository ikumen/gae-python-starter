Starter for Flask + Google App Engine based applications.

## Requirements
- Python 2
- [Pyenv](https://github.com/pyenv/pyenv) for managing Python versions
- [Pip](https://pip.pypa.io/en/stable/) and [Virtualenv](https://virtualenv.pypa.io/en/stable/) for managing and isolating project dependencies (Python).
- [Google App Engine Account](https://appengine.google.com/)
- [Google Cloud Tools](https://cloud.google.com/sdk/docs/) for deploying and managing GAE applications and SDK components

### Environment Setup
- Using [Pyenv](https://github.com/pyenv/pyenv)
  ``` bash
  $ pyenv install 2.7.12
  $ cd <project directory>
  $ pyenv local 2.7.12  # sets the Python version we want to use (creates .python-version)
  ```
- Using [Virtualenv](https://virtualenv.pypa.io/en/stable/)
  ``` bash
  # Let's create a local virtual environment
  $ cd <project directory>
  $ virtualenv .venv
  
  # To activate virtualenv, now all dependencies installed via `pip` will be isolated to local directory
  $ . .venv/bin/active  
  
  # Example install and saving dependencies to requirements.txt
  (.venv) $ pip install <some package> 
  (.venv) $ pip freeze > requirements.txt
  
  # Finally let's install the project dependencies
  (.venv) $ pip install -r requirements.txt
  ```
- To use third party libraries, we need to [add a vendor "lib" and tell GAE about it.](https://cloud.google.com/appengine/docs/standard/python/getting-started/python-standard-env). Ideally we don't want to check these dependencies into source control. One solution is to install the dependences to the default `virtualenv` location, then symlink that location to our "lib" directory for Google.
  ``` bash
  $ cd <project directory>
  $ ln -s .venv/lib/python2.7/site-packages lib
  ``` 
- Install the Google App Engine SDK using our `gcloud` tool from above.
  ``` bash
  # Installing app engine SDK (note: as of Dec 2017, gcloud requires Python 2.7)
  $ gcloud components install app-engine-python
    
  # Here are some common commands
  $ gcloud components list
  $ gcloud components install <component-id>
  $ gcloud components remove <component-id>
  $ gcloud components update
  ```




