from flask import Flask, render_template, request
from game import Game
import game_util, deck_util, html_util
app = Flask(__name__)

#Stores the games that are currently being played
games_running = {}
#Go ahead and add test game for testing purposes
games_running['test'] = Game('test')

@app.route("/", methods=['GET'])
def main():
	return render_template("main.html")

@app.route("/about", methods=['GET'])
def about():
	return html_util.get_about_html()

@app.route("/welcome", methods=['GET'])
def welcome():
	return '<img src="static\\cats.jpg">'

@app.route("/games", methods=['GET'])
def games():
	return game_util.gen_games_html( games_running.keys() )
		
@app.route("/game", methods=['GET'])
def game():
	game_name = request.args.get('name', '')
	return game_util.gen_game_html( game_name )

@app.route("/new_game", methods=['GET', 'POST'])
def new_game():
	if request.method == 'GET':
		return game_util.get_new_game_html()
	elif request.method == 'POST':
		print request.form
		response = game_util.create_game( request.form )
		return response
	
@app.route("/edit_game", methods=['GET', 'POST'])
def edit_game():
	return 'Still working on it'
	
@app.route("/delete_game", methods=['GET', 'POST'])
def delete_game():
	if request.method == 'GET':
		return game_util.get_delete_game_html()
	elif request.method == 'POST':
		response = game_util.delete_game( request.form['game_name'] )
		return response

@app.route("/start_game", methods=['GET', 'POST'])
def start_game():
	if request.method == 'GET':
		not_running = []
		for game in game_util.get_games_list():
			if game not in games_running:
				not_running.append( game )
		return game_util.get_start_game_html( not_running )
	elif request.method == 'POST':
		game_name = request.form['name']
		games_running[game_name] = Game(game_name)
		return game_util.get_started_game_html( game_name )

@app.route("/stop_game", methods=['GET', 'POST'])
def stop_game():
	if request.method == 'GET':
		return game_util.get_stop_game_html( games_running.keys() )
	elif request.method == 'POST':
		game_name = request.form['name']
		del( games_running[game_name] )
		return game_util.get_stopped_game_html( game_name )

@app.route("/decks", methods=['GET'])
def decks():
	return deck_util.gen_decks_html()

@app.route("/deck", methods=['GET'])	
def deck():
	deck_name = request.args.get('name', '')
	return deck_util.gen_deck_html( deck_name )

@app.route("/new_deck", methods=['GET', 'POST'])
def new_deck():
	if request.method == 'GET':
		return deck_util.get_new_deck_html()
	elif request.method == 'POST':
		response = deck_util.create_deck( request.form['deck_name'], request.form['deck_text'].split('\r\n') )
		return response

@app.route("/advanced_deck", methods=['GET', 'POST'])
def advanced_deck():
	if request.method == 'GET':
		return deck_util.get_advanced_deck_html()
	elif request.method == 'POST':
		response = deck_util.advanced_deck( request.form['deck_name'] )
		return response

@app.route("/edit_deck", methods=['GET', 'POST'])
def edit_deck():
	deck_name = request.args.get('name', '')
	if request.method == 'GET':
		if deck_name == '':
			return deck_util.get_edit_deck_html()
		else:
			return deck_util.gen_edit_deck_html(deck_name)
	elif request.method == 'POST':
		response = deck_util.create_deck( request.form['deck_name'], request.form['deck_text'].split('\r\n') )
		return response

@app.route("/delete_deck", methods=['GET', 'POST'])
def delete_deck():
	if request.method == 'GET':
		return deck_util.get_delete_deck_html()
	elif request.method == 'POST':
		response = deck_util.delete_deck( request.form['deck_name'] )
		return response

@app.route("/play", methods=['GET', 'POST'])
def play():
	#If there weren't any html args provided, show options
	if len(request.args) == 0:
		return game_util.gen_play_game_html( games_running.keys() )
	else:
		game_name = request.args.get('name', '')
		player_name = request.args.get('player', '')
		view = request.args.get('view', 'board')
		if game_name in games_running.keys():
			g = games_running[game_name]
			if (player_name in ['P1', 'P2']) and (view in ['board', 'deck', 'graveyard', 'banished', 'extra']):
				if view == 'board':
					if request.method == 'POST':
						g.send( request.form['{}_command'.format(player_name)], player_name )
					return render_template( "{}_{}.html".format( game_name, player_name ) )
				elif view == 'deck':
					card_list = g.get_deck( player_name )
				elif view == 'graveyard':
					card_list = g.get_graveyard( player_name )
				elif view == 'banished':
					card_list = g.get_banished( player_name )
				elif view == 'extra':
					card_list = g.get_extra( player_name )
				return game_util.get_swipe_html( card_list, g, player_name )
	
		return 'Nothing here!'

if __name__ == "__main__":
    app.debug = True
    app.run('0.0.0.0')