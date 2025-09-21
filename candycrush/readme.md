# Based on your computer system, follow the steps to run the game program

## Mac & Linux
0. Check your Python
Open the search bar, and search "Terminal". 
Open it and run 
```
python3 --version
```
If you don't see python 3.x, install the latest python3 from python.org (teh macOS installer). After installing, reopen Terminal and try again. 

1. Go into the project folder
Go into the project folder in terminal. 
```
cd /path/to/the/folder/
```

2. Create & activate a virtual environment
```
python3 -m venv .venv
# activate
source .venv/bin/activate
# your prompt should now start with (.venv)
```

3. Upgrade pip and install pygame
```
python -m pip install --upgrade pip wheel setuptools
python -m pip install pygame
```

4. Quick self-test
pygame ships with examples. This command should pop up a small demo window
```
python -m pygame.examples.aliens
```
close it to continue. If it works, you are good to go. 

5. Run the script
```
python candycrush.py
```

## Windows
0. Install/check python
    a. Press `Win` -> type cmd -> Enter
    b. Check python
    ```
    py --version
    ```
    If you don't see python 3.x, download the Windows installer from python.org and install it. During install, check "Add python.exe to PATH." Then reopen Command Prompt and run `py --version` again. 

1. Go into the project folder
```
cd path\to\folder
```

2. Create & activate a virtual environment (recommended)
```
py -m venv .venv
.\.venv\Scripts\activate
```
Your prompt should now begin with `(.venv)`

3. Upgrade pip and install pygame
```
py -m pip install --upgrade pip wheel setuptools
py -m pip install pygame
```

4. Quick self-test (run a demo)
```
py -m pygame.examples.aliens
```
A small game window should appear. Close it to continue. 

5. Run the game script
```
py candycrush.py
```
