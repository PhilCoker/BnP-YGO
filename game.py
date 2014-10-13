import os
import sys
import string
import random
import socket
import time
import game_util

#Represents a game of Yu-Gi-Oh between two players.
class Game:

	def __init__(self, game_name='test' ):
		self.game_name = game_name
		self.tag_dict = game_util.load_game( game_name )
		self.undo = []
		self.history_u = []
		self.history_g = []
		for p in ['P1', 'P2']:
			game_util.write_html(self, p)

	#A bunch of getters to abstract how the data is stored
	def get_deck( self, player ):
		try:
			split = self.tag_dict[player+'_DECK'].split(';')
		except KeyError:
			return []
		return [] if split == [''] else split
	def get_hand( self, player ):
		try:
			split = self.tag_dict[player+'_HAND'].split(';')
		except KeyError:
			return []
		return [] if split == [''] else split
	def get_monsters( self, player ):
		ret_monsters = []
		try:
			ret_monsters = self.tag_dict[player+'_M'].split(';')
		except KeyError:
			pass
		while len(ret_monsters) < 5:
			ret_monsters.append('')
		return ret_monsters
	def get_spells( self, player ):
		ret_spells = []
		try:
			ret_spells = self.tag_dict[player+'_S'].split(';')
		except KeyError:
			pass
		while len(ret_spells) < 5:
			ret_spells.append('')
		return ret_spells
	def get_graveyard( self, player ):
		try:
			split = self.tag_dict[player+'_GRAVE'].split(';')
		except KeyError:
			return []
		return [] if split == [''] else split
	def get_extra( self, player ):
		try:
			split = self.tag_dict[player+'_EXTRA'].split(';')
		except KeyError:
			return []
		return [] if split == [''] else split
	def get_field( self, player ):
		try:
			split = self.tag_dict[player+'_FIELD'].split(';')
		except KeyError:
			return []
		return [] if split == [''] else split
	def get_banished( self, player ):
		try:
			split = self.tag_dict[player+'_BANISHED'].split(';')
		except KeyError:
			return []
		return [] if split == [''] else split
	def get_deck_name( self, player ):
		return self.tag_dict[player+'_DECK_NAME']
	def get_LP( self, player ):
		return self.tag_dict[player+'_LP']
	#A bunch of setters, to abstract how the data is stored
	def set_deck( self, deck_list, player ):
		new_deck = ''
		for d in deck_list:
			new_deck += d + ';'
		self.tag_dict[player+'_DECK'] = new_deck[:-1]
	def set_hand( self, hand_list, player ):
		new_hand = ''
		for h in hand_list:
			new_hand += h + ';'
		self.tag_dict[player+'_HAND'] = new_hand[:-1]
	def set_monsters( self, monsters_list, player ):
		trimmed_list = list(monsters_list)
		#Trim trailing empty strings
		while (len(trimmed_list) > 0) and (trimmed_list[-1] == ''):
			trimmed_list.pop()
		new_monsters = ''
		for m in trimmed_list:
			new_monsters += m + ';'
		self.tag_dict[player+'_M'] = new_monsters[:-1]
	def set_spells( self, spells_list, player ):
		trimmed_list = list(spells_list)
		#Trim trailing empty strings
		while (len(trimmed_list) > 0) and (trimmed_list[-1] == ''):
			trimmed_list.pop()
		new_spells = ''
		for s in trimmed_list:
			new_spells += s + ';'
		self.tag_dict[player+'_S'] = new_spells[:-1]
	def set_graveyard( self, graveyard_list, player ):
		new_graveyard = ''
		for g in graveyard_list:
			new_graveyard += g + ';'
		self.tag_dict[player+'_GRAVE'] = new_graveyard[:-1]
	def set_extra( self, extra_list, player ):
		new_extra = ''
		for e in extra_list:
			new_extra += e + ';'
		self.tag_dict[player+'_EXTRA'] = new_extra[:-1]
	def set_field( self, field_list, player ):
		new_field = ''
		for f in field_list:
			new_field += f + ';'
		self.tag_dict[player+'_FIELD'] = new_field[:-1]
	def set_banished( self, banished_list, player ):
		new_banished = ''
		for b in banished_list:
			new_banished += b + ';'
		self.tag_dict[player+'_BANISHED'] = new_banished[:-1]
	def set_LP( self, new_LP, player ):
		self.tag_dict[player+'_LP'] = new_LP
	
	#Shuffles the deck of the given player
	def shuffle( self, player ):
		if player in ('P1', 'P2'):
			deck = self.get_deck(player)
			random.shuffle(deck)
			self.set_deck( deck, player )
	
	#Removes the top card from the deck and adds it to the hand
	def draw( self, player ):
		if player in ('P1', 'P2'):
			pulled = self.pull( 'd1', player )
			if pulled != None:
				hand = self.get_hand(player)
				hand_size = len(hand)
				self.put( pulled, 'h' + str(hand_size+1) , player )
			else:
				print 'Got back none type!'
				self.put( pulled, 'd1', player )
		else:
			print 'Found bad player: {}'.format(player)

	#Removes a card from the hand and places it on top of the graveyard
	#E.g. discard( '2', 'P1' ) will make player one discard the second hand in his hand
	def discard( self, slot, player ):
		if player in ['P1', 'P2']:
			pulled = self.pull( 'h' + slot, player )
			if pulled != None:
				graveyard = self.get_graveyard(player)
				grave_size = len(graveyard)
				self.put( pulled, 'g' + str(grave_size+1), player )
			else:
				print 'Got back none type!'
		else:
			print 'Found bad player: {}'.format(player)
	
	#Removes a card from the top of the deck and places it on top of the graveyard
	#E.g. mill( 5, 'P1' ) will make player one mill 5 cards
	def mill( self, times, player ):
		for i in range(times):
			pulled = self.pull( 'd1', player )
			if pulled != None:
				graveyard = self.get_graveyard(player)
				grave_size = len(graveyard)
				self.put( pulled, 'g' + str(grave_size+1), player )
	
	#Removes a card from the hand and places it into the monster, spell, or field zone
	def play( self, hand_slot, field_slot, position, player ):
		if player in ['P1', 'P2']:
			pulled = self.pull( 'h' + hand_slot, player )
			if pulled != None:
				self.put( pulled, field_slot, player, [position] )
			else:
				print 'Got back none type in play.'
	
	#Removes a card from the monster, spell, or field zone and places it on top of the deck
	def spin( self, field_slot, player ):
		pulled = self.pull( field_slot, player )
		if pulled != None:
			self.put( pulled.split(':')[0], 'd1', player )
		else:
			print 'Got back none type in spin.'
	
	#Sets/adjusts a player's life points
	def lp( self, mode, amount, player ):
		if mode in ['set', 'adjust']:
			if mode == 'set':
				self.set_LP( amount, player )
			elif mode == 'adjust':
				int_LP = int(self.get_LP(player))
				int_adjust = int(amount)
				self.set_LP( str(int_LP+int_adjust), player )
			else:
				print 'Bad mode argument on lp statement: {}'.format( mode )
		
	#Removes a card from the monster, spell, or field zone and places it on top of the graveyard
	def destroy( self, field_slot, player ):
		pulled = self.pull( field_slot, player )
		if pulled != None:
			graveyard = self.get_graveyard(player)
			grave_size = len(graveyard)
			self.put( pulled.split(':')[0], 'g' + str(grave_size+1), player ) 
		else:
			print 'Got back none type in destroy.'
	
	#Removes a card from the monster, spell, or field zone and returns it to the hand
	def return_card( self, field_slot, player ):
		pulled = self.pull( field_slot, player )
		if pulled != None:
			hand_size = len(self.get_hand(player))
			self.put( pulled.split(':')[0], 'h'+str(hand_size+1), player)
		else:
			print 'Got back none type in return card.'
	
	#Changes the position of a card on the playing field
	def flip( self, field_slot, new_pos, player ):
		if new_pos in ['0', '1', '2', '3']:
			pulled = self.pull( field_slot, player )
			if pulled != None:
				pulled_split = pulled.split(':')
				#Change the position of the card
				pulled_split[1] = new_pos
				self.put( pulled_split[0], field_slot, player, pulled_split[1:] )
			else:
				print 'Got back none type in flip.'
		else:
			print 'Bad new position in flip: {}.'.format( new_pos )
	
	#Sets/adjusts the number of tokens on a field card
	def token( self, field_slot, mode, amount, player ):
		if mode in ['set', 'adjust']:
			pulled = self.pull( field_slot, player )
			if pulled != None:
				if pulled != '':
					pulled_split = pulled.split(':')
					if len(pulled_split) != 3:
						pulled_split.append('0')
					if mode == 'set':
						pulled_split[2] = amount
					elif mode == 'adjust':
						pulled_split[2] = str( int(pulled_split[2]) + int(amount) )
					self.put( pulled_split[0], field_slot, player, pulled_split[1:3] )
				else:
					print 'No card is in play at field slot {} in token.'.format( field_slot )
			else:
				print 'Got back none type in token.'
		else:
			print 'Bad mode in token: {}'.format(mode)
	
	#Banishes a card
	def banish( self, field_slot, player ):
		pulled = self.pull( field_slot, player )
		if pulled != None:
			if pulled != '':
				banished = self.get_banished(player)
				banished_size = len(banished)
				self.put( pulled.split(':')[0], 'b' + str(banished_size+1), player )
			else:
				print 'No card is in play at field slot {} in banish.'.format( field_slot )
		else:
			print 'Got back none type in banish.'
	
	#Switches between player one and two
	def switch_turn( self ):
		if self.tag_dict['TURN'] == 'P1':
			self.tag_dict['TURN'] = 'P2'
		elif self.tag_dict['TURN'] == 'P2':
			self.tag_dict['TURN'] = 'P1'
		else:
			print 'Found bad player: {}'.format( self.tag_dict['TURN'] )
	
	#Big kahoona!
	#Returns True if successful, false otherwise.
	def send( self, msg, player ):
		good_msg = 'OK'
		msg_parsed = msg.split(' ')
		main = msg_parsed[0]
		if main in ['draw', 'refresh', 'discard', 'mill', 'save', 'play', 'spin', 'lp', 'destroy', 'shuffle', 'return', 'flip', 'token', 'banish', 'tell']:
			if main == 'draw':
				if len(msg_parsed) == 1:
					self.draw( player )
				else:
					print 'Bad draw statement. Try: "draw"'
					return False
			elif main == 'refresh':
				if len(msg_parsed) == 1:
					pass
				else:
					print 'Bad refresh statement. Try: "refresh"'
					return False
			elif main == 'discard':
				if len(msg_parsed) == 2:
					self.discard( msg_parsed[1], player )
				else:
					print 'Bad discard statement. Try "discard x" where x is the hand slot.'
					return False
			elif main == 'mill':
				if len(msg_parsed) == 2:
					self.mill( int(msg_parsed[1]), player )
				else:
					print 'Bad mill statement. Try "mill x" where x is the number of cards to mill.'
					return False
			elif main == 'save':
				if len(msg_parsed) == 1:
					game_util.save_game(self.tag_dict)
				elif len(msg_parsed) == 2:
					game_util.save_game( self.tag_dict, msg_parsed[1] )
				else:
					print 'Bad save statement. Try "save" to save to a default file, or "save x" to save to x.g.txt.'
					return False
			elif main == 'play':
				if len(msg_parsed) == 4:
					self.play( msg_parsed[1], msg_parsed[2], msg_parsed[3], player )
				else:
					print 'Bad play statement. Try "play 1 m3 0" to play the first card in your hand to the third monster slot in faceup attack position.'
					return False
			elif main == 'spin':
				if len(msg_parsed) == 2:
					self.spin( msg_parsed[1], player )
				else:
					print 'Bad spin statement. Try "spin m3" to return the third monster on the field to the top of your deck.'
					return False
			elif main == 'lp':
				if len(msg_parsed) == 3:
					self.lp( msg_parsed[1], msg_parsed[2], player )
				else:
					print 'Bad lp statement. Try "lp set 2000" to set your life points to 2000, or "lp adjust 200"/"lp adjust -200" to raise/lower your life points by 200.'
					return False
			elif main == 'destroy':
				if len(msg_parsed) == 2:
					self.destroy( msg_parsed[1], player )
				else:
					print 'Bad destroy statement. Try "destroy m2" to send the second monster to the graveyard.'
					return False
			elif main == 'shuffle':
				if len(msg_parsed) == 1:
					self.shuffle(player)
				else:
					print 'Bad shuffle statement. Try "shuffle" to shuffle your deck.'
					return False
			elif main == 'return':
				if len(msg_parsed) == 2:
					self.return_card( msg_parsed[1], player )
				else:
					print 'Bad return statement. Try "return s5" to return the fifth spell to your hand.'
					return False
			elif main == 'flip':
				if len(msg_parsed) == 3:
					self.flip( msg_parsed[1], msg_parsed[2], player )
				else:
					print 'Bad flip statement. Try "flip m2 0" to change the position of the second monster into faceup attack mode.'
					return False
			elif main == 'token':
				if len(msg_parsed) == 4:
					self.token( msg_parsed[1], msg_parsed[2], msg_parsed[3], player )
				else:
					print 'Bad token statement. Try "token f1 set 1" to make your field card have one token, or "token m1 adjust -1" to remove one token from your first monster.'
					return False
			elif main == 'banish':
				if len(msg_parsed) == 2:
					self.banish( msg_parsed[1], player )
				else:
					print 'Bad banish statement. Try "banish m1" to banish the first monster.'
					return False
			elif main == 'tell':
				None
			game_util.write_html(self, player)
			return True
		else:
			print 'What?'
			return False
	
	#Removes a card from a certain area of the file, e.g. the hand, and returns it. Proper format is pull('h2', player), which removes and returns the second card in the player's hand
	#Returns None if error.
	def pull( self, code, player ):
		area = code[0]
		num_str = code[1:]
		num = int(num_str)
		#Error if number negative or zero
		if num <= 0:
			print 'Bad slot in pull: {}'.format(num)
			return None
		if area in ['h', 'd', 'm', 's', 'g', 'f', 'b']:
			#Remove card from hand
			if area == 'h':
				hand = self.get_hand(player)
				if num > len(hand):
					print 'Bad slot on hand pull: {}'.format( num )
					return None
				else:
					return_card = hand.pop(num - 1)
					self.set_hand( hand, player )
					return return_card
			#Remove card from deck
			elif area == 'd':
				deck = self.get_deck(player)
				if num > len(deck):
					print 'Bad slot on deck pull: {}'.format( num )
					return None
				else:
					return_card = deck.pop(num-1)
					self.set_deck( deck, player )
					return return_card
			#Remove card from monster field
			elif area == 'm':
				if num > 5:
					print 'Bad slot on monster pull: {}'.format( num )
					return None
				else:
					monsters = self.get_monsters(player)
					return_card = monsters[num-1]
					monsters[num-1] = ''
					self.set_monsters( monsters, player )
					return return_card
			#Remove card from spell field
			elif area == 's':
				if num > 5:
					print 'Bad slot on spell pull: {}'.format( num )
					return None
				else:
					spells = self.get_spells(player)
					return_card = spells[num-1]
					spells[num-1] = ''
					self.set_spells( spells, player )
					return return_card
			#Remove card from graveyard
			elif area == 'g':
				grave = self.get_graveyard(player)
				if num > len(grave):
					print 'Bad slot on graveyard pull: {}'.format( num )
					return None
				else:
					return_card = grave.pop(num-1)
					self.set_graveyard( grave, player )
					return return_card
			#Remove card from field card area
			elif area == 'f':
				field = self.get_field(player)
				return_card = field.pop()
				self.set_field(field, player)
				return return_card
			#Remove card from banished zone
			elif area == 'b':
				banished = self.get_banished(player)
				if num > len(banished):
					print 'Bad slot on banished pull: {}'.format( num )
					return None
				else:
					return_card = banished.pop(num-1)
					self.set_banished( banished, player )
					return return_card
		else:
			print 'Bad area on pull: {}'.format( area )
	
	#Puts a card into an area, whose implementation varies on the area
	#Returns None if there is an error, such as bad code or player
	def put( self, card, code, player, special=[] ):
		area = code[0]
		num_str = code[1:]
		num = int(num_str)
		#Error if number negative or zero
		if num <= 0:
			print 'Number zero or less in put method.'
			return None
		if area in ['h', 'd', 'g', 'm', 's', 'f', 'b']:
			if area == 'h':
				hand = self.get_hand(player)
				if num <= len(hand)+1:
					lside = hand[:num-1]
					lside.append(card)
					rside = hand[num-1:]
					lside.extend(rside)
				
					self.set_hand( lside, player )
				else:
					print 'Bad number in hand put: {}'.format( num )
					return None
			elif area == 'd':
				deck = self.get_deck(player)
				if num <= len(deck)+1:
					lside = deck[:num-1]
					lside.append(card)
					rside = deck[num-1:]
					lside.extend(rside)
				
					self.set_deck( lside, player )
			elif area == 'g':
				grave = self.get_graveyard(player)
				if num <= len(grave)+1:
					lside = grave[:num-1]
					lside.append(card)
					rside = grave[num-1:]
					lside.extend(rside)
				
					self.set_graveyard( lside, player )
			elif area == 'm':
				if num > 5:
					print 'Bad into slot on monster put: {}'.format( num )
					return None
				if special[0] not in ['0', '1', '2', '3']:
					print 'Bad special on monster put.'
					return None
				monsters = self.get_monsters(player)
				new_monster = card
				#See if no monster is already there
				if monsters[num-1] == '':
					for s in special:
						new_monster += ':' + s
					monsters[num-1] = new_monster
				else:
					print 'Bad into slot on monster put: {}'.format( num )
					return None
				
				self.set_monsters( monsters, player )
			elif area == 's':
				if num > 5:
					print 'Bad into slot on spell put: {}'.format( num )
					return None
				if special[0] not in ['0', '1', '2', '3']:
					print 'Bad special on spell put.'
					return None
				#See if no spell/trap is already there
				spells = self.get_spells(player)
				new_spell = card
				if spells[num-1] == '':
					for s in special:
						new_spell += ':' + s
					print 'New spell is: {}'.format(new_spell)
					spells[num-1] = new_spell
				else:
					print 'Bad into slot on spell put: {}'.format( num )
					return None
				
				self.set_spells( spells, player )
			elif area == 'f':
				if num != 1:
					print 'Bad into slot on field put: {}'.format( num )
					return None
				if special[0] not in ['0', '1', '2', '3']:
					print 'Bad special on field put.'
					return None
				#See if no field card already there
				field = self.get_field(player)
				if field == []:
					new_field = card
					for s in special:
						new_field += ':' + s
					field.append( new_field )
				else:
					print 'Already a field card in play.'
					return None
				self.set_field( field, player )
			elif area == 'b':
				banished = self.get_banished(player)
				if num <= len(banished)+1:
					lside = banished[:num-1]
					lside.append(card)
					rside = banished[num-1:]
					lside.extend(rside)
				
					self.set_banished( lside, player )
					
		else:
				print 'Bad area on put: {}'.format( area )