def import_words(file):
    try:
        with open(file, "r") as file:
            words = file.read().splitlines()
        print(f"Words found: {words}")
        return words
        
    except FileNotFoundError:
        print("No file found")
        return []

def save_word(words, file):
    with open(file, "w") as file:
        for word in words:
            file.write(word + "\n")

file = "cl_topics_a\\homework\\words.txt"
word_list = import_words(file)

while True:
    word = input("Enter a Word: ")
    if word == "exit":
        break
    word_list.append(word)

save_word(word_list, file)
print(word_list)