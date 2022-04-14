from PIL import Image
im = Image.open('pieces.png')
chesses = ['king', 'guard', 'knight', 'bishop', 'rock', 'cannon', 'pawn']
players = ['Red', 'Black']

piece_size = 300
for i in range(len(chesses)):
	for j in range(len(players)):
		filename = players[j] + '_' + chesses[i] + '.png'
		left = i * piece_size
		upper = j * piece_size
		right = left + piece_size
		lower = upper + piece_size
		im2 = im.crop((left, upper, right, lower))
		if j == 1:
			im2 = im2.rotate(180)
		im2.save(filename)