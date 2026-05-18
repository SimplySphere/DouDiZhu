import random 
import re
import pygame
import time
import sys
pygame.init()
screen = pygame.display.set_mode((960,648))
pygame.display.set_caption('Play Dou Di Zhu')
pygame.font.init()
font1 = pygame.font.SysFont('San Francisco', 40)
font2 = pygame.font.SysFont('San Francisco', 35)
font3 = pygame.font.SysFont('San Francisco', 24)
white = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 128)
X = 960
Y = 648
display_surface = pygame.display.set_mode((X, Y))
def refresh():
    bg = pygame.image.load("poker_table.png")
    screen.blit(bg, (-240, -96))
    pygame.display.flip()
refresh()
deck = [
        'AH','2H','3H','4H','5H','6H','7H','8H','9H','10H','JH','QH','KH',
        'AC','2C','3C','4C','5C','6C','7C','8C','9C','10C','JC','QC','KC',
        'AD','2D','3D','4D','5D','6D','7D','8D','9D','10D','JD','QD','KD',
        'AS','2S','3S','4S','5S','6S','7S','8S','9S','10S','JS','QS','KS',
        'JokerB','JokerR'
        ]
random.shuffle(deck)
def get_input():
    clock = pygame.time.Clock()
    text = ""
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:
                    return text
                elif event.key == pygame.K_BACKSPACE:
                    if text != "":
                        text = text[:-1]
                else:
                    text += event.unicode
        bg = pygame.image.load("poker_table.png")
        screen.blit(bg, (-240, -96))
        time.sleep(0.01)
        display = font2.render(text, True, (255, 255, 255))
        screen.blit(display, (480-(len(text)/2*14), 510))
        pygame.display.update(pygame.Rect(0, 510, 960, 545))
def print_deck(deck):
    if len(deck) % 2 == 0:
        start = 98 + (20-len(deck))*18
    else:
        start = 91 + (20-len(deck)-1)*18 + 9
    for i in range(len(deck)):
        card = pygame.transform.scale(pygame.image.load((deck[i]+".png")), (96,96))
        screen.blit(card, (start+i*36, 400))
        time.sleep(0.07)
        pygame.display.flip()
def value(card):
    if len(card) == 2:
        if card[0] == "2": return 15
        elif card[0].isdigit(): return int(card[0])
        elif card[0] == "J": return 11
        elif card[0] == "Q": return 12
        elif card[0] == "K": return 13
        else: return 14
    elif len(card) == 3: return 10
    else:
        if card[-1] == "B": return 16
        else: return 17
def singe_value(card):
    if len(card[0]) == 1:
        if card == "2": return 15
        elif card.isdigit(): return int(card)
        elif card == "J": return 11
        elif card == "Q": return 12
        elif card == "K": return 13
        else: return 14
    elif card[0] == "10": return 10
def sort(deck):
    temp = []
    for i in deck:
        temp.append(i)
        for j in range(len(temp)-1):
            if value(temp[-j-1]) < value(temp[-j-2]):
                var = temp[-j-2]
                temp[-j-2] = temp[-j-1]
                temp[-j-1] = var
    return temp
def single_consecutive(deck, num=0):
    if num == 3:
        const = True
        deck = sort(deck)
        for i in range(len(deck)-1):
            if singe_value(deck[i])+1 != singe_value(deck[i+1]):
                const = False
                break
        return const
    const = True
    deck = sort(deck)
    for i in range(len(deck)-1):
        if value(deck[i])+1 != value(deck[i+1]):
            const = False
            break
    return const
def double_consecutive(deck):
    const = True
    deck = sort(deck)
    for i in range(round(len(deck)/2)):
        if value(deck[i*2]) != value(deck[i*2+1]) or value(deck[i])+1 != value(deck[i+2]):
            const = False
            break
    return const
def check_triple(deck):
    deck = sort(deck)
    triples = []
    temp = deck
    for i in deck:
        if i[:-1] in ['A','2','3','4','5','6','7','8','9','10','J','Q','K'] and len(re.findall(i[:-1], "".join(deck))) == 3:
            if i[:-1] not in triples:
                triples.append(i[:-1])
    if single_consecutive(sort(triples), 3) == True:
        if len(triples)*3 == len(deck): return "SOT"
        elif len(triples)*4 == len(deck): return "SOT1"
        elif len(triples)*5 == len(deck):
            deck = []
            for i in temp:
                deck.append(i[:-1])
            for i in triples:
                for j in range(3):
                    deck.pop(deck.index(i))
            if len(deck)%2 == 0:
                for i in range(round(len(deck)/2)):
                    if deck[i*2] != deck[i*2+1]:
                        return None
            return "SOT2"
        else: return None
def configure(play):
    play = sort(play)
    print(play)
    if len(play) == 1: return "S"
    elif len(play) == 2 and ((play[0] == "JokerB" and play[1] == "JokerR") or (play[0] == "JokerR" and play[1] == "JokerB")): return "JJ"
    elif len(play) == 2 and play[0][0] == play[1][0]: return "D"
    elif len(play) == 3 and play[0][0] == play[1][0] == play[2][0]: return "T"
    elif len(play) == 4 and play[0][0] == play[1][0] == play[2][0] == play[3][0]: return "Q"
    elif len(play) == 4 and ((play[0][0] == play[1][0] == play[2][0] or play[1][0] == play[2][0] == play[3][0])): return "T1"
    elif len(play) == 5 and (play[0][0] == play[1][0] == play[2][0] == play[3][0] or play[1][0] == play[2][0] == play[3][0] == play[4][0]): return "Q1"
    elif len(play) == 5 and ((play[0][0] == play[1][0] == play[2][0] and play[3][0] == play[4][0]) or (play[2][0] == play[3][0] == play[4][0] and play[0][0] == play[1][0])): return "T2"
    elif len(play) == 6 and (play[0][0] == play[1][0] == play[2][0] == play[3][0] or play[1][0] == play[2][0] == play[3][0] == play[4][0] or play[2][0] == play[3][0] == play[4][0] == play[5][0]): return "Q2"
    elif len(play) == 7 and (play[0][0] == play[1][0] == play[2][0] == play[3][0] or play[1][0] == play[2][0] == play[3][0] == play[4][0] or play[2][0] == play[3][0] == play[4][0] == play[5][0] or play[3][0] == play[4][0] == play[5][0] == play[6][0]): return "Q3"
    else: 
        if len(play) >= 5 and single_consecutive(play) == True: return "SOS"
        elif len(play) >= 6 and double_consecutive(play) == True: return "SOD"
        else: return check_triple(play)
def play_value(play):
    play = sort(play)
    form = configure(play)
    if form == None: return 0
    elif form == "S": return value("".join(play))
    elif form == "D": return value(play[0])
    elif form == "T": return value(play[0])
    elif form == "JJ": return 100000
    elif form == "Q": return value(play[0])*100
    elif form == "T1": return value(play[1])
    elif form == "T2": return value(play[2])
    elif form == "Q1": return value(play[1])
    elif form == "Q2": return value(play[2])
    elif form == "Q3": return value(play[3])
    elif form == "SOS": return value(play[0])
    elif form == "SOD": return value(play[0])
    elif form == "SOT1" or form == "SOT" or form == "SOT2":
        triples = []
        for i in play:
            if i[:-1] in ['A','2','3','4','5','6','7','8','9','10','J','Q','K'] and len(re.findall(i[:-1], "".join(play))) == 3:
                if i[:-1] not in triples: triples.append(i[:-1])
        return sort(triples[0])
bait = [deck.pop(0) for i in range(3)]
bait = sort(bait)
player1 = [deck.pop(0) for i in range(17)]
player2 = [deck.pop(0) for i in range(17)]
player3 = [deck.pop(0) for i in range(17)]
player1 = sort(player1)
player2 = sort(player2)
player3 = sort(player3)
highest = [0, random.randint(1,3)]
print("\nAuction:",(", ".join(bait)))
print(f"Player {highest[1]} bids first!")
player = highest[1]-1
display = highest[1]
text = font3.render(f'Player {highest[1]} bids first!', True, (255, 255, 255))
screen.blit(text, (408, 179))
pygame.display.flip()
for i in range(3):
    print(f"Highest bid: {highest[0]}")
    while True:
        text = font1.render("Auction: ", True, (255, 255, 255))
        screen.blit(text, (421, 119))
        for i in range(3):
            card = pygame.transform.scale(pygame.image.load((bait[i] + ".png")), (96, 96))
            screen.blit(card, (354 + i * 80, 220))
            pygame.display.flip()
        text = font3.render(f"Highest bid: {highest[0]}", True, (255, 255, 255))
        screen.blit(text, (421, 345))
        text = font3.render(f"Player {display}'s turn!", True, (255, 255, 255))
        screen.blit(text, (416, 371))
        pygame.display.flip()
        if display == 1:
            print_deck(player1)
            print(", ".join(player1))
        elif display == 2:
            print_deck(player2)
            print(", ".join(player2))
        else:
            print_deck(player3)
            print(", ".join(player3))
        bid = get_input()
        if bid in ['0','5','10','15']:
            player += 1
            if player != 3: player %= 3
            display += 1
            if display > 3: display %= 3
            if int(bid) > highest[0]:
                highest[0] = int(bid)
                highest[1] = player
                break
            elif int(bid) <= highest[0]: break
    refresh()
    if highest[0] == 15: break
if highest[0] == 0: highest[0] = 5
for i in bait:
    if highest[1] == 1: player1.append(i)
    elif highest[1] == 2: player2.append(i)
    else: player3.append(i)
player1 = sort(player1)
player2 = sort(player2)
player3 = sort(player3)
if "3H" in player1: turn = 1
elif "3H" in player2: turn = 2
else: turn = 3
print(f"\nPlayer {turn} goes first!")
text = font3.render(f"Player {turn} goes first!", True, (255, 255, 255))
screen.blit(text, (414, 376))
pygame.display.flip()
table = ""
form = None
count = 0
while True:
    #for i in range(2):
    #    for j in range(3):
    #        card = pygame.transform.scale(pygame.image.load((".png")), (96, 96))
    print(f"Landlord: Player {highest[1]}")
    text = font3.render(f"Landlord: Player {highest[1]}", True, (255, 255, 255))
    screen.blit(text, (410, 171))
    print(f"On Table: {table}")
    text = font1.render("On Table:", True, (255, 255, 255))
    screen.blit(text, (415, 119))
    if table != "":
        if len(table.split(", ")) % 2 == 0: start = 98 + (20 - len(table.split(", "))) * 18
        else: start = 91 + (20 - len(table.split(", ")) - 1) * 18 + 9
        for i in range(len(table.split(', '))):
            card = pygame.transform.scale(pygame.image.load(((table.split(', '))[i] + ".png")), (96, 96))
            screen.blit(card, (start + i * 36, 210))
            time.sleep(0.07)
            pygame.display.flip()
    if turn == 1:
        print_deck(player1)
        print(", ".join(player1))
    elif turn == 2:
        print_deck(player2)
        print(", ".join(player2))
    else:
        print_deck(player3)
        print(", ".join(player3))
    while True:
        play = get_input().strip().split(", ")
        print(configure(play))
        if play != [""]:
            count = 0
            if configure(play) == None: continue
            elif configure(play) == "JJ": pass
            elif configure(play) == "Q":
                if form == "JJ" or play_value(play) <= play_value(table.split(", ")): continue
            else:
                if (play_value(play) <= play_value(table.split(", ")) or configure(play) != form) or len(play) != len(table.split(", ")): continue
            form = configure(play)
            if turn == 1 and play == [i for i in play if i in player1]:
                table = ", ".join([player1.pop(player1.index(i)) for i in play])
                break
            elif turn == 2 and play == [i for i in play if i in player2]:
                table = ", ".join([player2.pop(player2.index(i)) for i in play])
                break
            elif turn == 3 and play == [i for i in play if i in player3]: 
                table = ", ".join([player3.pop(player3.index(i)) for i in play])
                break
            else: print("Try again.")
        else: 
            count += 1
            if count == 2:
                form = None
                table = ""
                count = 0
            break
    if len(player1) == 0 or len(player2) == 0 or len(player3) == 0: break
    turn %= 3
    turn += 1
    refresh()
    print(f"\nPlayer {turn}'s turn!")
    text = font3.render(f"Player {turn}'s turn!", True, (255, 255, 255))
    screen.blit(text, (416, 376))
    pygame.display.flip()
print(f"\nPlayer {player} wins!")
time.sleep(10)
refresh()
pygame.quit()