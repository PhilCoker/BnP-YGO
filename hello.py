from flask import Flask, render_template, request
from game import Game
import game_util
app = Flask(__name__)

#Game is started
the_game = Game('test')

@app.route("/", methods=['GET'])
def main():
	return render_template("main.html")
	
@app.route("/games", methods=['GET'])
def games():
	return game_util.gen_games_html()
	
@app.route("/decks", methods=['GET'])
def decks():
	return game_util.gen_decks_html()

@app.route("/game", methods=['GET', 'POST'])
def hello():
	game_name = request.args.get('name', '')
	player_name = request.args.get('player', '')
	if player_name in ['P1', 'P2']:
		if request.method == 'GET':
			return render_template( "{}_{}.html".format( game_name, player_name ) )
		elif request.method == 'POST':
			the_game.send( request.form['{}_command'.format(player_name)], player_name )
			return render_template( "{}_{}.html".format( game_name, player_name ) )
	else:
		return 'Sorry, nothing here!'

if __name__ == "__main__":
    app.debug = True
    app.run()