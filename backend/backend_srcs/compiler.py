"""
This module provides functions to compile Python code to other languages using Pyccel.

Functions:

* `read_files_to_json`: Reads all files in a directory and returns them as JSON.
* `Compiler`: A class that encapsulates the functionality of compiling Python code to other languages using Pyccel.
* `Backend_compiler`: A function that compiles Python code to another language using Pyccel and returns the results.
* `Pyccel_version`: A function that returns the version of Pyccel.
"""
import os
import glob
import json
import re
import subprocess

def execute_command_with_timeout(command, timeout):
  """Executes the given command with a timeout of 30 seconds.

  Args:
    command: The command to be executed.
    timeout: The timeout in seconds.

  Returns:
    A tuple of the exit code, standard output, and error output of the command.
  """
  import subprocess
  import time

  process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
  try:
    output, error = process.communicate(timeout=timeout)
    exit_code = process.returncode
  except subprocess.TimeoutExpired:
    exit_code = -1
    output = None
    error = f"The command timed out after {timeout} seconds."
  return exit_code, error, output

def read_files_to_json(directory, file_types):
  """
  Reads all files in a directory and returns them as JSON.

  Args:
    directory: The directory to read the files from.
    file_types: A list of file extensions to read.

  Returns:
    A JSON object containing the files and their names.
  """

  all_files = glob.glob(f"{directory}/**/*")
  all_files += glob.glob(f"{directory}/*")
  files = [i for i in all_files if i.endswith('.h') or i.endswith('.c') or i.endswith('.f90')]
  data = []
  for file in files:
    with open(file) as fp:
      filename_s =  re.sub("^.*?/__pyccel__/", "", file)
      data.append({"FileName": filename_s, "Content": fp.read()})
  return data



class Compiler():
    """
    A class that encapsulates the functionality of compiling Python code to other languages using Pyccel.

    Attributes:
      folder_name: The name of the temporary folder where the Python code is compiled.
      file_path: The path to the Python file that is being compiled.

    Methods:
      Load_Python: Loads a Python file from input.
      Compile_it: Compiles the Python file to another language using Pyccel.
      Cleanup: Cleans up the temporary folder.
    """
    def __init__(self):
        self.folder_name = f"Pyccel_{str(hash(self))}"

    def Load_Python(self, input :str):
        """
        Loads a Python file from input.

        Args:
          input: The Python code
        """
        self.folder_path = f"/tmp/{self.folder_name}"
        self.file_path = f"{self.folder_path}/code_python.py"

        os.mkdir(self.folder_path)
        with open(self.file_path,'w') as my_file:
            my_file.write(input)
    def Execute_it(self):
        """
          Executing the script python
          check if the json have a security breach
          Return JSON
                  - "Pyccel":
                        "error_output"
                        "execution_output"
                  - "Python":
                        "error_output"
                        "execution output"
                  - "Security":
                        "Security_report"
        """
        # Check if the python code contain any security breaches
        pyccel_exit, pyccel_error, pyccel_execution = "", "", ""
        pyccel_exit_, pyccel_error_, pyccel_execution_ = "", "", ""
        python_exit, python_error, python_execution = "", "", ""

        bandit_command = f"bandit -r {self.file_path}"
        python_command = f"python3 -I {self.file_path}"
        pyccel_command = f"{self.folder_path}/code_python"
        command_builder = f"pyccel {self.file_path} --language {self.language}"

        security_exit, security_error, security_execition = execute_command_with_timeout(bandit_command, 30)
        print(f"security_exit {security_exit}")
        if security_exit == 0:
          security_error = "Safe"
          pyccel_exit_, pyccel_error_, pyccel_execution_ =  execute_command_with_timeout(command_builder, 30)
          pyccel_exit, pyccel_error, pyccel_execution =  execute_command_with_timeout(pyccel_command, 30)
          python_exit, python_error, python_execution = execute_command_with_timeout(python_command, 30)
        else:
          security_error = "Fatal"

        data = {
          "Pyccel": {
              "error_output": pyccel_execution_,
              "execution_output": pyccel_execution,
          },
          "Python": {
              "error_output": python_error,
              "execution_output": python_execution,
          },
          "Security": {
              "Security_report": security_error,
          },
        }
        return data

    def Compile_it(self, language :str):
        """
        Translate the Python file to another language using Pyccel.

        Args:
        language: The language to compile the code to.

        Returns:
        A JSON object containing the Translated files.
        """

        self.language = language
        file_types = ["c", "h", "f90", "py"]
        command_builder = f"pyccel {self.file_path} --language {language}"
        print(command_builder, "=====================================")
        pyccel_exit_, pyccel_error_, pyccel_execution_ =  execute_command_with_timeout(command_builder, 30)

        self.sources_dir = f"{self.folder_path}/__pyccel__"
        files = read_files_to_json(self.sources_dir, file_types)

        data_default = []

        for file in files:
          if file["FileName"] in ( 'prog_code_python.c' , 'prog_code_python.f90'):
              data_default.append({"FileNameDefault": file["FileName"], "ContentDefault": file["Content"]})
          elif file["FileName"] in ( 'code_python.f90' , 'code_python.c'):
              data_default.append( {"FileNameDefault": file["FileName"], "ContentDefault": file["Content"]})
        data = {
          "files" : files,
          "Default" : data_default,
          "Error" : str(pyccel_execution_)
        }
        return data

    def Cleanup(self):
        """
            Cleanup the The /tmp/Pyccel folder used in compilation.
        """
        if os.path.exists(self.folder_path):
            os.system("rm -r {}".format(self.folder_path))

def Backend_compiler(input: str, language: str):
    """
    Compiles Python code to another language using Pyccel and returns the results.

    Args:
      input: The Python code
      language: The language to compile the code to.

    Returns:
      A JSON object containing the compiled code.
    """
    response = ""
    d = Compiler()
    d.Load_Python(input)  #print(all_files)

    response = d.Compile_it(language)
    d.Cleanup()
    return response

def Backend_Executer(input: str, language: str):
    """
    Compiles Python code to another language using Pyccel and returns the results.

    Args:
      input: The Python code
      language: The language to compile the code to.

    Returns:
      A JSON object containing the compiled code.
    """
    response = ""
    d = Compiler()
    d.Load_Python(input)
    response = d.Compile_it(language)
    data = d.Execute_it()
    print(data)
    d.Cleanup()
    return data

def Pyccel_version():
    """
    Returns the version of Pyccel.

    Returns:
      A dictionary containing the Pyccel version.
    """
    command_builder = f"pyccel --version > /tmp/release_pyccel.txt"
    os.system(command_builder)
    with open("/tmp/release_pyccel.txt",'r') as release:
      version = release.read()
    version = version.split(" ")
    if len(version) >= 2:
      return {version[0]: version[1]}
    return(None)




# if __name__ == '__main__':
#     with open("/home/testing/hacker.py",'r') as f:
#       string = f.read()
#       Backend_Executer(string, 'c')