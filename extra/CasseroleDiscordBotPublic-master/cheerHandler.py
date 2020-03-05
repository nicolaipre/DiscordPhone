import re, random


class CheerHandler():

    def __init__(self):
        self.message = None
        self.responsePhrase = ""

    def callResponse(self, call, response):
        if self.message.strip().lower() == call.lower():
            return response
        else:
            return ""

    def update(self, messageText):

        response = ""

        if messageText.startswith('hello') or messageText.startswith('hi'):
            response += random.choice(["Hello!", "Hello.", "Howdy!", "Good day to you!", "How's it going?", "Hi!", "Yo!", "Greetings!"])
        
        # Handle Simple call/response cheers
        self.message = messageText
        response += self.callResponse("17", "36!")
        response += self.callResponse("Robot", "Casserole!")
        response += self.callResponse("Casserole Casserole", "Eat it Up! Eat it Up!")
        response += self.callResponse("What time is it?", "Nine Thirty!")
        response += self.callResponse("Four on Three", "One! Two! Three! Four!")
        response += self.callResponse("Who's Hungry?", "I'm Hungry!")
        response += self.callResponse("For What?", "Casserole!!!")
        response += self.callResponse("yay", "YAAAAAYYYYY!!!!")
        response += self.callResponse("Who's Hungary?", "The Hungarians! https://en.wikipedia.org/wiki/Hungary")

        ## Handle "Give me a..." cheers
        results = re.search("give me a[n]? (.*)", messageText)
        if(results):
            subphrase = results.group(1).strip()
            self.responsePhrase += subphrase
            response += (subphrase + "!")

        if(messageText.startswith("what does that spell?")):
            if(len(self.responsePhrase) > 0):
                response += (self.responsePhrase + "!")
                self.responsePhrase = ""

        return response
        


        
