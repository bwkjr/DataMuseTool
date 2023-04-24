from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Function to get related words based on a search query and a parameter
def get_words(query, param):
    base_url = "https://api.datamuse.com/words"
    params = {param:query}
    res = requests.get(base_url, params=params)
    words = [data['word'] for data in res.json()]
    return words

# Home page route
@app.route('/', methods=['GET', 'POST'])
def home():
    # Initialize variables for search term and related words
    search_word = ''
    words = []

    # If the search form is submitted
    if request.method == 'POST':
        search_word = request.form['search_word']
        button = request.form['button']

        # Get related words based on the button clicked
        if button == 'Rhymes':
            words = get_words(search_word, 'rel_rhy')
        elif button == 'Related Words':
            words = get_words(search_word, 'ml')
        elif button == 'Similar Sound':
            words = get_words(search_word, 'sl')
        elif button == 'Similar Spelling':
            words = get_words(search_word, 'sp')
        elif button == 'Synonyms':
            words = get_words(search_word, 'rel_syn')
        elif button == 'Antonyms':
            words = get_words(search_word, 'rel_ant')

    # Render the home page template with the search term and related words
    return render_template('home.html', search_word=search_word, words=words)

# Alt Features page route
@app.route("/altfeatures", methods=["GET", "POST"])
def altfeatures():
    # If the search form is submitted
    if request.method == "POST":
        base_url = "https://api.datamuse.com/words?"
        checkboxes = ["ml", "sl", "sp", "rel_syn", "rel_trg", "rel_ant", "rel_spc", "rel_gen", "rel_bga", "rel_bgb", "rel_rhy", "rel_nry"]
        params = []
        # Loop through the checkboxes and add the selected ones to the parameters
        for checkbox in checkboxes:
            if checkbox in request.form:
                value = request.form[checkbox]
                if value:
                    params.append(checkbox + "=" + value)
        # If at least one checkbox is selected, make a request to the Datamuse API with the selected parameters
        if params:
            query_url = base_url + "&".join(params)
            response = requests.get(query_url)
            results = response.json()
            return render_template("altfeatures.html", results=results)
        # If no checkboxes are selected, render the page with an error message
        else:
            return render_template("altfeatures.html", message="Please select at least one checkbox.")
    # If the search form is not submitted, render the page with an empty form
    else:
        return render_template("altfeatures.html")

# Phonetic Chain page route
@app.route('/phonetic_chain', methods=['GET', 'POST'])
def phonetic_chain():
    # Initialize variables for starting word and phonetic chain
    word = ''
    word_chain = []

    # If the search form is submitted
    if request.method == 'POST':
        word = request.form['word']
        # Generate a phonetic chain based on the starting word
        word_chain = generate_phonetic_chain(word)

    # Render the phonetic chain page template with the starting word and phonetic chain
    return render_template('phonetic_chain.html', word=word, word_chain=word_chain)

# Function to get the phonemes for a word using the Datamuse API
def get_phonemes(word):
    base_url = "https://api.datamuse.com/words"
    params = {"sp": word, "md": "p"}
    res = requests.get(base_url, params=params)
    data = res.json()
    if data and 'tags' in data[0]:
        phonemes = data[0]['tags'][0].split(" ")
        return phonemes
    return None

# Function to find a word that starts with a specific phoneme using the Datamuse API
def find_word_with_first_phoneme(phoneme):
    base_url = "https://api.datamuse.com/words"
    params = {"sp": phoneme + "*", "md": "p", "max": 100}
    res = requests.get(base_url, params=params)
    words = res.json()
    for word_data in words:
        if 'tags' in word_data:
            word = word_data['word']
            phonemes = word_data["tags"][0].split(" ")
            if phonemes[0] == phoneme:
                return word
    return None

# Function to generate a phonetic chain of related words based on a starting word using the Datamuse API
def generate_phonetic_chain(word, chain_length=5):
    word_chain = [word]
    index = 0
    # Loop through the phonemes of the words in the chain and find related words with the next phoneme
    while len(word_chain) < chain_length:
        phonemes = get_phonemes(word)
        if phonemes:
            if index < len(phonemes) - 1:
                next_phoneme = phonemes[index + 1]
                index += 1
            else:
                break

            found_word = False
            max_attempts = 10
            # Try to find a related word with the next phoneme several times before giving up
            while not found_word and max_attempts > 0:
                word = find_word_with_first_phoneme(next_phoneme)
                if word and word not in word_chain:
                    word_chain.append(word)
                    found_word = True
                max_attempts -= 1

            if not found_word:
                break
        else:
            break
    return word_chain

if __name__ == '__main__':
    app.run(debug=True)

