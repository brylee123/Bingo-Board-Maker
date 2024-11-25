# Bingo-Board-Maker

Input Directory: 
bingo_spaces : Add as many square png files in this directory as possible. This will be your bingo pieces. You can add more than what can fit on the board. There must be a center.png file.

Interim Directories:
bingo_board : This directory will hold the assembled boards without the template.
bingo_board_with_template : This directory will merge the bingo boards with the generated/edited templates.
template_backups : If you overwrite an existing template, the script will back up your last template and timestamp it.

Generated Files:
bingo_border_template.png : This file shows you where the bingo board will be placed. You should design around that square.
bingoList.js : This file passes a variable that contains a list of all the bingo pieces for draw_bingo.html
bingo_cards.pdf : This file is a PDF of all the images in bingo_board_with_template. This makes for easier tiling when printing.

Executable Files:
bingo.py : The master file that will generate boards. Also calls draw_bingo_init.py. It will prompt you for how many unique bingo sheets you'd like and round up to the closest multiple of 4 for print tiling.
draw_bingo_init.py : This file creates bingoList.js.
draw_bingo.html : This is the front end for the bingo game. It will always start with the free center piece. Then it keeps a history of old draws (in the current instance).
