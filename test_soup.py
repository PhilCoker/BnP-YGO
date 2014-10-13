import game_util
from game import Game

g = Game('test')
doc = game_util.get_board_html2( g, 'P1' )
with open('test_soup.html', 'w' ) as file:
	file.write(doc)