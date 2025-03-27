class Padding:
    def __init__(self, left=0, right=0, top=0, bottom=0):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.padx = (self.left, self.right)
        self.pady = (self.top, self.bottom)

    @staticmethod
    def all(padding):
        return Padding(padding, padding, padding, padding)

    @staticmethod
    def horizontal(padding):
        return Padding(padding, padding, 0, 0)

    @staticmethod
    def vertical(padding):
        return Padding(0,0, padding, padding)

    @staticmethod
    def symmetrical(horizontal, vertical):
        return Padding(horizontal, horizontal, vertical, vertical)

    @staticmethod
    def zero():
        return Padding(0, 0, 0, 0)