import os

def load_instruction_file(filename:str, default:str=""):
  """
  Load Instructions from a file. If the file does not exist, return the default
  instructions.

  Args: 
    filename (str): the path to the instruction file.
    default (str): Default instructions to return if the file does not exist.

  Returns:
    str: The content of the instructions file or the default instructions.
  """
  if os.path.exists(filename):
    with open(filename, 'r', encoding="utf-8") as file:
      return file.read()
  return default