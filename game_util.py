import os
from bs4 import BeautifulSoup
import deck_util, html_util
import game

'''
	A bunch of utility functions to help games.
'''

game_folder = 'game\\'
game_ext = '.g.txt'

#Returns a list of all the games saved
def get_games_list():
	game_list = []
	for game in os.listdir(game_folder):
		if game.endswith(game_ext):
			game_list.append( game.split(game_ext)[0] )
	return game_list

#Returns the URL path of the specified card number and deck_name
def get_card_path( cardnum, deck_name ):
	if cardnum > 0:
		count = 1
		with open( deck_util.deck_folder + deck_name + deck_util.deck_ext, 'r' ) as deck_file:
			while count < cardnum:
				deck_file.readline()
				count = count + 1
			found = deck_file.readline().replace('\n', '')
			return get_image_path( found )

#Returns the URL of the card given at Yugioh Prices
def get_image_path( card_name ):
	base = 'http://static.api3.studiobebop.net/ygo_data/card_images/'
	
	replaced = card_name.replace( ' ', '_' ).replace('-','_')
	url = base + replaced + '.jpg'
	return url

def write_html( game, player ):
	with open( 'templates\\{}_{}.html'.format(game.game_name, player), 'w' ) as file:
		file.write( get_board_html( game, player ) )

#Loads a game based on a certain format
def load_game( gname='test' ):
	dict = {}
	with open( game_folder + gname + game_ext, 'r' ) as file:
		for line in file:
			#Ignore comments
			if line[0] != '#':
				s = line.split('=')
				dict[ s[0] ] = s[1].replace('\n', '')
	return dict

#Writes the game state into a file in a certain format
def save_game( game_dict, game_name='unnamed' ):
	with open( game_folder + game_name + game_ext, 'w' ) as file:
		for k in game_dict.iterkeys():
			file.write( k + '=' + game_dict[k] + '\n' )

#Returns the html that allows someone to view/start/create/etc. games
def gen_games_html( game_names ):
	games_html = """<html>
<head>
<title>Games</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
<body>

<div id="g" style="margin-right:20px">
Here are the game files currently saved:
<br>
"""
	games = get_games_list()
	for game_name in games:
		games_html += '<a href="game?name=' + game_name + '">' + game_name + '</a><br>'
	games_html += """
</div>
<div id ="g">
These are the games currently running:
<br>
"""
	for game in game_names:
		games_html += game + '\n<br>\n'
	games_html += """
</div>
<br>
<div id="g" style="margin-right:20px;margin-top:10px;clear:left">
<a href="/start_game">Start running a game</a>
<br>
<a href="/play">Play a running game</a>
<br>
<a href="/stop_game">Stop a running game</a>
</div>
<div id="g" style="margin-top:10px">
<a href="/new_game">Create a new game</a>
<br>
<a href="/edit_game">Edit an existing game</a>
<br>
<a href="/delete_game">Delete an existing game</a>
</div>
<div style="clear:both">
<br>
<br>
<a href="/">Go back</a>
</div>
</body>
</html>"""
	return games_html

#Returns the html that allows someone to see a game's contents
def gen_game_html( game_name ):
	game_html = """<!DOCTYPE HTML>
<html>
<head>
<title>View game</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
<body>
<table style="border: 1px solid black">
	<tr>
		<th>{}</th>
		<th>{}</th>
	</tr>
""".format( 'Tag', 'Value' )
	with open( game_folder + game_name + game_ext, 'r' ) as file:
		for line in file:
			if line[0] != '#':
				if line.endswith('\n'):
					line = line[:-1]
				tag = line.split('=')[0]
				val = line.split('=')[1]
				game_html += """	<tr>
		<td>{}</td>
		<td>{}</td>
	</tr>
""".format( tag, val )
	game_html += """</table>
<br>
<a href="/games">Go back</a>
</body>
</html>"""
	return game_html

#Returns html that shows a given number of tokens
def get_token_html( num ):
	token_image = '<img src="http://www.nigeltomm.com/images/orange_square_nigel_tomm_m.jpg" style="float:left;position:relative;width:10px;height:10px;top:-212px;left:'
	return_html = ''
	for i in range(1, num+1):
		return_html += token_image + str(10*i) + 'px">'
	return return_html

#Returns the html that represents a player's side of the board in a game
def get_board_html( game, player):
	back = 'http://images.wikia.com/yugioh/images/archive/e/e5/20080209143844!Back-EN.png'
	error = 'http://www.katiescarbrough.co.uk/wp-content/uploads/a-big-x-2-473x350.jpg'
	format_dict = {}
	deck_name = game.get_deck_name(player)
	format_dict['deck_name'] = deck_name
	format_dict['player_name'] = player
	format_dict['game_name'] = game.game_name
	format_dict['life_points'] = game.get_LP(player)
	
	#The player's side of the field
	#Field
	field = game.get_field(player)
	format_dict['field_paths'] = 'src="" src2=""'
	format_dict['field_styles'] = ''
	format_dict['field_tokens'] = ''
	if field != []:
		field_split = field[0].split(':')
		card_num = int(field_split[0])
		pos = int( field_split[1] )
		field_paths = ''
		if pos == 0:
			field_paths = 'src="' + get_card_path( card_num, deck_name ) + '" src2="' + get_card_path( card_num, deck_name ) + '"'
		elif pos == 2:
			field_paths = 'src="' + back + '" src2="' + get_card_path( card_num, deck_name ) + '"' 
		else:
			field_paths = 'src="' + error + '" src2="' + error + '"'
		
		format_dict['field_paths'] = field_paths
		format_dict['field_styles'] = 'id="field_card" onClick=\'swipe("field_card");\''
		
		#Add tokens, if any
		if len( field_split ) > 2:
			token_num = int( field_split[2] )
			format_dict['field_tokens'] = get_token_html( token_num )
	#Monsters
	monsters = game.get_monsters(player)
	for i in range(len(monsters)):
		curr_monster = 'M' + str(i+1)
		format_dict[curr_monster + '_paths'] = 'src="" src2=""'
		format_dict[curr_monster + '_styles'] = ''
		format_dict[curr_monster + '_tokens'] = ''
		m = monsters[i]
		if m != '':
			m_split = m.split(':')
			card_num = int(m_split[0])
			pos = int( m_split[1] )
			
			monster_paths = ''
			#Add image path
			if (pos == 0) or (pos == 1):
				monster_paths = 'src="' + get_card_path( card_num, deck_name ) + '" src2="' + get_card_path( card_num, deck_name ) + '"'
			elif (pos == 2) or (pos == 3):
				monster_paths = 'src="' + back + '" src2="' + get_card_path( card_num, deck_name ) + '"'
			else:
				monster_paths = 'src="' + error + '" src2="' + error + '"'
			
			format_dict[curr_monster + '_paths'] = monster_paths
			
			#Add style
			new_style = ''
			if (pos==1) or (pos == 3):
				new_style = 'style="-webkit-transform: rotate(-90deg);-moz-transform: rotate(-90deg);" '
			new_style += 'id="M{0}_card" onClick=\'swipe("M{0}_card");\''.format(i+1)
			format_dict[curr_monster + '_styles'] = new_style
			
			#Add tokens, if any
			if len( m_split ) > 2:
				token_num = int( m_split[2] )
				format_dict[ curr_monster + '_tokens'] = get_token_html( token_num )
	#Graveyard
	grave = game.get_graveyard(player)
	graveyard_paths = 'src="" src2=""'
	graveyard_styles = ''
	if grave != []:
		img_path = get_card_path( int(grave[-1]), deck_name )
		graveyard_paths = 'src="' + img_path + '" src2="' + img_path + '"'
		graveyard_styles = 'onClick="look_at(\'graveyard\');"'
	format_dict['graveyard_paths'] = graveyard_paths
	format_dict['graveyard_styles'] = graveyard_styles
	#Banished zone
	banished = game.get_banished(player)
	banished_paths = 'src=""'
	banished_styles = ''
	if banished != []:
		img_path = get_card_path( int(banished[-1]), deck_name )
		banished_paths = 'src="' + img_path + '"'
		banished_styles = 'onClick="look_at(\'banished\');"'
	format_dict['banished_paths'] = banished_paths
	format_dict['banished_styles'] = banished_styles
	#Extra deck
	extra = game.get_extra(player)
	extra_paths = 'src=""'
	extra_styles = ''
	if extra != []:
		img_path = get_card_path( int(extra[-1]), deck_name )
		extra_paths = 'src="' + img_path + '"'
		extra_styles = 'onClick="look_at(\'extra\');"'
	format_dict['extra_deck_paths'] = extra_paths
	format_dict['extra_deck_styles'] = extra_styles
	#Spells/traps
	spells = game.get_spells(player)
	for i in range(len(spells)):
		curr_spell = 'ST' + str(i+1)
		format_dict[curr_spell + '_paths'] = 'src="" src2=""'
		format_dict[curr_spell + '_styles'] = ''
		format_dict[curr_spell + '_tokens'] = ''
		s = spells[i]
		if s != '':
			s_split = s.split(':')
			card_num = int(s_split[0])
			pos = int( s_split[1] )
			
			spell_paths = ''
			#Add image path
			if (pos == 0) or (pos == 1):
				spell_paths = 'src="' + get_card_path( card_num, deck_name ) + '" src2="' + get_card_path( card_num, deck_name ) + '"'
			elif (pos == 2) or (pos == 3):
				spell_paths = 'src="' + back + '" src2="' + get_card_path( card_num, deck_name ) + '"'
			else:
				spell_paths = 'src="' + error + '" src2="' + error + '"'
			
			format_dict[curr_spell + '_paths'] = spell_paths
			
			#Add style
			new_style = ''
			if (pos==1) or (pos == 3):
				new_style = 'style="-webkit-transform: rotate(-90deg);-moz-transform: rotate(-90deg);" '
			new_style += 'id="ST{0}_card" onClick=\'swipe("ST{0}_card");\''.format(i+1)
			format_dict[curr_spell + '_styles'] = new_style
			
			#Add tokens, if any
			if len( s_split ) > 2:
				token_num = int( s_split[2] )
				format_dict[ curr_spell + '_tokens'] = get_token_html( token_num )
	#Deck
	deck = game.get_deck(player)
	deck_paths = 'src=""'
	deck_styles = ''
	if deck != []:
		deck_paths = 'src="' + back + '"'
		deck_styles = 'onClick="look_at(\'deck\');"'
	format_dict['deck_paths'] = deck_paths
	format_dict['deck_styles'] = deck_styles
	#Hand
	hand = game.get_hand(player)
	hand_html = ''
	offset = 0
	for i in range( len(hand) ):
		card_num = hand[i]
		hand_html = hand_html + '<img src="{0}" src2="{0}" style="float:left;position:relative;left:{1}px" id="H{2}_card" onClick=\'swipe("H{2}_card");\' >\n\t\t'.format( get_card_path( int(card_num), deck_name ), offset, i+1 )
		offset = offset - 50
	format_dict['hand'] = hand_html
	
	format_dict['link'] = '<a href="/">Back to main</a>'
	
	page = """<!DOCTYPE HTML>
<html>
<head>
<title>Yu-Gi-Oh!</title>
<link rel="stylesheet" type="text/css" href={{ url_for('static', filename="gameboard.css") }} />
<link rel="icon" type="image/png" href={{ url_for('static', filename="favicon.png") }} />
</style>
</head>
<body>
<script>
function swipe(img_id)
{
	var largeImage = document.getElementById(img_id);
	var url=largeImage.getAttribute('src2');
	window.open(url,'Image','width=largeImage.stylewidth,height=largeImage.style.height,resizable=1');
}
function look_at(area)
{
	window.open( '/play?name=%(game_name)s&player=%(player_name)s&view='+area, 'Image', 'width=largeImage.stylewidth,height=largeImage.style.height,resizable=1' );
}
</script>
%(link)s
<br>
Life Points: %(life_points)s
	<div id="board">
		<div id="field_zone"><img %(field_paths)s %(field_styles)s >%(field_tokens)s
		</div>
		<div id="M1_zone"><img %(M1_paths)s %(M1_styles)s >%(M1_tokens)s
		</div>
		<div id="M2_zone"><img %(M2_paths)s %(M2_styles)s >%(M2_tokens)s
		</div>
		<div id="M3_zone"><img %(M3_paths)s %(M3_styles)s >%(M3_tokens)s
		</div>
		<div id="M4_zone"><img %(M4_paths)s %(M4_styles)s >%(M4_tokens)s
		</div>
		<div id="M5_zone"><img %(M5_paths)s %(M5_styles)s >%(M5_tokens)s
		</div>
		<div id="graveyard_zone"><img %(graveyard_paths)s %(graveyard_styles)s >
		</div>
		<div id="banished_zone"><img %(banished_paths)s %(banished_styles)s >
		</div>
	
		<div id="extra_deck_zone"><img %(extra_deck_paths)s %(extra_deck_styles)s >
		</div>
		<div id="ST1_zone"><img %(ST1_paths)s %(ST1_styles)s >%(ST1_tokens)s
		</div>
		<div id="ST2_zone"><img %(ST2_paths)s %(ST2_styles)s >%(ST2_tokens)s
		</div>
		<div id="ST3_zone"><img %(ST3_paths)s %(ST3_styles)s >%(ST3_tokens)s
		</div>
		<div id="ST4_zone"><img %(ST4_paths)s %(ST4_styles)s >%(ST4_tokens)s
		</div>
		<div id="ST5_zone"><img %(ST5_paths)s %(ST5_styles)s >%(ST5_tokens)s
		</div>
		<div id="deck_zone"><img %(deck_paths)s %(deck_styles)s >
		</div>
		<br>
	</div>
	<div id="hand">
		%(hand)s
	</div>
	<div>
	<form method='post'>Enter text:<input type='text' name='%(player_name)s_command' autofocus><input type='submit' value='Go!'></form>
	</div>
</body>
</html>""" % format_dict
	
	return page

#Returns the html that represents a player's deck in-game
def get_swipe_html( card_list, game, player ):
	left_content = ''
	right_side = '<div id="big_card" style="float:left"></div>'
	for i in range( len(card_list) ):
		p = int(card_list[i])
		slot = 'S' + str(i+1)
		left_content += '<img id={0} src="{1}" style="width:114px;height:167px" onClick="showImage(\'{0}\');"> {2}\n'.format( slot, get_card_path( p, game.get_deck_name(player) ), i+1 )
	left_side = '<div id="card_list" style="float:left;height:600px;width:160px;overflow:scroll;margin-right:10px">{}</div>'.format( left_content)
	return_html = """<html>
<body>
<script>
function showImage(img_id)
{{
	var largeImage = document.getElementById(img_id);
	var url=largeImage.getAttribute('src');
	document.getElementById('big_card').innerHTML = "<img src='" + url + "' >";
}}
</script>
{}
{}
</body>
</html>""".format( left_side, right_side )
	return return_html

#Returns the html that allows someone to create a new game
def get_new_game_html():
	return_html = """<!DOCTYPE html>
<html>
<head>
<title>Create game</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
<body>

<form method="post">
Game Name: <input type="text" name="game_name">
<br>
<br>
Player One's name: <input type="text" name="P1_name">
<br>
Player Two's name: <input type="text" name="P2_name">
<br>
Player One's Deck:
"""
	return_html += html_util.get_select_html( deck_util.get_decks_list(), 'P1_deck' )
	return_html += """<br>
Player Two's Deck:
"""
	return_html += html_util.get_select_html( deck_util.get_decks_list(), 'P2_deck' )
	return_html += """<br>
<input type="submit" value="Create game">
</form>
<br>
<a href="/games">Go back</a>
</body>
</html>"""
	return return_html

#Creates a new game with the given dictionary
def create_game( game_form_dict ):
	game_dict = { 'P1_LP': '8000', 'P2_LP': '8000' }
	game_dict['P1_NAME'] = game_form_dict['P1_name']
	game_dict['P2_NAME'] = game_form_dict['P2_name']
	P1_deck_name = game_form_dict['P1_deck']
	P2_deck_name = game_form_dict['P2_deck']
	game_dict['P1_DECK_NAME'] = P1_deck_name
	game_dict['P2_DECK_NAME'] = P2_deck_name
	P1_deck_size = len( deck_util.get_deck_list( P1_deck_name ) )
	P2_deck_size = len( deck_util.get_deck_list( P2_deck_name ) )
	P1_deck_str = ''
	for i in range(P1_deck_size):
		P1_deck_str += str(i+1) + ';'
	P2_deck_str = ''
	for i in range(P2_deck_size):
		P2_deck_str += str(i+1) + ';'
	game_dict['P1_DECK'] = P1_deck_str[:-1]
	game_dict['P2_DECK'] = P2_deck_str[:-1]
	
	save_game( game_dict, game_form_dict['game_name'] )
	
	return_html = """<!DOCTYPE html>
<head>
<title>Create game</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
Done!
<br>
<br>
<a href="/games">Back to games</a>"""
	return return_html

#Returns the html that allows someone to delete a saved game
def get_delete_game_html():
	return_html = """<!DOCTYPE html>
<html>
<head>
<title>Delete game</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
<body>

<form method="post">
Game:
"""
	return_html += html_util.get_select_html( get_games_list(), 'game_name' )
	return_html += """<input type="submit" value="Delete game">
</form>
<br>
<a href="/games">Go back</a>
</body>
</html>"""
	return return_html

#Deletes a game
def delete_game( game_name ):
	os.remove( game_folder + str(game_name) + game_ext )
	return_html = """<!DOCTYPE html>
<head>
<title>Delete game</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
Done!
<br>
<br>
<a href="/games">Back to games</a>"""
	return return_html

#Returns the html that allows someone to start playing a running game
def gen_play_game_html( game_names ):
	return_html = """<!DOCTYPE html>
<html>
<head>
<title>Play game</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
<body>

<form method="get">
Game:
"""
	return_html += html_util.get_select_html( game_names, 'name' )
	return_html += """<br>
Player:
"""
	return_html += html_util.get_select_html( ['P1', 'P2'], 'player' )
	return_html += """<br>
<input type="submit" value="Play game">
</form>
<br>
<a href="/games">Go back</a>
</body>
</html>"""
	return return_html

#Returns the html that allows someone to start running a game
def get_start_game_html( game_names ):
	return_html = """<!DOCTYPE html>
<html>
<head>
<title>Start game</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
<body>

<form method="post">
Game:
"""
	return_html += html_util.get_select_html( game_names, 'name' )
	return_html += """<input type="submit" value="Start game">
</form>
<br>
<a href="/games">Go back</a>
</body>
</html>"""
	return return_html

def get_started_game_html( game_name ):
	return_html = """<!DOCTYPE html>
<html>
<head>
<title>Start game</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
<body>
Game "{}" started!<br><br><a href="/games">Back to games</a>
</body>
</html>""".format( game_name )
	return return_html

#Returns the html that allows someone to stop a running a game
def get_stop_game_html( game_names ):
	return_html = """<!DOCTYPE html>
<html>
<head>
<title>Stop game</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
<body>

<form method="post">
Game:
"""
	return_html += html_util.get_select_html( game_names, 'name' )
	return_html += """<input type="submit" value="Stop game">
</form>
<br>
<a href="/games">Go back</a>
</body>
</html>"""
	return return_html

def get_stopped_game_html( game_name ):
	return_html = """<!DOCTYPE html>
<html>
<head>
<title>Stop game</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
<body>
Game "{}" stopped.<br><br><a href="/games">Back to games</a>
</body>
</html>""".format( game_name )
	return return_html