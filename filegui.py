#import statements
import tkinter as tk
from tkinter import filedialog

#funtion to test file opening with tkinter
def open_file():
    file_path = filedialog.askopenfilename(
        title="Select a File",
        filetypes=(("Text files", "*.txt*"), ("All files", "*.*"))
    )
    if file_path:
        with open(file_path, 'r') as file:
            content = file.read()
            print(content)  
            
root = tk.Tk()
root.title("File Input Example")

open_button = tk.Button(root, text="Open File", command=open_file)
open_button.pack(pady=20)

root.mainloop()
