import os
import game_util
import urllib2
from bs4 import BeautifulSoup

'''
	Used to create/edit decks to be used in games.
'''

deck_folder = 'deck\\'
deck_ext = '.d.txt'

#Returns a list of all the saved decks
def get_decks_list():
	deck_list = []
	for deck in os.listdir(deck_folder):
		if deck.endswith(deck_ext):
			deck_list.append( deck.split(deck_ext)[0] )
	return deck_list

#Returns a list of all the cards in a saved deck
def get_deck_list( deck_name ):
	return_list = []
	with open( deck_folder + deck_name + deck_ext, 'r' ) as file:
		for line in file:
			return_list.append( line )
	return return_list

#Returns the html for creating/editing/etc. decks
def gen_decks_html():
	decks_html = """<html>
<head>
<title>Decks</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
<body>
<div id="g" style="margin-right:20px">
Here are the decks currently saved:
<br>
<br>
"""
	decks = get_decks_list()
	for deck_name in decks:
		decks_html += '<a href="deck?name=' + deck_name + '">' + deck_name + '</a><br>'
	decks_html += """</div>
<br>
<br>
<div id="g">
<a href="/new_deck">Make a new deck</a>
<br>
<a href="/edit_deck">Edit an existing deck</a>
<br>
<a href="/delete_deck">Delete an existing deck</a>
<br>
<a href="/advanced_deck">--NEW-- Advanced deck creation</a>
</div>
<div style="clear:both">
<br>
<br>
<a href="/">Go back</a>
</div>
</body>
</html>"""
	return decks_html

#Returns the html that represents the saved deck
def gen_deck_html( deck_name ):
	return_html = """<html>
<head>
<title>View deck</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
<body>
<table style="border: 1px solid black">
	<tr>
		<th>{}</th>
		<th>{}</th>
	</tr>
""".format( 'Position', 'Value' )
	with open( deck_folder + deck_name + deck_ext, 'r' ) as file:
		i = 1
		for line in file:
			pos = i
			val = line
			return_html += """	<tr>
		<td>{}</td>
		<td>{}</td>
	</tr>""".format( pos, val )
			i += 1
	return_html += """</table>
<br>
<a href="/decks">Go back</a>
</body>
</html>"""
	return return_html

#Returns the html that allows someone to create a deck
def get_new_deck_html():
	return_html = """<!DOCTYPE html>
<html>
<head>
<title>Create deck</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
<body>

<form method="post">
<input type="text" name="deck_name" value="Enter deck name here!">
<br>
<textarea name='deck_text' rows="20" cols="30">
Enter cards here!</textarea>
<input type="submit" value="Create deck">
</form>
<br>
<a href="/decks">Go back</a>
</body>
</html>"""
	return return_html

def get_advanced_deck_html():
	return_html = """<!DOCTYPE html>
<html>
<head>
<title>Advanced deck</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
<body>

<form method="post">
<input type="text" name="deck_name">
<br>
<input type="submit" value="Create deck">
</form>
<br>
<a href="/decks">Go back</a>
</body>
</html>"""
	return return_html

#Returns the html that allows someone to choose a deck to edit
def get_edit_deck_html():
	return_html = """<!DOCTYPE html>
<html>
<head>
<title>Edit deck</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
<body>

<form method="get">
"""
	return_html += game_util.get_select_html( get_decks_list(), 'name' )
	return_html += """<input type="submit" value="Edit deck">
</form>
<br>
<a href="/decks">Go back</a>
</body>
</html>"""
	return return_html

#Returns the html that allows someone to edit a deck
def gen_edit_deck_html( deck_name ):
	return_html = """<!DOCTYPE html>
<html>
<head>
<title>Edit deck</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
<body>

<form method="post">
<input type="text" name="deck_name" value="{}">
<br>
<textarea name='deck_text'>
""".format(deck_name)
	card_list = get_deck_list( deck_name )
	for card in card_list:
		return_html += card
	if return_html.endswith('\n'):
		return_html = return_html[:-1]
	return_html += """</textarea>
<input type="submit" value="Save changes">
</form>
<br>
<a href="/edit_deck">Go back</a>
</body>
</html>"""
	return return_html

#Returns the html that allows someone to choose a deck to delete
def get_delete_deck_html():
	return_html = """<!DOCTYPE html>
<html>
<head>
<title>Delete deck</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
<body>

<form method="post">
"""
	return_html += game_util.get_select_html( get_decks_list(), 'deck_name' )
	return_html += """</select><input type="submit" value="Delete deck">
</form>
<br>
<a href="/decks">Go back</a>
</body>
</html>"""
	return return_html

#Creates a deck with the given deck name and deck contents
def create_deck( deck_name, deck_list ):
	deck_path = deck_folder + deck_name + deck_ext
	deck_string = ''
	for card in deck_list:
		deck_string += card + '\n'
	with open( deck_path, 'w' ) as file:
		file.write(deck_string)
	return_html = """<!DOCTYPE html>
<head>
<title>Create deck</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
Done!
<br>
<br>
<a href="/decks">Back to decks</a>"""
	return return_html

def advanced_deck( deck_name ):
	response = None
	formatted = deck_name.replace(' ', '_')
	offset = 1
	name_slot = 2
	amount_slot = 5

	#Try two different urls to see what works
	try:
		response = urllib2.urlopen( 'http://yugioh.wikia.com/wiki/Set_Card_Lists:{}_Structure_Deck_(TCG-EN)'.format( formatted ) )
	except urllib2.HTTPError:
		print 'Failed first url, trying second.'
		try:
			response = urllib2.urlopen( 'http://yugioh.wikia.com/wiki/Set_Card_Lists:Structure_Deck:_{}_(TCG-EN)'.format( formatted ) )
		except urllib2.HTTPError:
			print 'Failed second url, stopping.'
			return None
	html = response.read()

	soup = BeautifulSoup(html)
	results = []

	all_rows = soup.find_all('tr')
	if all_rows[1].td == None:
		offset = 2

	for row in soup.find_all('tr')[offset:]:
		tag_list = []
		for tag in row:
			tag_list.append(tag)
		print tag_list
		results.append( (tag_list[name_slot].a.string, tag_list[amount_slot].string.replace('\n', '') ) )

	deck_string = ''
	deck_list = []
	for result in results:
		for i in range( int(result[1]) ):
			deck_list.append( result[0] )
			deck_string += result[0] + '\n'
	print deck_string
	create_deck( deck_name, deck_list )
	return_html = """<!DOCTYPE html>
<head>
<title>Advanced deck</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
Done!
<br>
<br>
<a href="/decks">Back to decks</a>"""
	return return_html

#Deletes the deck with given name, returns a confirmation web page
def delete_deck( deck_name ):
	os.remove( deck_folder + str(deck_name) + deck_ext )
	return_html = """<!DOCTYPE html>
<head>
<title>Delete deck</title>
<link rel="stylesheet" type="text/css" href="static/site.css">
<link rel="icon" type="image/png" href="static/favicon.png" />
</head>
Done!
<br>
<br>
<a href="/decks">Back to decks</a>"""
	return return_html