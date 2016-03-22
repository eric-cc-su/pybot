# pybot
A simply Python interface with AIML-based chatbots.

A brain file for [A.L.I.C.E.](http://www.alicebot.org/aiml.html) has been included.

*Note*: This is not an AIML interpreter/parser

## Requirements

- Python2
- aiml (`pip install aiml`)
    - Since Pybot currently relies on the aiml package, there is no built-in support for AIML2
- AIML files for Pybot to assemble

*This has not yet been tested in Python 3*

## Getting Started

1a. Use Pybot as a module:   

        from pybot import Pybot
           
        # Initialize Pybot at current path with brain file "bot_brain.brn"
        mybot = Pybot() 
        
        # Teach Pybot with the files at the current path
        mybot.teach()   
        
        # Talk to your Pybot
        response = mybot.talk("hello") 
        
1b. User Pybot's command line interface:

        # Initialize Pybot at current path with brain file "bot_brain.brn"
        > python pybot.py
        # Teach Pybot with the files at the current path
        > python pybot.py --teach
        
        # Open chat thread with your bot (Exit with Ctrl+C)
        > python pybot.py --chat
        
        >> "hello"
        "Hello, I'm your bot"
        ...
        
Simple as that for now...