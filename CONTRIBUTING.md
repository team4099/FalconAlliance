# Contributing

## Cloning the Repository
In the folder you want to clone the repository in, run `git clone https://github.com/team4099/FalconAlliance.git`.


## Installing Dependencies
**FalconAlliance** uses poetry to manage dependencies. Below are the steps to get all dependencies set up.
1. Run `python -m pip install -U poetry` in your terminal to install poetry.
2. Run `poetry install` to install all dependencies that FalconAlliance uses.
    - If you get an error regarding the dependencies not matching any versions, run `poetry update` instead.
3. Run `pre-commit install` to install the pre-commit hooks used for formatting your code and ensuring it complies to PEP8.


## Commiting Your Code
When commiting your code, you should see pre-commit hooks such as `flake8`, `black` and more. It should look something like this: ![image](https://user-images.githubusercontent.com/82843611/185821954-402ba66a-3573-44a5-a85c-483ff618de0d.png)
<br>
If no pre-commit hooks run, run `pre-commit install` then commit your changes.
### Pre-Commit Hooks Failing
If `flake8` fails, it will inform you about the lines of code that don't follow PEP8, and you should fix them accordingly.
If any pre-commit hook other than `flake8` fails simply commit again as they have formatted your code to follow PEP8 (Python's style guide).


## Style Guide
The code below shows generally what the style guide is, specifically with writing functions. If you have no parameters or returns, you can move their corresponding section in the function's docstring.
Remember to follow this when following your code.
```py
def function_name(parameter: parameter_type) -> return_type:
  """
  Explanation of what this function does.

  Parameters:
  	parameter:
    	Explanation of what parameter is

  Returns:
  	Explanation of what this function returns
  """
  ```

## Tests
When adding code, you should also add tests that cover said code.
An example of a test case is:
```py
def test_explanation_of_test():
  """Explanation of test case."""
  assert condition_that_ensures_that_code_works
```

You should add your test cases to the corresponding file for the test case. Test case files are organized by test cases for a specific class (eg `team_test` or `district_test`), if a file like this doesn't exist for the class you want to add test cases on, remember to create it!
<br>
Then, to run your test cases, simply run `coverage run -m pytest` in the terminal.
<br>
<br>
If all your test cases have passed, remember to run `coverage report -m` to ensure that the code coverage is 100%.
<br>
If your code coverage is not 100%, remember to add tests for the lines it says that are missed! However, if you know that a portion of code will never run but it works, you can append `# pragma: no cover` to the line where the block of code starts.
