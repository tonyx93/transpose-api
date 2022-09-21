from typing import Iterator
from flask import Flask, request, Response

app = Flask(__name__)

# Optimal Time Complexity: O(m*n) - All elements need to be accessed at least once
# Optimal Space Complexity: O(m*n) - Matrix elements are accessed out of order so buffered streaming is not possible

# API framework will also add additional overhead

@app.post("/simple")
def simple():
    """
    One of the many "clean" ways to transpose a valid matrix in Python without using external libraries like Numpy.
    
    Supports all data types with input validation (proper JSON array-of-arrays syntax)
    Will truncate rows to the match the length of the shortest row if the rows are uneven
    e.g. [[0,1],[2,3,4]] => [[0,2],[1,3]] (4 is ignored)

    Time: O(m*n):
      m*n to deserialize JSON input into matrix data structure
      m*n to zip columns for each row and collect into a list
      m*n to serialize JSON output
    Space: O(m*n)
      m*n to store original matrix
      m*n to store transposed matrix
    """
    matrix = request.json
    return list(zip(*matrix))


@app.post("/explicit")
def explicit():
    """
    Another one of the many "clean" ways to transpose a valid matrix in Python without using external libraries like Numpy.

    Supports all data types with input validation (proper JSON array-of-arrays syntax)
    Will IndexError if any([len(matrix[0]) > len(matrix[i]) for i in range(1, m)])
      (unlike zip(), which will stop when it reaches the first row that no longer has any more elements)
    Will truncate rows to the match len(matrix[0]) otherwise

    Time: O(m*n):
      m*n to deserialize JSON input into matrix data structure
      m*n to map elements to new transposed matrix
      m*n to serialize JSON output
    Space: O(m*n)
      m*n to store original matrix
      m*n to store transposed matrix
    """
    matrix = request.json
    # original = [[matrix[i][j] for j in range(len(matrix[0]))] for i in range(len(matrix))]
    transposed = [[matrix[i][j] for i in range(len(matrix))] for j in range(len(matrix[0]))]
    return transposed


@app.post("/raw")
def raw():
    """
    "Optimized" matrix transposition via byte manipulation
    Supports ASCII standard (i.e. ascii, utf-8, latin-1) using single byte encoding for characters
    WARNING: There is no input validation! Malformed input can lead to unexpected unbehavior e.g. infinite loops

    In this approach, we are storing raw input data as a byte array and then streaming the bytes back to the client
    in the order that represents the transposed matrix. There's no JSON serialization/deserialization and we're not
    creating any data structures that represent the input and output matrices

    It would be cool to begin writing to the response stream as we read data from the input stream, but in this case, it's not possible.
    We need to know the whole contents of the matrix in order to transpose it

    Time: O(m*n):
      m*n to read input bytes representing input matrix
      m*n to index input array
      m*n to write output bytes representing transposed matrix
    Space: O(m*n)
      m*n to store bytes representing input matrix
      m to store indexes for start of rows
    """
    data = memoryview(request.data)

    # iterate through input to index start of matrix rows
    index = []
    start = True
    for i in range(len(data)):
        if start:
            if _byte_is_numeric(data[i]):
                index.append(i)
                start = False
        else:
            if data[i] == 93: # byte represeting ']' character
                start = True
    del start

    # stream output to response
    def generate() -> Iterator[str]:
        yield "["
        last = False
        while not last:
            yield "["
            for i in range(len(index)):
                if i != 0:
                    yield ","
                ptr = index[i]
                while _byte_is_numeric(data[ptr]):
                    yield chr(data[ptr])
                    ptr += 1
                while _byte_is_ignored(data[ptr]):
                    ptr += 1
                match data[ptr]:
                    case 44: # ',' - means there are more elements
                        while not _byte_is_numeric(data[ptr]):
                            ptr += 1
                        index[i] = ptr
                    case 93: # ']' - means we're ready to break out at the end of this loop
                        last = True
                    case _:
                        # Could only happen if there are ignored characters between 2 numbers e.g. 2e6
                        # That's actually a valid number, but I'm not supporting it.
                        # If you want to add support for scientific notation, just add 'e' and '+' ASCII values to _byte_is_numeric()
                        raise ValueError(f"Unexpected '{data[ptr]}' character encountered at position {ptr}")
            yield "]"
            if not last:
                yield ","
        yield "]"
        yield "\n" # Not neccesary - Just keeping output consistent with the above implementations

    return Response(generate(), mimetype="application/json")


def _byte_is_numeric(b: int) -> bool:
    """
    Returns True if b represents a digit, -, or . in the standard ASCII table

    We can add other additional "numeric" characters like 'e' or '+' if needed because
    '[', ']', ',' are the only speicial tokens in a valid JSON array string representation
    """
    return 48 <= b <= 57 or b == 45 or b == 46

def _byte_is_ignored(b: int) -> bool:
    """
    Returns True if b should be ignored i.e. not a part of number, nor a special token ('[', ']', ',') 
    Examples include whitespace characters
    """
    return not _byte_is_numeric(b) and b != 91 and b != 93 and b != 44