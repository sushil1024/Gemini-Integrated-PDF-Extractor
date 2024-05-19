import os
import sys
from pdf2image import convert_from_path
import textwrap
import PIL.Image
import google.generativeai as genai
from IPython.display import Markdown
from colorama import Fore


class GeminiExtractor:

  def __init__(self):
    file_path = str(input("File name?(with extension) : "))

    # convert pdf to jpg
    img = self.conv_to_jpg(file_path)
    if type(img) == str:
      print("Please check the file again!")
      input()
      sys.exit()

    # prompt
    prompt_img = self.generate_prompt(img)

    # look for API key in txt file
    key_file = "GEMINI_API_KEY.txt"
    GEMINI_API_KEY = self.check_api(key_file)

    genai.configure(api_key=GEMINI_API_KEY)

    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content(prompt_img, stream=True)
    response.resolve()

    try:
      self.to_markdown(response.text)
    except Exception as e:
      if len(response.parts) < 1:
        exit("404: not found!")


    temp_text = ""

    # json chunks into readable texts
    for chunk in response:
      temp_text += chunk.text

    lines = temp_text.split('\n')

    # value of every key
    values = []
    for elements in lines:
      values.append(elements.split(':')[1].strip())

    green_color_code = Fore.GREEN
    [print(f"{green_color_code}{i}") for i in values]

  # convert pdf to jpg
  def conv_to_jpg(self, file_path):
    if file_path.lower().endswith(".pdf") and os.path.exists(file_path):
      images = convert_from_path(file_path)

      jpg_path = file_path + ".jpg"
      images[0].save(jpg_path, 'JPEG')
      print("Image generated")
      return PIL.Image.open(jpg_path)

    else:
      return "Image not generated"

  # generate prompt
  def generate_prompt(self, img):
    prompt_img = []

    while(True):
      fetch = str(input("Fetch? : "))
      assoc = str(input("Associated with? : "))

      prompt_img.append(f"fetch '{fetch}' which is associated around '{assoc}' in this picture. Directly provide response in Key : Value pair string. Example= {fetch} : actual_value")

      ch = str(input("More values? (y/n): "))

      if ch.lower() != "y":
        # last element should be the image
        prompt_img.append(img)
        return prompt_img

  # check for API key in txt
  def check_api(self, key_file):
    # found
    if os.path.exists(key_file):
      f = open(key_file,'r')
      try:
        GEMINI_API_KEY = f.readline().strip('\n')
        return GEMINI_API_KEY
      except Exception as e:
        print("Error reading api key from text file.")
        print(e)
        input()
        sys.exit()
    # not found
    else:
      GEMINI_API_KEY = str(input("Enter Gemini API key: "))
      with open(key_file, "w") as f:
        f.write(GEMINI_API_KEY)

      return GEMINI_API_KEY

  # refactor the response
  def to_markdown(self, text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


if __name__ == "__main__":
  obj = GeminiExtractor()
  input()