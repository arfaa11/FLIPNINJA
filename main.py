"""
AUTHOR: ARFAA MUMTAZ
PROJECT: CMPT 230 GAME
DESCRIPTION: A GAME REVOLVING A NINJA THAT CAN FLIP HIS GRAVITY AND HAS OT NAVIGATE THROUGH OBSTACLES
             IN A JOURNEY TOWARDS SELF-IMPROVEMENT BECAUSE HE IS ALWAYS TRYING TO DO BETTER THAN HE DID
             LAST TIME.
"""

# Import statements
import pygame
import sys
import random
import math
import json
import os

from Game import *

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    game = Game()
    game.run()