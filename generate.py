import sys

from crossword import *
import itertools


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
        self.enforce_node_consistency()     # unary constraints 
        self.ac3()                          # Binary constraints
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for v in self.domains :         # Iterate in domains
            remove_word = set()         # Set of words to remove in the domain
            for w in self.domains[v] :  # Iterate in the domain itself
                if len(w) != v.length : # If length doesn't match 
                    remove_word.add(w)  # Add the word to the set
            for w in remove_word :          # Iterate in the set
                self.domains[v].remove(w)   # Remove words of the set from domain


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False                             # In case no revision is done
        overlaps = self.crossword.overlaps[x, y]    # Take note of the overlaps
        if overlaps is not None :                   # In csae their are overlaps
            remove_word = set()                     # Set of words that need to be remove
            for x_w in self.domains[x] :            # Iterate in x's
                overlap_char = x_w(overlaps[0])     # Keep track of overlaps
                corresponding_y_char = {w[overlaps[1]] for w in self.domains[y]} # Find coresponding overlaps in y

                if overlap_char not in corresponding_y_char :   # If no corresponding is found 
                    remove_word.add(x_w)                        # Add to the set
                    revised = True                              # Take note the revision has been done
            for w in remove_word :                  # Iterate in the set
                self.domains[x].remove(w)           # Remove set words in the domains
        return revised                      # Return if revision has been done

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None: # Create a queue with the variables to be treated
            queue = list(itertools.product(self.crossword.variables, self.crossword.variables))
            queue = [arc for arc in queue if arc[0] != arc[1] and self.crossword.overlaps[arc[0], arc[1]] is not None]
        else:
            queue = arcs
        while queue:
            arc = queue.pop(0)                  # Move first element in queue into arc
            x, y = arc[0], arc[1]               # Take elements 0 and 1 from arc
            if self.revise(x, y):               # If revision between elements 0 and 1
                if not self.domains[x]:         # If no domain of element 0
                    print("ending ac3")         # End the ac3
                    return False                     # No arc has been done
                for z in (self.crossword.neighbors(x) - {y}):   # Iterate in neighbors
                    queue.append(((z, x)))                      # Add neighbors in teh queue
        return True                                  # Arc has been done


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for a in self.domains :
            if a not in assignment :
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        used_variables = []

        for var_x in assignment:        # Iterate in assignements
            val_x = assignment[var_x]

            # Inconsistent if a word is used multipke times
            if val_x in used_variables:
                return False
            used_variables.append(val_x)

            # Inconsistent if the lenght is incorrect
            if len(val_x) != var_x.length:
                return False

            # Inconsistent if overlaps are not respected
            for var_y in self.crossword.neighbors(var_x):
                if var_y in assignment:
                    val_y = assignment[var_y]

                    # Check if neighbor variable is assigned and satisfies constraints
                    if not self.overlap_satisfied(var_x, var_y, val_x, val_y):
                        return False

        # Otherwise evrythin is consistent
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        raise NotImplementedError


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
