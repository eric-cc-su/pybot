#!/usr/bin/python
import aiml
import os
import re

kernel = aiml.Kernel()

brain = None
files = [file for file in os.listdir(".") if os.path.isfile(os.path.join(".", file))]
for filename in files:
    if re.search("(.brn)$", filename):
        brain = filename

if brain and os.path.isfile(brain):
    kernel.bootstrap(brainFile=brain)
else:
    print("No brain found. Initialize a chatbot brain with Pybot")
    kernel.bootstrap(learnFiles="default.aiml")
    kernel.saveBrain("bot_brain.brn")

#kernel ready
while True:
    print(kernel.respond(raw_input(">> ")))