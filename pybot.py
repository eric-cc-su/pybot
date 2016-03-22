import aiml
import argparse
import os.path
from os import listdir
import re

class Pybot:
    def __init__(self, path=".", brain="bot_brain.brn"):
        self._brain = brain
        self._path = path
        # self.files = [file for file in listdir(self._path) if os.path.isfile(os.path.join(self._path, file))]
        self.kernel = aiml.Kernel()
        self.properties = {}

        self.keyreg = r"(\[\")([\s\S]+)(\",)" #group 2
        self.valuereg = r"(,( )?\")([\s\S]+)(\"])" #group3

        # Search for and initialize bot properties (.properties and .pdefaults files)
        files = [file for file in listdir(self._path) if os.path.isfile(os.path.join(self._path, file))]
        for filename in files:
            if re.search(r"(\.properties)$", filename):
                props = self.parse_set_file(filepath=os.path.join(self._path, filename))
                for key, value in props.items():
                    self.properties[key] = value
                    self.kernel.setBotPredicate(key, value)
            if re.search(r"(\.pdefaults)$", filename):
                pdefaults = self.parse_set_file(filepath=os.path.join(self._path, filename))
                for key, value in pdefaults.items():
                    self.properties[key] = value
                    self.kernel.setBotPredicate(key, value)

    def parse_set_file(self, filepath):
        """
        Parse file with lines in format: [key, value]

        :param filepath: the absolute path to the file
        :return: dictionary object
        """
        newdict = {}
        with open(filepath, 'r') as properties:
            for line in properties:
                property = line.strip(",").strip("[]").replace("\"","").split(",")
                if len(property) >= 2:
                    newdict[re.search(self.keyreg, line).group(2)] = re.search(self.valuereg, line).group(3)
                    # self.kernel.setBotPredicate(key, value)
        return(newdict)

    def teach(self, filepath=None, files=[]):
        """
        Teach the bot with the given file(s)

        :param filepath: path for a single file
        :param files: array of filepaths for multiple files
        :return: None
        """
        # Given a single file to teach
        if filepath:
            self.kernel.learn(filepath)
        # Given a set of filepaths to teach
        if len(files) > 0:
            for file in files:
                self.kernel.learn(file)
        # Teach the files given at the initial path
        else:
            files = [file for file in listdir(self._path) if os.path.isfile(os.path.join(self._path, file))]
            for file in files:
                self.kernel.learn(os.path.join(self._path, file))
        # Save the brain
        self.kernel.saveBrain(self._brain)

    def talk(self, message):
        """
        Send a message to the bot and get back the response

        :param message: string, a message for the bot
        :return: string, the response from the bot
        """
        self.kernel.bootstrap(brainFile=self.brain)
        return(self.kernel.respond(message))

def main():
    # Pybot CLI
    parser = argparse.ArgumentParser(description="Create and execute a Pybot")
    parser.add_argument("-p", "--path", help="The Pybot's directory path. Default is current directory.", default=".")
    parser.add_argument("-b", "--brain", help="The path for the Pybot brain file. Default is 'bot_brain.brn'.", default="bot_brain.brn")
    parser.add_argument("-t", "--teach", action="store_true", help="Teach the Pybot on initialization")
    parser.add_argument("--chat", action="store_true", help="Initialize chat with the Pybot")

    cl_args = parser.parse_args()
    bot = Pybot(path=cl_args.path, brain=cl_args.brain)
    if cl_args.teach:
        bot.teach()

    if cl_args.chat:
        kernel = aiml.Kernel()

        brain = cl_args.brain

        if brain and os.path.isfile(brain):
            kernel.bootstrap(brainFile=brain)
        else:
            print("No brain found. Initializing empty Pybot")
            kernel.bootstrap(learnFiles="default.aiml")
            kernel.saveBrain("bot_brain.brn")

        #kernel ready
        while True:
            print(kernel.respond(raw_input(">> ")))

if __name__ == "__main__":
    main()