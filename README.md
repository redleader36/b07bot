# b07 bot

## Getting Started

1. Install Python and Twisted
2. Clone the source:

   git clone https://github.com/dirtydave0221/b07bot.git  
   cd b07bot  

3. Copy the sample config file and edit it:

   cp b07.sample ~/.b07  
   edit ~/.b07  

4. Run the script:

   PYTHONPATH=src python src/b07/main.py



=======
b07bot
======

This is a script that allows ingress users to get their inventory in a better way, 
see their inventory in a beautiful grid, (both in the console and in a possible e-mail)
as well as create and e-mail a [KML](https://developers.google.com/kml/documentation/) file 
that contains all of the keys in the user's inventory (and attached pictures where possible)
