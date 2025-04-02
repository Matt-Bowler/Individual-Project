class Wall:
    def __init__(self, row, col, orientation):
        self.row = row
        self.col = col
        self.orientation = orientation

    def __eq__(self, other):
        if isinstance(other, Wall):
            return (self.row == other.row and 
                    self.col == other.col and 
                    self.orientation == other.orientation)
        return False
    
    def __hash__(self):
        return hash((self.row, self.col, self.orientation))
    
    def __repr__(self):
        return str(self.row) + " " + str(self.col) + " " + str(self.orientation)
