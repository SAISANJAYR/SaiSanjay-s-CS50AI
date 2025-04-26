import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = [[False for _ in range(self.width)] for _ in range(self.height)]

        # Add mines randomly
        while len(self.mines) < mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if (i, j) not in self.mines:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """ Prints a text-based representation of where mines are located. """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                print("|X" if self.board[i][j] else "| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines within one row and column of a given cell,
        not including the cell itself.
        """
        count = 0
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) == cell:
                    continue
                if 0 <= i < self.height and 0 <= j < self.width and self.board[i][j]:
                    count += 1
        return count

    def won(self):
        """ Checks if all mines have been flagged. """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game.
    A sentence consists of a set of board cells and a count of the number of those cells that are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """ Returns the set of all cells in self.cells known to be mines. """
        if len(self.cells) == self.count:
            return set(self.cells)
        return set()

    def known_safes(self):
        """ Returns the set of all cells in self.cells known to be safe. """
        if self.count == 0:
            return set(self.cells)
        return set()

    def mark_mine(self, cell):
        """ Updates internal knowledge representation given the fact that a cell is known to be a mine. """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """ Updates internal knowledge representation given the fact that a cell is known to be safe. """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player.
    """

    def __init__(self, height=8, width=8):
        self.height = height
        self.width = width
        self.moves_made = set()
        self.mines = set()
        self.safes = set()
        self.knowledge = []

    def mark_mine(self, cell):
        """ Marks a cell as a mine, and updates all knowledge to mark that cell as a mine as well. """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """ Marks a cell as safe, and updates all knowledge to mark that cell as safe as well. """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given safe cell,
        how many neighboring cells have mines in them.
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # Find all neighboring cells
        neighbors = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) == cell or not (0 <= i < self.height and 0 <= j < self.width):
                    continue
                if (i, j) in self.mines:
                    count -= 1
                elif (i, j) not in self.safes and (i, j) not in self.moves_made:
                    neighbors.add((i, j))

        # Add new sentence if not empty
        if neighbors:
            self.knowledge.append(Sentence(neighbors, count))

        # Update knowledge
        updated = True
        while updated:
            updated = False
            new_knowledge = []
            for sentence in self.knowledge:
                safes = sentence.known_safes()
                mines = sentence.known_mines()

                if safes:
                    for safe in safes.copy():
                        self.mark_safe(safe)
                    updated = True

                if mines:
                    for mine in mines.copy():
                        self.mark_mine(mine)
                    updated = True

            # Infer new sentences
            knowledge_copy = self.knowledge[:]
            for sentence1 in knowledge_copy:
                for sentence2 in knowledge_copy:
                    if sentence1 != sentence2 and sentence1.cells.issubset(sentence2.cells):
                        new_sentence = Sentence(sentence2.cells - sentence1.cells, sentence2.count - sentence1.count)
                        if new_sentence not in self.knowledge and len(new_sentence.cells) > 0:
                            new_knowledge.append(new_sentence)
                            updated = True

            self.knowledge.extend(new_knowledge)

    def make_safe_move(self):
        """ Returns a safe cell to choose on the Minesweeper board. """
        available_steps = self.safes - self.moves_made
        return random.choice(tuple(available_steps)) if available_steps else None

    def make_random_move(self):
        """ Returns a move to make on the Minesweeper board. """
        all_possible_moves = {
            (i, j) for i in range(self.height) for j in range(self.width)
        } - self.moves_made - self.mines
        return random.choice(tuple(all_possible_moves)) if all_possible_moves else None