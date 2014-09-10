import os

'''
	A bunch of utility functions to aid the game.
'''

#Returns the URL of the card given at Yugioh Prices
def get_image_path( card_name ):
	base = 'http://static.api5.studiobebop.net/ygo_data/card_images/'
	
	replaced = card_name.replace( ' ', '_' ).replace('-','_')
	url = base + replaced + '.jpg'
	return url

def gen_games_html():
	games_html = """<html>
<head>
<title>Games</title>
</head>
Here are the game files currently saved:
<br>
"""
	for game in os.listdir('game'):
		games_html += game.split('.')[0] + '<br>'
	games_html += """<a href="main.html">Go back</a>
</html>"""
	return games_html

def gen_decks_html():
	decks_html = """<html>
<head>
<title>Decks</title>
</head>
Here are the decks currently saved:
<br>
"""
	for deck in os.listdir('deck'):
		print deck.split('.')[0]
		decks_html += deck.split('.')[0] + '<br>'
	decks_html += """<a href="/">Go back</a>
</html>"""
	return decks_html

def get_token_html( num ):
	token_image = '<img src="http://www.nigeltomm.com/images/orange_square_nigel_tomm_m.jpg" style="float:left;position:relative;width:10px;height:10px;top:-212px;left:'
	return_html = ''
	for i in range(1, num+1):
		return_html += token_image + str(10*i) + 'px">'
	return return_html
		

def get_board_html( game, player):
	back = 'http://images.wikia.com/yugioh/images/archive/e/e5/20080209143844!Back-EN.png'
	error = 'http://www.katiescarbrough.co.uk/wp-content/uploads/a-big-x-2-473x350.jpg'
	paths = []
	styles = []
	tokens = []
	
	#The player's side of the field
	#Field
	field = game.get_field(player)
	if field != []:
		field_split = field[0].split(':')
		card_num = int(field_split[0])
		pos = int( field_split[1] )
		if pos == 0:
			paths.append( game.get_card_path( card_num, player ) )
		elif pos == 2:
			paths.append( back )
		else:
			paths.append(error)
		styles.append('id="field_card" onClick=\'swipe("field_card");\'')
		
		#Add tokens, if any
		if len( field_split ) > 2:
			token_num = int( field_split[2] )
			tokens.append( get_token_html( token_num ) )
		else:
			tokens.append('')
	else:
		paths.append('')
		styles.append('')
		tokens.append('')
	#Monsters
	monsters = game.get_monsters(player)
	for i in range(len(monsters)):
		m = monsters[i]
		if m != '':
			m_split = m.split(':')
			card_num = int(m_split[0])
			pos = int( m_split[1] )
			
			#Add image path
			if (pos == 0) or (pos == 1):
				paths.append( game.get_card_path( card_num, player ) )
			elif (pos == 2) or (pos == 3):
				paths.append( back )
			else:
				paths.append( error )
			
			#Add style
			new_style = ''
			if (pos==1) or (pos == 3):
				new_style = 'style="-webkit-transform: rotate(-90deg);-moz-transform: rotate(-90deg);" '
			new_style += 'id="M{0}_card" onClick=\'swipe("M{0}_card");\''.format(i+1)
			styles.append(new_style)
			
			#Add tokens, if any
			if len( m_split ) > 2:
				token_num = int( m_split[2] )
				tokens.append( get_token_html( token_num ) )
			else:
				tokens.append('')
		else:
			paths.append('')
			styles.append('')
			tokens.append('')
	#Graveyard
	grave = game.get_graveyard(player)
	if grave != []:
		paths.append( game.get_card_path( int(grave[-1]), player ) )
	else:
		paths.append('')
	styles.append('')
	
	#Extra deck
	extra = game.get_extra(player)
	if extra != []:
		paths.append( game.get_card_path( int(extra[-1]), player ) )
	else:
		paths.append('')
	styles.append('')
	#Spells/traps
	spells = game.get_spells(player)
	for i in range(len(spells)):
		s = spells[i]
		if s != '':
			s_split = s.split(':')
			card_num = int(s_split[0])
			pos = int( s_split[1] )
			if (pos == 0) or (pos == 1):
				paths.append( game.get_card_path( card_num, player ) )
			elif (pos == 2) or (pos == 3):
				paths.append( back )
			else:
				paths.append( error )
			
			new_style = ''
			if (pos==1) or (pos == 3):
				new_style = 'style="-webkit-transform: rotate(-90deg);-moz-transform: rotate(-90deg);" '
			new_style += 'id="ST{0}_card" onClick=\'swipe("ST{0}_card");\''.format(i+1)
			styles.append(new_style)
			
			#Add tokens, if any
			if len( s_split ) > 2:
				token_num = int( s_split[2] )
				tokens.append( get_token_html( token_num ) )
			else:
				tokens.append('')
		else:
			paths.append('')
			styles.append('')
			tokens.append('')
	#Deck
	deck = game.get_deck(player)
	if deck != []:
		paths.append(back)
	else:
		paths.append('')
	styles.append('')
	#Hand
	hand = game.get_hand(player)
	hand_html = ''
	offset = 0
	for i in range( len(hand) ):
		card_num = hand[i]
		hand_html = hand_html + '<img src="{0}" style="float:left;position:relative;left:{1}px" id="H{2}_card" onClick=\'swipe("H{2}_card");\' >\n\t\t'.format( game.get_card_path( int(card_num), player ), offset, i )
		offset = offset - 50
	page = """<!DOCTYPE HTML>
<html>
<head>
<title>Yu-Gi-Oh!</title>
<link rel="stylesheet" type="text/css" href={{{{ url_for('static', filename="gameboard.css") }}}} />
<link rel="icon" type="image/png" href={{{{ url_for('static', filename="favicon.png") }}}} />
</style>

</head>
<body>
<script>
function swipe(img_id)
{{
	var largeImage = document.getElementById(img_id);
	var url=largeImage.getAttribute('src');
	window.open(url,'Image','width=largeImage.stylewidth,height=largeImage.style.height,resizable=1');
}}
</script>
Life Points: {30}
	<div id="board">
		<div id="field_zone"><img src="{0}" {14} >{31}
		</div>
		<div id="M1_zone"><img src="{1}" {15}>{32}
		</div>
		<div id="M2_zone"><img src="{2}" {16}>{33}
		</div>
		<div id="M3_zone"><img src="{3}" {17}>{34}
		</div>
		<div id="M4_zone"><img src="{4}" {18}>{35}
		</div>
		<div id="M5_zone"><img src="{5}" {19}>{36}
		</div>
		<div id="graveyard_zone"><img src="{6}" {20}>
		</div>
	
		<div id="extra_deck_zone"><img src="{7}" {21}>
		</div>
		<div id="ST1_zone"><img src="{8}" {22}>{37}
		</div>
		<div id="ST2_zone"><img src="{9}" {23}>{38}
		</div>
		<div id="ST3_zone"><img src="{10}" {24}>{39}
		</div>
		<div id="ST4_zone"><img src="{11}" {25}>{40}
		</div>
		<div id="ST5_zone"><img src="{12}" {26}>{41}
		</div>
		<div id="deck_zone"><img src="{13}" {27}>
		</div>
		<br>
	</div>
	<div id="hand">
		{28}
	</div>
	<div>
	<form method='post'>Enter text:<input type='text' name='{29}_command' autofocus><input type='submit' value='Go!'>
	</div>
</body>
</html>""".format( paths[0], paths[1], paths[2], paths[3], paths[4], paths[5], paths[6], paths[7], paths[8], paths[9], paths[10], paths[11], paths[12], paths[13], styles[0], styles[1], styles[2], styles[3], styles[4], styles[5], paths[6], styles[7], styles[8], styles[9], styles[10], styles[11], styles[12], styles[13], hand_html, player, game.get_LP(player), tokens[0], tokens[1], tokens[2], tokens[3], tokens[4], tokens[5], tokens[6], tokens[7], tokens[8], tokens[9], tokens[10] )
		
	return page