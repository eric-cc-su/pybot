import aiml
import argparse
import os.path
from os import listdir
import re

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

class Pybot:
    def __init__(self, path=".", brain="bot_brain.brn"):
        self._brain = brain
        self._path = path
        # self.files = [file for file in listdir(self._path) if os.path.isfile(os.path.join(self._path, file))]
        self.kernel = aiml.Kernel()
        self.properties = {}

        self.keyreg = r"(\[\")([\s\S]+)(\",)" #value = group 2
        self.valuereg = r"(,( )?\")([\s\S]+)(\"])" #value = group3
        self.setitemreg = r"\[((\"\w+\"(, ?)?)+)\]," #value = group 1

        # Search for and initialize bot properties (.properties and .pdefaults files)
        files = [file for file in listdir(self._path) if os.path.isfile(os.path.join(self._path, file))]
        for filename in files:
            if re.search(r"(\.properties)$", filename):
                props = self.parse_kv_file(filepath=os.path.join(self._path, filename), return_dict=True)
                for key, value in props.items():
                    self.properties[key] = value
                    self.kernel.setBotPredicate(key, value)
            if re.search(r"(\.pdefaults)$", filename):
                pdefaults = self.parse_kv_file(filepath=os.path.join(self._path, filename), return_dict=True)
                for key, value in pdefaults.items():
                    self.properties[key] = value
                    self.kernel.setBotPredicate(key, value)

        self.kernel.bootstrap(brainFile=self._brain)

    def parse_kv_file(self, filepath, return_dict=False):
        """
        Parse file with lines in format: [key, value]

        :param filepath: string - the absolute path to the file
        :param return_dict: bool - Whether to return a dictionary obj or only write to file
        :return: None or dictionary object
        """
        newdict = {}
        try:
            category = os.path.splitext(filepath)[0][filepath.rindex("/")+1:]
        except ValueError:
            category = os.path.splitext(filepath)[0]
        if not return_dict:
            tmpfile = open("tempset.ini", "w")
            tmpfile.write("[{}]\n".format(category))

        with open(filepath, 'r') as properties:
            for line in properties:
                property = line.strip(",").strip("[]").replace("\"","").split(",")
                if len(property) >= 2:
                    if return_dict:
                        newdict[re.search(self.keyreg, line).group(2)] = re.search(self.valuereg, line).group(3)
                    else:
                        tmpfile.write("'{}'='{}'\n".format(re.search(self.keyreg, line).group(2), re.search(self.valuereg, line).group(3)))
                    # self.kernel.setBotPredicate(key, value)
        if return_dict:
            return(newdict)
        else:
            tmpfile.close()

    def parse_set_file(self, filepath, return_list=False):
        """
        Parse set file with lines in format ["foo"] or ["foo", "bar"] = "foo bar"

        :param filepath: string - the absolute filepath
        :param return_list: bool - Whether to return a dictionary obj or only write to file
        :return: None or dictionary
        """
        newlist = []
        try:
            category = os.path.splitext(filepath)[0][filepath.rindex("/")+1:]
        except ValueError:
            category = os.path.splitext(filepath)[0]
        if not return_list:
            tmpfile = open("tempset.ini", "w")
            tmpfile.write("[{}]\n".format(category))

        with open(filepath, 'r') as properties:
            for line in properties:
                setitem = re.match(self.setitemreg, line)
                setitem = setitem.group(1).replace("\"","").replace(",","") if setitem else None
                if setitem and setitem != "fooz":
                    if return_list:
                        newlist.append(setitem)
                    else:
                        tmpfile.write(setitem+"\n")
                    # self.kernel.setBotPredicate(key, value)
        if return_list:
            return(newlist)
        else:
            tmpfile.close()

    def learn(self, filepath=None):
        """
        Teach the bot with the given file(s)

        :param filepath: path for a single file
        :param files: array of filepaths for multiple files
        :return: None
        """
        files = []
        # Assemble list of files to learn
        if os.path.isfile(filepath):
            files.append(filepath)
        elif os.path.isdir(filepath):
            files += [os.path.join(filepath, filename) for filename in listdir(filepath) if os.path.isfile(os.path.join(filepath, filename))]
        # Teach the files given at the initial path
        if not filepath and len(files) == 0:
            files = [os.path.join(self._path, file) for file in listdir(self._path) if os.path.isfile(os.path.join(self._path, file))]

        for file in files:
            # Load substitutions, exclude from learning
            if os.path.splitext(file)[1] == ".substitution":
                self.parse_kv_file(file)
                self.kernel.loadSubs("tempset.ini")
            # TODO: add support for map and set files
            # Only learn AIML
            elif os.path.splitext(file)[1] == ".aiml":
                self.kernel.learn(file)
        # Save the brain
        self.kernel.saveBrain(self._brain)
        # Re-prep Kernel for use
        self.kernel.bootstrap(brainFile=self._brain)

    def talk(self, message):
        """
        Send a message to the bot and get back the response

        :param message: string, a message for the bot
        :return: string, the response from the bot
        """
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