import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }


    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.domains:
            removed_words = set()
            for word in self.domains[variable]:
                if len(word) != variable.length:
                    removed_words.add(word)
            for words in removed_words:
                self.domains[variable].remove(words)
                

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        #anbe vaa en anbe vaa, munbe vaa en munbe vaa, poopu vaai poopu vaai
        revised = False

        # Get the overlap position between x and y
        overlap = self.crossword.overlaps.get((x, y))
        if overlap is None:
            return False  # No constraint between x and y

        x_index, y_index = overlap

        to_remove = set()

        for x_val in self.domains[x]:
            satisfies = False
            for y_val in self.domains[y]:
                if x_val[x_index] == y_val[y_index]:
                    satisfies = True
                    break
            if not satisfies:
                to_remove.add(x_val)
                revised = True

        for val in to_remove:
            self.domains[x].remove(val)

        return revised
        

    def ac3(self, arcs=None):

        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Initialize arcs
        if arcs is None:
            arcs = list(self.crossword.overlaps)

        while arcs:
            x, y = arcs.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for neighbor in self.crossword.neighbors(x) - {y}:
                    arcs.append((neighbor, x))
        return True



    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.crossword.variables:
            if variable not in assignment or assignment[variable] is None:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        values = list(assignment.values())
        if len(values) != len(set(values)):
            return False  # duplicate words found

        for var in assignment:
            word = assignment[var]

        # Check correct length
            if len(word) != var.length:
                return False

        # Check for conflicts with overlapping variables
            for other in assignment:
                if var == other:
                    continue
                overlap = self.crossword.overlaps.get((var, other))
                if overlap:
                    i, j = overlap
                    if word[i] != assignment[other][j]:
                        return False

        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        return_value = dict()
        values = self.domains[var]
        neighbors = self.crossword.neighbors(var)

        for value in values:
            count = 0
            for neighbor in neighbors:
                if neighbor in assignment:
                    continue

                overlap = self.crossword.overlaps.get((var, neighbor))
                if overlap is None:
                    continue

                i, j = overlap
                for neighbor_val in self.domains[neighbor]:
                    if value[i] != neighbor_val[j]:
                        count += 1

            return_value[value] = count

    
        return sorted(values, key=lambda v: return_value[v])
        

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
    
        variables = list(self.domains)
        list_var = dict()

        for variable in variables:
            if variable in assignment:
                continue
            else:
                val_len = len(self.domains[variable])
                list_var[variable] = val_len

        min_val = min(list_var.values())
        min_vars = [var for var in list_var if list_var[var] == min_val]

        if len(min_vars) == 1:
            return min_vars[0]
        else:
            return max(min_vars, key = lambda var: len(self.crossword.neighbors(var)))


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        else:
            new_var = self.select_unassigned_variable(assignment)
            for value in self.order_domain_values(new_var, assignment):
                new_assignment = assignment.copy()
                new_assignment[new_var] = value

                if self.consistent(new_assignment):
                    result = self.backtrack(new_assignment)

                    if result is not None:
                        return result
        return None

 
        


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
