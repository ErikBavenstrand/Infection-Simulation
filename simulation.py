import argparse
import sys
import time
from random import randint, random
from os import system, name

def clear(): 

    if name == 'nt': 
        _ = system('cls') 

    else: 
        _ = system('clear') 

def probability(p):
    p = float(p)
    if p > 1 or p < 0:
        raise argparse.ArgumentTypeError("must be a probability")
    return p

def positiveInt(v):
    v = int(v)
    if v < 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return v

def getArgs():
    PARSER = argparse.ArgumentParser(description="Input values for simulation")
    PARSER.add_argument('-i', "--infected", help="number of individuals infected that day",
                    action="store_true")
    PARSER.add_argument('-d', "--deceased", help="number of individuals deceased that day",
                    action="store_true")
    PARSER.add_argument("-r", "--recovered", help="number of individuals recovered that day",
                    action="store_true")
    PARSER.add_argument("-ti", "--totalinfected", help="number of infected individuals",
                    action="store_true")
    PARSER.add_argument("-ai", "--accumulatedinfected", help="accumulated number of infected individuals",
                    action="store_true")
    PARSER.add_argument("-ad", "--accumulateddeceased", help="accumulated number of deceased individuals",
                    action="store_true")
    PARSER.add_argument("-da", "--daily", help="displays daily information about the population",
                    action="store_true")
    PARSER.add_argument("-p", "--pause", help="pause program each day and wait for input to continue",
                    action="store_true")
    PARSER.add_argument('N', metavar='N', type=positiveInt,
                        help="[int] size of the population in N*N matrix")
    PARSER.add_argument('spreadProb', metavar='spreadProb', type=probability,
                        help="[probability] probability of disease spreading to neighbors each day")
    PARSER.add_argument('minInfectedDays', metavar='minInfectedDays', type=positiveInt,
                        help="[int] minimum amount of days that an indivudual is sick")
    PARSER.add_argument('maxInfectedDays', metavar='maxInfectedDays', type=positiveInt,
                        help="[int] maximum amount of days that an indivudual is sick")
    PARSER.add_argument('deathProb', metavar='deathProb', type=probability,
                        help="[probability] probability that an indivudual with the disease dies of each day")
    PARSER.add_argument('infectedNumber', metavar='infectedNumber', type=positiveInt,
                        help="[int] number of initially infected")
    PARSER.add_argument('infectedPos', metavar='infectedPos', type=positiveInt, nargs=argparse.REMAINDER,
                        help="[int] [int] space separated positions for all the infected")

    ARGS = PARSER.parse_args()
    checkArgs(ARGS)
    return ARGS
    
def checkArgs(args):
    if args.minInfectedDays > args.maxInfectedDays:
        raise argparse.ArgumentTypeError("minInfectedDays can not be larger than maxInfectedDays")
    try:
        for i in range(args.infectedNumber):
            if args.infectedPos[i*2] > args.N - 1 or args.infectedPos[i*2 + 1] > args.N - 1:
                raise argparse.ArgumentTypeError("positions of infected must be valid positions in N*N matrix")
        if len(args.infectedPos) != args.infectedNumber * 2:
            raise IndexError
    except IndexError:
        raise argparse.ArgumentTypeError("number of infected must match the amount of position pairs")

class bcolors:
    BLACK  = '\33[30m'
    REDBG = '\033[101m'
    YELLOWBG = '\033[103m'
    BLUEBG = '\033[104m'
    GREENBG = '\033[102m'
    ENDC = '\033[0m'

class Individual:
    def __init__(self, x, y):
        self.infected = False
        self.alive = True
        self.dayInfected = -1
        self.daysToRecovery = -1
        self.immune = False
        self.displayVal = 'A  '
        self.neighbors = []
        self.x = x
        self.y = y

    def __str__(self):
        if self.alive is False:
            return bcolors.REDBG + bcolors.BLACK + self.displayVal + bcolors.ENDC
        if self.infected is True:
            return bcolors.YELLOWBG + bcolors.BLACK + self.displayVal + bcolors.ENDC
        if self.immune is True:
            return bcolors.BLUEBG + bcolors.BLACK + self.displayVal + bcolors.ENDC
        if self.alive is True:
            return bcolors.GREENBG + bcolors.BLACK + self.displayVal + bcolors.ENDC
        

    def addNeighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def tryInfect(self, p, day, f, t):
        infected = []
        if self.dayInfected != day:
            for n in self.neighbors:
                if self.__roll(p) and self.infected is True and self.alive is True and n.immune is False and n.alive is True and n.infected is False:
                    n.infected = True
                    n.dayInfected = day
                    n.displayVal = 'I  '
                    n.daysToRecovery = randint(f, t)
                    infected.append([n.x, n.y])
        return infected


    def tryRecover(self):
        self.daysToRecovery -= 1
        if self.daysToRecovery == 0:
            self.infected = False
            self.dayInfected = -1
            self.immune = True
            self.displayVal = 'A* '
            return 1
        return 0
    
    def tryDie(self, p, day):
        if self.__roll(p) and self.infected is True and self.alive is True and self.dayInfected != day:
            self.alive = False
            self.displayVal = 'D  '
            self.daysToRecovery = -1
            return 1
        return 0

    def initInfect(self, f, t):
        self.infected = True
        self.displayVal = 'I  '
        self.dayInfected = -1
        self.daysToRecovery = randint(f, t)

    def __roll(self, p):
        v = random()
        if p >= v:
            return True
        return False

def printMatrix(m):
    clear()
    for row in m:
        for i in row:
            print(i, end='')
        print()
    print()

def initializeInfected(m, l, inf, f, t):
    for i in range(inf):
        m[l[i*2 + 1]][l[i*2]].initInfect(f, t)
    return m

def addNeighbors(m, n):
    for j in range(n):
        for i in range(n):
            if 0 < i < n - 1 and 0 < j < n - 1:
                m[j][i].addNeighbor(m[j-1][i-1])
                m[j][i].addNeighbor(m[j-1][i])
                m[j][i].addNeighbor(m[j-1][i+1])
                m[j][i].addNeighbor(m[j][i-1])
                m[j][i].addNeighbor(m[j][i+1])
                m[j][i].addNeighbor(m[j+1][i-1])
                m[j][i].addNeighbor(m[j+1][i])
                m[j][i].addNeighbor(m[j+1][i+1])
            elif i == 0 and j == 0:
                m[j][i].addNeighbor(m[j+1][i])
                m[j][i].addNeighbor(m[j+1][i+1])
                m[j][i].addNeighbor(m[j][i+1])
            elif i == 0 and j == n - 1:
                m[j][i].addNeighbor(m[j-1][i])
                m[j][i].addNeighbor(m[j-1][i+1])
                m[j][i].addNeighbor(m[j][i+1])
            elif i == n - 1 and j == 0:
                m[j][i].addNeighbor(m[j][i-1])
                m[j][i].addNeighbor(m[j+1][i-1])
                m[j][i].addNeighbor(m[j+1][i])
            elif i == n - 1 and j == n - 1:
                m[j][i].addNeighbor(m[j][i-1])
                m[j][i].addNeighbor(m[j-1][i-1])
                m[j][i].addNeighbor(m[j-1][i])
            elif 0 < i < n - 1 and j == 0:
                m[j][i].addNeighbor(m[j][i-1])
                m[j][i].addNeighbor(m[j+1][i-1])
                m[j][i].addNeighbor(m[j+1][i])
                m[j][i].addNeighbor(m[j+1][i+1])
                m[j][i].addNeighbor(m[j][i+1])
            elif i == 0 and 0 < j < n - 1:
                m[j][i].addNeighbor(m[j-1][i])
                m[j][i].addNeighbor(m[j-1][i+1])
                m[j][i].addNeighbor(m[j][i+1])
                m[j][i].addNeighbor(m[j+1][i+1])
                m[j][i].addNeighbor(m[j+1][i])
            elif 0 < i < n - 1 and j == n - 1:
                m[j][i].addNeighbor(m[j-1][i])
                m[j][i].addNeighbor(m[j-1][i+1])
                m[j][i].addNeighbor(m[j][i+1])
                m[j][i].addNeighbor(m[j-1][i-1])
                m[j][i].addNeighbor(m[j][i-1])
            elif i == n - 1 and 0 < j < n - 1:
                m[j][i].addNeighbor(m[j-1][i])
                m[j][i].addNeighbor(m[j-1][i-1])
                m[j][i].addNeighbor(m[j][i-1])
                m[j][i].addNeighbor(m[j+1][i-1])
                m[j][i].addNeighbor(m[j+1][i])

def printInfo(args, day, infected, deceased, recovered, totalInfected, accInfected, accDeceased):
    s = ""
    if args.infected or args.deceased or args.recovered or args.totalinfected or args.accumulatedinfected or args.accumulateddeceased:
        s += "Day " + str(day) + ": "
        if args.infected:
            s += "infected=" + str(infected) + ", "
        if args.deceased:
            s += "deceased=" + str(deceased) + ", "
        if args.recovered:
            s += "recovered=" + str(recovered) + ", "
        if args.totalinfected:
            s += "totalInfected=" + str(totalInfected) + ", "
        if args.accumulatedinfected:
            s += "accumulatedInfected=" + str(accInfected) + ", "
        if args.accumulateddeceased:
            s += "accumulatedDeceased=" + str(accDeceased)
        print(s)

def runSim(m, args):
    day = 0
    infected = []
    nextInf = []
    for i in range(args.infectedNumber):
        infected.append([args.infectedPos[i*2 + 1], args.infectedPos[i*2]])
    accDeceased = 0
    accInfected = args.infectedNumber
    if args.daily:
        printMatrix(m)
        time.sleep(0.25)
    while infected:
        newInfected = 0
        newDead = 0
        newRecovered = 0
        recover = 0
        die = 0
        infect = 0
        for v in infected:
            inf = m[v[0]][v[1]]
            recover = inf.tryRecover()
            if recover == 1:
                nextInf.append(v)
            die = inf.tryDie(args.deathProb, day)
            if die == 1:
                nextInf.append(v)
            infect = inf.tryInfect(args.spreadProb, day, args.minInfectedDays, args.maxInfectedDays)
            infected += infect
            infectN = len(infect)
            accDeceased += die
            accInfected += infectN
            newInfected += infectN
            newRecovered += recover
            newDead += die

        for i in nextInf:
            try:
                infected.remove(i)
            except:
                k = 1
        if args.daily:
            printMatrix(m)
        printInfo(args, day, newInfected, newDead, newRecovered, len(infected), accInfected, accDeceased)
        if args.pause:
            input()
        if not args.pause and args.daily:
            time.sleep(0.25)
        day += 1



def main(args):
    individuals = [[Individual(j,i) for i in range(args.N)] for j in range(args.N)]
    addNeighbors(individuals, args.N)
    initializeInfected(individuals, args.infectedPos, args.infectedNumber, args.minInfectedDays, args.maxInfectedDays)
    runSim(individuals, args)
            

if __name__ == "__main__":
    args = getArgs()
    main(args)
