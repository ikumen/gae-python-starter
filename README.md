# gae-python-starter

## Requirements
- Python 2
- [Pyenv](https://github.com/pyenv/pyenv) for managing Python versions
- [Virtualenv](https://virtualenv.pypa.io/en/stable/) for managing project specific Python dependencies
- Google App Engine Account and
  - [Google Cloud Tools](https://cloud.google.com/sdk/docs/) for deploying and managing SDK components
  - List/install/remove/update SDK components
    ```
    $ gcloud components list
    $ gcloud components install <component-id>
    $ gcloud components remove <component-id>
    $ gcloud components update
    ```
  - Install Google Python SDK (this globally for your machine)
    ```
    # gcloud (as of Dec 2017) requires Python 2.7, so make sure you're running it with 2.7 is on your PATH
    $ gcloud components install app-engine-python
    ```

### Environment Setup
- Using [Pyenv](https://github.com/pyenv/pyenv)
  ```
  $ pyenv install 2.7.12
  $ cd <project directory>
  $ pyenv local 2.7.12  # sets the Python version we want to use (creates .python-version)
  ```
- Using [Virtualenv](https://virtualenv.pypa.io/en/stable/)
  ```
  $ cd <project directory>
  $ virtualenv .venv
  $ . .venv/bin/active  # to activate virtualenv, now all dependencies installed via `pip` will be isolated to local directory
  (.venv) $ pip install <some package> 
  (.venv) $ pip freeze > requirements.txt  # save dependencies used to rebuild our project
  ```
- To use third party libraries, we need to [add a vendor "lib" and tell GAE about it.](https://cloud.google.com/appengine/docs/standard/python/getting-started/python-standard-env). Ideally we don't want to check these dependencies in so we can simply symlink the `virtualenv`'s pip dependencies (which we've configure git to ignore) to our `lib` directory.
  ```
  $ cd <project directory>
  $ ln -s .venv/lib/python2.7/site-packages lib
  ``` 




