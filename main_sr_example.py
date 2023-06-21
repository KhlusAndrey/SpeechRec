import random
import time

import speech_recognition as sr


def recognize_speech_from_mic(recognizer: sr.Recognizer, microphone: sr.Microphone) -> dict:
    """Transcribe speech from recorded from `microphone`.

    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was successful
    "error":   `None` if no error occured, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
               otherwise a string containing the transcribed text
    """
    
    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response


if __name__ == "__main__":
    # set the list of words, maxnumber of guesses, and prompt limit
    words = ["apple", "banana", "grape", "orange", "mango", "lemon"]
    random.shuffle(words)
    NUM_GUESSES = 3
    PROMPT_LIMIT = 5
   
    # create recognizer and mic instances
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    # get a random word from the list
    word = random.choice(words)
    print(word)
    # format the instructions string
    instructions = f"I'm thinking of one of these words:\n \
    {words}\n\
    You have {NUM_GUESSES} tries to guess which one.\n"

    # show instructions and wait 3 seconds before starting the game
    print(instructions)
    time.sleep(3)

    for i in range(NUM_GUESSES):
        # get the guess from the user
        # if a transcription is returned, break out of the loop and
        #     continue
        # if no transcription returned and API request failed, break
        #     loop and continue
        # if API request succeeded but no transcription was returned,
        #     re-prompt the user to say their guess again. Do this up
        #     to PROMPT_LIMIT times
        for j in range(PROMPT_LIMIT):
            print(f'Guess {i+1}. Speak!')
            guess = recognize_speech_from_mic(recognizer, microphone)
            if guess["transcription"] or not guess["success"]:
                break
            print("I didn't catch that. What did you say?\n")

        # if there was an error, stop the game
        if guess["error"]:
            print("ERROR: {}".format(guess["error"]))
            break

        # show the user the transcription
        print(f"You said: {guess['transcription']}")

        # determine if guess is correct and if any attempts remain
        guess_is_correct = word.lower() in guess["transcription"].lower()
        
        # determine if the user has won the game
        # if not, repeat the loop if user has more attempts
        # if no attempts left, the user loses the game
        if guess_is_correct:
            print("Correct! You win! " + word)
            break
        elif i < NUM_GUESSES - 1:
            print("Incorrect. Try again.\n")
        else:
            print(f"Sorry, you lose!\nI was thinking of '{word}'.")
            break
