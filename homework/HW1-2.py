import tkinter as tk
import random

streak = 0

# Function to handle the button click event and check the answer
def check_answer(num_1,num_2):
    global streak
    user_input = int(entry.get())
    correct_answer = num_1 * num_2
    if user_input == correct_answer:
        result.config(text="Correct!", fg="green")  
        streak += 1 
        counter.config(text=f"Streak: {streak}")
        problem_creator()
        entry.delete(0, "end")
    else:
        streak = 0
        counter.config(text=f"Streak: {streak}")
        result.config(text=f"Wrong! Try again.", fg="red")
        entry.delete(0, "end")

# Function to generate a new problem and update the label
def problem_creator():
    global num_1, num_2
    num_1 = random.randint(2, 12)
    num_2 = random.randint(2, 12)
    label.config(text=f"{num_1} x {num_2}")

def main():
    global label, entry, result, num_1, num_2,counter

    root = tk.Tk()
    root.title("Roan's Math Game")
    root.geometry("600x400")

    label = tk.Label(root, text="", font=("Arial", 45))
    label.pack(padx=20, pady=20)

    entry = tk.Entry(root, font=("Arial", 24), width=10)
    entry.pack(padx=20, pady=10)
    
    button = tk.Button(root, text="Submit", font=("Arial", 12), bg="grey", relief="raised", command=lambda: check_answer(num_1,num_2))
    button.pack(padx=20, pady=20)

    result = tk.Label(root, text="", font=("Arial", 18))
    result.pack(padx=20, pady=10)
    counter = tk.Label(root, text="Streak: 0", font=("Arial", 18))
    counter.pack(padx=20, pady=10)
    problem_creator()

    root.mainloop()

if __name__ == "__main__":
    main()
