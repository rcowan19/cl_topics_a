import tkinter as tk
from tkinter import ttk

def button_click():
    global label
    label.config(text="Starting")

def main():
    global label
    #set up a window
    root  = tk.Tk()
    root.title("Window")
    root.geometry("600x400")

    label = tk.Label(root, text ="Cick to Start")
    label.pack(padx=100, pady=100)

    button = tk.Button(root, text="Click me", command= button_click, font=("Arial", 12), bg="grey", relief="raised")
    button.pack()
    

    #Start event loop
    root.mainloop()

if __name__ == "__main__":
    main()

