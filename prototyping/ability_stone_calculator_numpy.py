from numpy import zeros, array, argmax
from pynput import keyboard
from os import system

chances = [0.25, 0.35, 0.45, 0.55, 0.65, 0.75]

def score(s_1, s_2, s_3):
    return s_1 + s_2 - s_3 - (abs(s_1 - s_2))


def make_lookup_table(facet_count):
    facet_count += 1
    dim = range(facet_count)

    f = facet_count
    #                 chance, remainingx3, succsessesx3
    expected_facets = zeros([6,   f, f, f,     f, f, f]) - 500
    print("Gerenrating Table")
    for s_1 in dim:
        for s_2 in dim:
            for s_3 in dim:
                expected_facets[:,0 , 0, 0, s_1, s_2, s_3] = score(s_1, s_2, s_3)
    
    for r_1 in dim:
        print(r_1 / facet_count * 100, " %")
        for r_2 in dim:
            for r_3 in dim:
                if r_1 == r_2 == r_3 == 0:
                                continue
                for s_1 in range(facet_count - r_1)[::-1]:
                    for s_2 in range(facet_count - r_2)[::-1]:
                        for s_3 in range(facet_count - r_3)[::-1]:
                            for chance in range(6):
                                suc_chance = chances[chance]
                                fail_chance = 1 - suc_chance
                                suc_chance_pointer = max(0, chance - 1)
                                fail_chance_pointer = min(5, chance + 1)

                                value = 0
                                if r_1 > 0:
                                    value = max(value, suc_chance * expected_facets[suc_chance_pointer, r_1 - 1, r_2, r_3, s_1 + 1, s_2, s_3] + fail_chance * expected_facets[fail_chance_pointer, r_1 - 1, r_2, r_3, s_1, s_2, s_3])
                                if r_2 > 0:
                                    value = max(value, suc_chance * expected_facets[suc_chance_pointer, r_1, r_2 - 1, r_3, s_1, s_2 + 1, s_3] + fail_chance * expected_facets[fail_chance_pointer, r_1, r_2 - 1, r_3, s_1, s_2, s_3])
                                if r_3 > 0:
                                    value = max(value, suc_chance * expected_facets[suc_chance_pointer, r_1, r_2, r_3 - 1, s_1, s_2, s_3 + 1] + fail_chance * expected_facets[fail_chance_pointer, r_1, r_2, r_3 - 1, s_1, s_2, s_3])

                                expected_facets[chance, r_1, r_2, r_3, s_1, s_2, s_3] = value


    return expected_facets


class Stone:
    def __init__(self, num_facets: int):
        self.num_facets = num_facets
        self.chance = 5
        self.row1 = []
        self.row2 = []
        self.row3 = []

    def copy(self):
        clone = Stone(self.num_facets)
        clone.chance = self.chance
        clone.row1 = self.row1.copy()
        clone.row2 = self.row2.copy()
        clone.row3 = self.row3.copy()
        return clone

    def to_array(self):
        return [self.chance, self.num_facets - len(self.row1), self.num_facets - len(self.row2), self.num_facets - len(self.row3), sum(self.row1), sum(self.row2), sum(self.row3)]

    def tap1(self, succ: bool):
        if len(self.row1) >= self.num_facets:
            return
        else:
            self.row1.append(succ)
        self.change_chance(succ)
    
    def tap2(self, succ: bool):
        if len(self.row2) >= self.num_facets:
            return
        else:
            self.row2.append(succ)
        self.change_chance(succ)
    
    def tap3(self, succ: bool):
        if len(self.row3) >= self.num_facets:
            return
        else:
            self.row3.append(succ)
        self.change_chance(succ)

    def change_chance(self, succ):
        if succ:
            self.chance = max(0, self.chance - 1)
        else:
            self.chance = min(5, self.chance + 1)

    def string(self):
        chances = [25, 35, 45, 55, 65, 75]
        res = "   success chance: " + str(chances[self.chance]) + " %\n\n  "
        for i in self.row1:
            res += " * " if i else " _ "

        res += "   "*(self.num_facets - len(self.row1))
        res += " " + str(sum(self.row1)) + " Z U\n\n  "

        for i in self.row2:
            res += " * " if i else " _ "
        
        res += "   "*(self.num_facets - len(self.row2))
        res += " " + str(sum(self.row2)) + " H J\n\n  "

        for i in self.row3:
            res += " * " if i else " _ "
        res += "   "*(self.num_facets - len(self.row3))
        res += " " + str(sum(self.row3)) + " N M\n\n  "

        res += "\n   Backspace: Undo, Delete: Reset, Esc: Page Up"
        return res

    
def get_score(stone, row):
    global table
    global chances
    global num_facets

    chance, r_1, r_2, r_3, s_1, s_2, s_3 = stone


    suc_chance = chances[chance]
    fail_chance = 1 - suc_chance
    suc_chance_pointer = max(0, chance - 1)
    fail_chance_pointer = min(5, chance + 1)

    if r_1 == 0 and row == 0:
        return -9
    if r_2 == 0 and row == 1:
        return -9
    if r_3 == 0 and row == 2:
        return -9

    if row == 0:
        return suc_chance * table[suc_chance_pointer, r_1 - 1, r_2, r_3, s_1 + 1, s_2, s_3] + fail_chance * table[fail_chance_pointer, r_1 - 1, r_2, r_3, s_1, s_2, s_3]
    if row == 1:
        return suc_chance * table[suc_chance_pointer, r_1, r_2 - 1, r_3, s_1, s_2 + 1, s_3] + fail_chance * table[fail_chance_pointer, r_1, r_2 - 1, r_3, s_1, s_2, s_3]
    if row == 2:
        return suc_chance * table[suc_chance_pointer, r_1, r_2, r_3 - 1, s_1, s_2, s_3 + 1] + fail_chance * table[fail_chance_pointer, r_1, r_2, r_3 - 1, s_1, s_2, s_3]
    
    

def on_press(key):
    global listener
    global stonestates
    global num_facets

    if key == keyboard.Key.page_up:
        print("Exiting")
        listener.stop()
        return

    elif key == keyboard.Key.backspace:
        if len(stonestates) > 1:
            stonestates = stonestates[:-1]
        cur_stone = stonestates[-1].copy()
    
    elif key == keyboard.Key.delete:
        stonestates = [Stone(num_facets)]
        cur_stone = stonestates[-1].copy()

    else:
        key = str(key)[1]
        cur_stone = stonestates[-1].copy()
        
        if key == "z": #suc 1
            cur_stone.tap1(1)
        
        if key == "h": #suc 2
            cur_stone.tap2(1)
        
        if key == "n": #suc 3
            cur_stone.tap3(1)

        
        if key == "u": #fail 1
            cur_stone.tap1(0)
        
        if key == "j": #fail 2
            cur_stone.tap2(0)
        
        if key == "m": #fail 3
            cur_stone.tap3(0)

        stonestates.append(cur_stone)


    system("cls")
    print(cur_stone.string())
    arr = cur_stone.to_array()
    scores = array([get_score(arr, 0), get_score(arr, 1), get_score(arr, 2)])
    print(scores)
    print("Do row: ", argmax(scores) + 1)


num_facets = int(input("num facets: "))

table = make_lookup_table(num_facets)

stonestates = [Stone(num_facets)]

system("cls")

print(stonestates[-1].string())
arr = stonestates[-1].to_array()
scores = array([get_score(arr, 0), get_score(arr, 1), get_score(arr, 2)])
print(scores)
print("Do row: ", argmax(scores) + 1)

listener = keyboard.Listener(on_press=on_press)
listener.start()
listener.join()

input("Press Enter to close the Window")