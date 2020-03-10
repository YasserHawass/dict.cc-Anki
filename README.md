# dict.cc-Anki


dirty fork from https://github.com/rbaron/dict.cc.py
made it while i was learning German language.

# current possiblities
- same as dict.cc.py
- able to extract audio for native speakers, my tutor prefered Hameflix, so priority goes to him, if not found it picks another native speaker.
- outputting text file to import into anki

# optimisation
- replace chromedrive for a better fetching method.
- output Anki files instead of txt.
- allowing massive input (txt file ordered by word and the arguments)
  - refactoring
  - cleaning trash code
  - changing output directories
  - adding GUI (hopefully fork it from dict.cc.py and PR it)
    - maybe add search button, clean button, import a txt filled with words, handling the missing arguments as "de en".

# problems
- audio fetching could require multi tries to fetch it, because of dict.cc anti scrapping efforts.
- some Errors, could stop the script, and leave the chromedriver running on background.

# comments
the code would work way better if ran on linux environment and altered slightly (the audio fetching part).
