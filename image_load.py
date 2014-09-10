import os
import sys
import urllib

if( len(sys.argv) < 2 ):
	print 'Provide the deck name.'
	sys.exit(0)

base = 'http://static.api5.studiobebop.net/ygo_data/card_images/'
#See if img dir exists, if not then create it
if 'img' not in os.listdir('.'):
	os.mkdir( 'img' )

#Go through all cards in deck and download images, put them in img
with open('deck\\' + sys.argv[1]) as file:
	for line in file:
		replaced = line.replace('\n', '').replace( ' ', '_' ).replace('-','_')
		url = base + replaced + '.jpg'
		print 'Looking at url ', url
		urllib.urlretrieve( url, 'img\\' + replaced + '.png'  )