# This is the file for your basic Issues.
# Use V S Code ( no problem if other editor)
#
# Issue 1: 
# Just create a Window in Python of any size (say 800 by 600 pixels)
# So this is total black screen.
# 
# Note : While referring to any file use 'copy relative path' ,Path relative to main repo.
# ex. 'Sprites\Sprites_Player\Char_003.png'
# In python \m is taken as escape sequence 
# Hence any path should be like Sprites/Sprites_Player   and not like Sprites\Sprites_Player.
# Hence after copying relative path , just change \ to / 
#  
#  Use the tiles in Sprites/Sprites_Environment and create the map.
# (Using Single tile , will give a boring map ) 
# (Use multiple tiles ,so that beautiful map is created )
# 
# Issue 2:
# Now , we will create a Character Sprite and Animate it .
# Begin by drawing a rectangle on the screen , say 64 by 64 size.
# This will be our main character . Give it 8-directional motion .
# Learn from the player.py and main.py code .
#
# Issue 3: (Read Explaination.txt)
# Now ,Lets animate using sprite in  "Sprites\Sprites_Player\Char_003.png"
# The top-left of any image is (0,0) in cordinates
# The bottom-right of any image is (width,height) in cordinates
#   The image has 16 photos of same character in 4X4 grid manner .
# Check properties of Char_003.png to know its size , it is 288 X 288 pixel
# So , the character is 288/4 = 72 pixel in size .
# Hence if we were to access Top-left photo ,  (x,y, width, height) will be (0,0, 72,72 )
# Photo in top row and 2nd Column will be (72 , 0 , 72, 72 )
# Photo in 4th row and 3rd Column will be ((4-1)*72, (3-1)*72 , 72,72 ) i.e (216 , 144, 72,72 )
# So , we can access any photo :
# (x,y) = ( (column-1)*72 , (row-1)*72
#
# We will use 2 for-loops to access the sprites. Observe the code in player.py 
# write similar code and properly access the spritesheet for the Player up-down left-right movement 
# Notice that player moves diagonally but still left or right animation is played .(AND IT FEELS okay !)
# 
# Issue 4:
# For time when Player is not moving/ Idle , access 'Sprites/Sprites_Player/Char_003_Idle.png' ,
# and Just use its first row , where Player is facing the screen 
# Hurray ! You have learned animating a character using Spritesheet . 
#
# Ta da ! This Sums up all 4 issues .