import random
import time
import os
import tkinter as tk
import PIL.Image
import PIL.ImageTk

def deckCoor(cardVal,cardSuit):
    value = cardVal
    suit = cardSuit
    xstart = 0
    xend = 0
    ystart = 0
    yend = 0

    #find suit row
    if suit == "Clubs":
        yMult = 1
    elif suit == "Spades":
        yMult = 2
    elif suit == "Hearts":
        yMult = 3
    elif suit == "Diamonds":
        yMult = 4

    #find value column
    if value == 14:
        xMult = 1
    else:
        xMult = value

    #calculate coordinates
    xstart = (xMult - 1)*73
    xend = xMult*73
    ystart = (yMult - 1)*98
    yend = yMult*98

    return (xstart,ystart,xend,yend)

class Card(object):
    def __init__(self, suit, val):
        self.suit = suit
        self.value = val

    def show(self):
        if self.value < 11:
            print("{} of {}".format(self.value, self.suit))
        if self.value == 11:
            print("Jack of {}".format(self.suit))
        if self.value == 12:
            print("Queen of {}".format(self.suit))
        if self.value == 13:
            print("King of {}".format(self.suit))
        if self.value == 14:
            print("Ace of {}".format(self.suit))

    def showValue(self):
        if self.value == 11:
            return 10
        if self.value == 12:
            return 10
        if self.value == 13:
            return 10
        else:
            return self.value

class Deck(object):
    def __init__(self):
        self.cards = []
        self.build()

    def build(self):
        for s in ["Spades", "Clubs", "Diamonds", "Hearts"]:
            for v in range(2, 15):
                self.cards.append(Card(s, v))

    def show(self):
        for c in self.cards:
            c.show()

    def shuffle(self):
        for i in range(len(self.cards)-1, 0, -1):
            r = random.randint(0, i)
            self.cards[i], self.cards[r] = self.cards[r], self.cards[i]

    def newDeck(self):
        self.cards.clear()
        self.build()

    def drawCard(self):
        return self.cards.pop()

class Player(object):
    def __init__(self, name, isdealer):
        self.name = name
        self.dealer = isdealer
        self.hand = []
        self.total = 0
        self.totalsoft = 0
        self.money = 1000
        self.bet = 0

    def draw(self, deck):
        self.hand.append(deck.drawCard())

    def betPlace(self,betPlaced):
        self.bet = betPlaced

    def calcTotal(self):
        self.total = 0
        self.totalsoft = 0

        ##check if dealer
        if self.dealer == 1:
            for card in self.hand:
                if card != self.hand[0]:
                    if card.showValue() == 14:
                        if self.total > 10:
                            val = 1
                            valsoft = 1
                        else:
                            val = 11
                            valsoft = 1
                    else:
                        val = card.showValue()
                        valsoft = card.showValue()

                    self.total += val
                    self.totalsoft += valsoft

        ##if player
        else:
            for card in self.hand:
                if card.showValue() == 14:
                    if self.total > 10:
                        val = 1
                        valsoft = 1
                    else:
                        val = 11
                        valsoft = 1
                else:
                    val = card.showValue()
                    valsoft = card.showValue()

                self.total += val
                self.totalsoft += valsoft

    def calcWinnings(self,result):
        #0 for loss, 1 for win, 2 for blackjack
        if result == 0:
            self.money -= int(self.bet)
        if result == 1:
            self.money += int(self.bet)
        if result == 2:
            self.money += int(int(self.bet)*(3/2))
        self.bet = 0


    def check21(self):
        self.total = 0
        self.totalsoft = 0
        for card in self.hand:
            if card.showValue() == 14:
                if self.total > 10:
                    val = 1
                    valsoft = 1
                else:
                    val = 11
                    valsoft = 1
            else:
                val = card.showValue()
                valsoft = card.showValue()

            self.total += val
            self.totalsoft += valsoft

        if self.total == 21:
            return 1
        else:
            return 0

    def checkBust(self):
        self.calcTotal()
        if self.total > 21:
            if self.totalsoft > 21:
                return 1
        else:
            return 0

    def doubleDown(self):
        self.bet = self.bet*2

    def getTotal(self):
        self.calcTotal()
        if self.totalsoft != self.total:
            if self.total < 22:
                return self.total
            else:
                return self.totalsoft
        else:
            return self.total

    def showHand(self):
        ##show player totals
        self.calcTotal()
        if self.totalsoft != self.total:
            if self.total > 21:
                print("{} shows {}".format(self.name, self.totalsoft))
            else:
                print("{} shows {} (soft {})".format(self.name, self.total, self.totalsoft))
        else:
            print("{} shows {}".format(self.name, self.total))

        #show cards
        for card in self.hand:
            card.show()

        #display money and current bet
        if self.name != 'dealer':
            print('Money {}. Current bet: {}'.format(self.money, self.bet))

    def discard(self):
        self.hand.clear()

from tkinter import *
class Gui():
    def __init__(self,root):
        self.root=root
        self.entry = tk.Entry(root)
        self.canvas=tk.Canvas(root, width=800, height=600)
        self.canvas.configure(background="green")
        self.canvas.pack()
        self.cardCount = 0
        self.cardImages = {}
        self.playerhand = 0
        self.dealerhand = 0

        #booleans
        self.hit = False
        self.stand = False
        self.double = False
        self.placeBet = False
        self.end = False
        self.next = False

        #text user totals
        self.dealerTotal = self.canvas.create_text(0,0,text="")
        self.playerTotal = self.canvas.create_text(0,0,text="")

        #text game status
        self.gameStatus = self.canvas.create_text(100, 550, text="")

        #text money and current bet
        self.playerMoney = self.canvas.create_text(600, 100, text="")

        #define button controls
        self.betBut = Button(self.root, text = "Bet", command=lambda: self.betAction())
        self.betBut.configure(width = 10, activebackground = "blue", relief = FLAT)
        self.betBut.Window = self.canvas.create_window(600,150, window=self.betBut)

        self.doubleBut = Button(self.root,text="Double Down", state=DISABLED,command=lambda: self.doubleAction())
        self.doubleBut.configure(width=10, activebackground="blue", relief=FLAT)
        self.doubleBut.Window = self.canvas.create_window(600, 200, window=self.doubleBut)

        self.hitBut = Button(self.root, text="Hit",state=DISABLED, command=lambda: self.hitAction())
        self.hitBut.configure(width=10, activebackground="blue", relief=FLAT)
        self.hitBut.Window = self.canvas.create_window(600, 250, window=self.hitBut)

        self.standBut = Button(self.root, text="Stand",state=DISABLED, command=lambda: self.standAction())
        self.standBut.configure(width=10, activebackground="blue", relief=FLAT)
        self.standBut.Window = self.canvas.create_window(600, 300, window=self.standBut)

        self.nextBut = Button(self.root, text="Next Hand", state=DISABLED, command=lambda: self.nextAction())
        self.nextBut.configure(width=10, activebackground="blue", relief=FLAT)
        self.nextBut.Window = self.canvas.create_window(600, 350, window=self.nextBut)

        #define bet textfield
        self.betEntry = Entry(self.canvas)
        self.canvas.create_window(725,150,window=self.betEntry)

        #create deck img reference
        self.deckImg = PIL.Image.open("deck.png")

        #create faceDown img
        self.back = PIL.Image.open("back.png")
        self.faceDown = PIL.ImageTk.PhotoImage(self.back)

    def betAction(self):
        if self.betEntry.get().isdigit():
            self.placeBet = True
        else:
            print("Place bet...")

    def getBet(self,checkMax):
        # set button configs
        self.betBut.config(state="normal")
        self.doubleBut.config(state="disabled")
        self.hitBut.config(state="disabled")
        self.standBut.config(state="disabled")
        self.nextBut.config(state="disabled")

        if self.placeBet == True:
            if int(self.betEntry.get()) <= checkMax:
                return self.betEntry.get()
                self.placeBet = False
            else:
                # clear entry
                self.betEntry.delete(0, END)
                self.placeBet = False
                return 0
        else:
            return 0

    def updateMoney(self,money,bet):
        if bet == 0:
            self.canvas.itemconfig(self.playerMoney, text="Money: {}".format(money))
        else:
            self.canvas.itemconfig(self.playerMoney, text="Money: {}   Bet: {}".format(money,bet))

    def hitAction(self):
        self.hit = True

    def standAction(self):
        self.stand = True

    def doubleAction(self):
        self.double = True

    def nextAction(self):
        if self.end == True:
            self.next = True

    def begRound(self):
        self.hit = False
        self.stand = False
        self.double = False
        self.next = False
        self.end = False

        #set button configs
        self.betBut.config(state="disabled")
        self.doubleBut.config(state="normal")
        self.hitBut.config(state="normal")
        self.standBut.config(state="normal")
        self.nextBut.config(state="disabled")

    def endRound(self):
        self.end = True

        # set button configs
        self.betBut.config(state="disabled")
        self.doubleBut.config(state="disabled")
        self.hitBut.config(state="disabled")
        self.standBut.config(state="disabled")
        self.nextBut.config(state="normal")

        #clear entry
        self.betEntry.delete(0,END)

    def placeCard(self, playerName, cardVal, cardSuit):
        self.name = playerName

        #crop card from deck image
        self.cropped = self.deckImg.crop(deckCoor(cardVal, cardSuit))
        self.cardImages[self.cardCount] = PIL.ImageTk.PhotoImage(self.cropped)

        #place card on canvas based on player location
        if self.name == "dealer":
            self.xCoor = 50
            self.yCoor = 100
            if self.cardCount == 0:
                self.faceDownImg = self.canvas.create_image(self.xCoor + (self.dealerhand * 80), self.yCoor,
                                         image=self.faceDown)
            else:
                self.canvas.create_image(self.xCoor + (self.dealerhand * 80), self.yCoor,
                                     image=self.cardImages[self.cardCount])
        else:
            self.xCoor = 50
            self.yCoor = 300
            self.canvas.create_image(self.xCoor + (self.playerhand * 80), self.yCoor,
                                     image=self.cardImages[self.cardCount])

        #increment cardCount
        if self.name == "dealer":
            self.dealerhand += 1
        else:
            self.playerhand += 1
        self.cardCount += 1

    def revealDealer(self,total):
        self.canvas.itemconfig(self.faceDownImg, image='')
        self.xCoor = 50
        self.yCoor = 100
        self.canvas.create_image(self.xCoor, self.yCoor,
                                 image=self.cardImages[0])
        self.placeHandtotal("dealer",total)

    def placeNametag(self,playerName):
        self.name = playerName
        # set player location
        if self.name == "dealer":
            self.xCoor = 50
            self.yCoor = 100
        else:
            self.xCoor = 50
            self.yCoor = 300

        if playerName == "dealer":
            self.canvas.create_text(self.xCoor,self.yCoor-80,font="Times 20 italic bold",
                                    text="Dealer")
            self.canvas.move(self.dealerTotal,self.xCoor+100,self.yCoor-80)
        else:
            self.canvas.create_text(self.xCoor, self.yCoor-80,fill="black" ,font="Times 20 italic bold",
                                    text=playerName)
            self.canvas.move(self.playerTotal, self.xCoor + 100, self.yCoor - 80)

    def placeHandtotal(self,playerName,total):
        self.name = playerName
        # set player location
        if self.name == "dealer":
            self.canvas.itemconfig(self.dealerTotal,
                                   text="Dealer shows {}".format(total))
        else:
            self.name = playerName
            self.canvas.itemconfig(self.playerTotal,
                                   text="{} shows {}".format(self.name, total))


    def doubleDown(self,check):
        if check == False:
            self.doubleBut.config(state="disabled")
        else:
            self.doubleBut.config(state="normal")

    def updateStatus(self,condition):
        #0 for loss, 1 for bust, 2 for dealer blackjack
        #3 for win, 4 for dealer bust, 5 for player blackjack
        if condition == 0:
            self.canvas.itemconfig(self.gameStatus, text="Player Loses!", fill="red")
        elif condition == 1:
            self.canvas.itemconfig(self.gameStatus, text="Bust! Player Loses!", fill="red")
        elif condition == 2:
            self.canvas.itemconfig(self.gameStatus, text="Dealer has Blackjack! Player Loses!", fill="red")
        elif condition == 3:
            self.canvas.itemconfig(self.gameStatus, text="Player Wins!")
        elif condition == 4:
            self.canvas.itemconfig(self.gameStatus, text="Dealer busts! Player Wins!")
        elif condition == 5:
            self.canvas.itemconfig(self.gameStatus, text="Blackjack! Player Wins!")
        elif condition == 6:
            self.canvas.itemconfig(self.gameStatus, text="Push!")
        else:
            self.canvas.itemconfig(self.gameStatus, text="", fill="black")

    def cleanCards(self):
        self.cardImages.clear()
        self.cardCount = 0
        self.dealerhand = 0
        self.playerhand = 0

        #clear gamestatus
        self.canvas.itemconfig(self.gameStatus, text="", fill="black")

class gameController():
    def __init__(self,player,dealer,gameGui):
        self.dealer = dealer
        self.player = player
        self.gameGui = gameGui

        # initialize deck
        self.deck = Deck()

        #special cases
        self.doubledownOption = False
        self.gameGui.doubleDown(self.doubledownOption)

        #turn booleans
        self.playerTurn = True
        self.dealer_bust = False
        self.player_bust = False
        self.dealer_blackjack = False
        self.player_blackjack = False
        self.dealer_reveal = False
        # self.doubledown = False
        # self.hit = False
        # self.stand = False

        #money variables
        self.winnings = 0

        #place nametags
        self.gameGui.placeNametag(self.dealer.name)
        self.gameGui.placeNametag(self.player.name)

    def addCard(self,player):
        self.cardplayer = player

        #call player add card
        self.cardplayer.draw(self.deck)

        #place card
        self.gameGui.placeCard(self.cardplayer.name, self.cardplayer.hand[len(self.cardplayer.hand)-1].value, self.cardplayer.hand[len(self.cardplayer.hand)-1].suit)
        self.gameGui.placeHandtotal(self.cardplayer.name, self.cardplayer.getTotal())

    def calcWinning(self):
        #reveal hands
        # self.dealer.showHand()
        # self.player.showHand()

        if self.dealer_reveal == False:
            gameGui.revealDealer(self.dealer.getTotal())
            self.dealer_reveal = True


        # def updateStatus(self, condition):

        # 0 for loss, 1 for bust, 2 for dealer blackjack
        # 3 for win, 4 for dealer bust, 5 for player blackjack, 6 for push

        #player.calcWinnings: 0 for loss, 1 for win, 2 for backjack, else for push

        ##calculate winnings
        # player blackjack
        if self.player_blackjack == True:
            # push
            if self.dealer_blackjack == True:
                self.gameGui.updateStatus(6)
                self.player.calcWinnings(3)
            else:
                self.gameGui.updateStatus(5)
                self.player.calcWinnings(2)
        # dealer blackjack
        elif self.dealer_blackjack == True:
            self.gameGui.updateStatus(2)
            self.player.calcWinnings(0)

        # dealer bust
        elif self.dealer_bust == True:
            self.gameGui.updateStatus(4)
            self.player.calcWinnings(1)

        #player bust
        elif self.player_bust == True:
            self.gameGui.updateStatus(1)
            self.player.calcWinnings(0)

        # player win
        elif self.player.getTotal() > self.dealer.getTotal():
            self.gameGui.updateStatus(3)
            self.player.calcWinnings(1)

        # push
        elif self.player.getTotal() == self.dealer.getTotal():
            self.gameGui.updateStatus(6)
            self.player.calcWinnings(3)

        # dealer win
        elif self.player.getTotal() < self.dealer.getTotal():
            self.gameGui.updateStatus(0)
            self.player.calcWinnings(0)

    def checkbust(self):
        if self.dealer.checkBust() == 1:
            self.dealer_bust == True
        if self.player.checkBust() == 1:
            self.player_bust = True
            return 1
        else:
            return 0

    def checkblackjack(self):
        if self.player.check21() == 1:
            self.player_blackjack = True
        if self.dealer.check21() == 1:
            self.dealer_blackjack = True

    def dealerTurn(self):
        self.dealer.dealer = 0

        #remove dace down img and replace with card
            #also update total on dealer
        if self.dealer_reveal == False:
            gameGui.revealDealer(self.dealer.getTotal())
            self.dealer_reveal = True
            root.update()


        #check if player bust or got blackjack
        self.checkbust()
        if self.player_bust == True:
            return 1
        if self.player_blackjack == True:
            return 1

        # check if not busted
        if self.dealer.checkBust() == 1:
            self.dealer_bust = True
            return 1
        if self.dealer.getTotal() < 17:
            time.sleep(1.5)
            self.addCard(dealer)
        else:
            return 1

    def roundStart(self):
        #set starting variables
        self.dealer_bust = False
        self.player_bust = False
        self.dealer_blackjack = False
        self.player_blackjack = False
        self.doubledownOption = True
        self.doubledown = False

        #set gui Bools
        self.gameGui.begRound()
        self.gameGui.doubleDown(self.doubledownOption)

        self.newTurn = False

        #shuffle deck
        self.deck.shuffle()

        #deal starting hand
        self.addCard(self.dealer)
        self.addCard(self.dealer)
        self.addCard(self.player)
        self.addCard(self.player)

        self.checkblackjack()

        #set double down button active
        # self.gameGui.doubleDown(True)

    def roundEnd(self):
        ##clean hands and gui
        self.player.discard()
        self.dealer.discard()

        # reinstate dealer discretion
        self.dealer.dealer = 1
        self.dealer_reveal = False

        self.deck.newDeck()

        self.gameGui.cleanCards()

        # clear totals
        self.gameGui.canvas.itemconfig(gameGui.dealerTotal,text="")
        self.gameGui.canvas.itemconfig(gameGui.playerTotal, text="")



    def gameEngine(self):
        #check if dealer or player has blackjack
        if self.player_blackjack == True:
            self.doubledownOption = False
            self.gameGui.doubleDown(self.doubledownOption)
            return 1
        if self.dealer_blackjack == True:
            self.doubledownOption = False
            self.gameGui.doubleDown(self.doubledownOption)
            return 1

        #check bust
        self.checkbust()
        if self.player_bust == True:
            return 1

        #check double down
        if self.gameGui.double == True:
            if self.doubledownOption == True:
                self.player.doubleDown()
                self.gameGui.updateMoney(self.player.money,self.player.bet)
                self.doubledownOption = False
                self.gameGui.doubleDown(self.doubledownOption)
                self.addCard(self.player)
                self.revealDealer = True
                return 1

        #check hit
        if self.gameGui.hit == True:
            self.doubledownOption = False
            self.gameGui.doubleDown(self.doubledownOption)
            self.addCard(self.player)
            self.gameGui.hit = False
            self.newTurn = True

        #check stand
        if self.gameGui.stand == True:
            self.doubledownOption = False
            self.gameGui.doubleDown(self.doubledownOption)
            self.revealDealer = True
            return 1

#initialize players
dealer = Player("dealer",1)
adam = Player("Adam",0)
root = tk.Tk()
gameGui = Gui(root)
root.update()
gameControl = gameController(adam,dealer,gameGui)


while 1:
    #place bet
    gameGui.updateMoney(adam.money, 0)
    while gameGui.getBet(adam.money) == 0:
        root.update()
    adam.betPlace(int(gameGui.getBet(adam.money)))
    gameGui.updateMoney(adam.money, adam.bet)
    gameGui.placeBet = False

    #start round
    gameControl.roundStart()
    root.update()

    #run players turn
    while gameControl.gameEngine() != 1:
        root.update()

    #run dealers turn
    while gameControl.dealerTurn() != 1:
        root.update()

    #calculate winnings
    gameControl.calcWinning()
    root.update()

    #wait for new game
    gameGui.endRound()
    while gameGui.next == False:
        root.update()

    #round end
    gameControl.roundEnd()
    root.update()