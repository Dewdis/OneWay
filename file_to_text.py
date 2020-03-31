def file_to_text(path):
    file = open(path, 'r')
    text = file.read()
    # Ignore new string symbol.
    return text[0:len(text)-1]
