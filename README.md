# b07 bot

## Getting Started

1. Install Python (Tested on 2.7.4 on Ubuntu 13.04), Twisted (Ver 12.1 or newer) and MySQL-python (available on pip)
2. Clone the source:

   git clone https://github.com/redleader36/b07bot.git 
   cd b07bot   

3. Run the script:

   PYTHONPATH=src python src/b07/main.py  
   
   The first time the script is run, you will be prompted for username and password and email server configuration. 
   If you don't have your own email server and information, just answer "n" to the prompt and it will send from your 
   gmail account to your gmail account.



=======
b07bot
======

This is a script that allows ingress users to get their inventory in a better way, 
see their inventory in a beautiful grid, (both in the console and in a possible e-mail)
as well as create and e-mail a [KML](https://developers.google.com/kml/documentation/) file 
that contains all of the keys in the user's inventory (and attached pictures where possible)
