class SparseMatrix:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.data: dict[int, dict[int, float]] = {}  # row -> {col -> value}
        self.is_transposed = False
        self.shape = (rows, cols)

    @classmethod
    def load_from_file(cls, file_path):
        # load from a file containing the matrix in dense format
        with open(file_path, 'r') as f:
            lines = f.readlines()

        rows = len(lines)
        cols = len(lines[0].strip().split())
        matrix = cls(rows, cols) 

        for i, line in enumerate(lines):
            for j, value in enumerate(line.strip().split()):
                matrix.insert(i, j, float(value))

        return matrix

    @classmethod
    def random(cls, rows, cols, density=0.2, value_range=(1, 10)):
        import random
        matrix = cls(rows, cols)
        non_zero_elements = int(rows * cols * density)

        for _ in range(non_zero_elements):
            while True:
                i = random.randint(0, rows - 1)
                j = random.randint(0, cols - 1)
                if matrix.access(i, j) == 0:
                    value = random.uniform(value_range[0], value_range[1])
                    matrix.insert(i, j, value)
                    break

        return matrix           
    
    # display matrix in a human-readable format
    def show(self, dense=False):
        if dense:
            for i in range(self.rows):
                row_values = []
                for j in range(self.cols):
                    row_values.append(str(self.access(i, j)))
                print(" ".join(row_values))
        else:
            for row, cols_dict in self.data.items():
                for col, value in cols_dict.items():
                    print(f"({row}, {col}): {value}")

    # MATRIX OPERATIONS
    def access(self, i, j):
        r, c = self._get_coords(i, j)
        return self.data.get(r, {}).get(c, 0.0)

    def insert(self, i, j, value):
        r, c = self._get_coords(i, j)
        if value == 0:
            # Remove zero elements to maintain sparsity
            if r in self.data and c in self.data[r]:
                del self.data[r][c]
                if not self.data[r]:
                    del self.data[r]
        else:
            if r not in self.data:
                self.data[r] = {}
            self.data[r][c] = value

    def transpose(self):
        self.is_transposed = not self.is_transposed
        self.shape = (self.shape[1], self.shape[0])

    # handle transparent transposition
    def _get_coords(self, row, col):
        if self.is_transposed:
            return col, row
        return row, col

    def __add__(self, other): # TODO: Test zero values after addition
        if not isinstance(other, SparseMatrix):
            raise ValueError("Can only add another matrix of the same type.")

        if self.shape != other.shape:
            raise ValueError("Matrices must have the same dimension to be added.")
        
        result = SparseMatrix(self.rows, self.cols)
        
        # Copy all elements from self
        for row, cols_dict in self.data.items():
            result.data[row] = cols_dict.copy()
        
        # Add elements from other
        for row, cols_dict in other.data.items():
            if row not in result.data:
                result.data[row] = {}
            for col, value in cols_dict.items():
                new_value = result.data[row].get(col, 0) + value
                if new_value == 0:
                    if col in result.data[row]:
                        del result.data[row][col]
                else:
                    result.data[row][col] = new_value
            
            # Clean up empty rows
            if not result.data[row]:
                del result.data[row]
        
        return result
        
    def __radd__(self, other):
        return self.__add__(other)
        
    # Scalar multiplication
    def _scalar_mul(self, scalar):
        result = SparseMatrix(self.rows, self.cols)

        for row, cols_dict in self.data.items():
            result.data[row] = {}
            for col, value in cols_dict.items():
                new_value = value * scalar
                if new_value != 0:
                    result.data[row][col] = new_value
            
            if not result.data[row]:
                del result.data[row]

        return result

    def _matrix_mul(self, other):
        if self.cols != other.rows:
            raise ValueError("Incompatible dimensions for multiplication")
        
        result = SparseMatrix(self.rows, other.cols)
        
        # For each non-zero in A, multiply with relevant non-zeros in B
        for a_row, a_cols in self.data.items():
            # Build result row
            result_row = {}
            
            for a_col, a_val in a_cols.items():
                # If B has non-zeros in this column (a_col acts as row in B)
                if a_col in other.data:
                    for b_col, b_val in other.data[a_col].items():
                        result_row[b_col] = result_row.get(b_col, 0) + a_val * b_val
            
            # Remove zeros and store if non-empty
            result_row = {col: val for col, val in result_row.items() if val != 0}
            if result_row:
                result.data[a_row] = result_row
        
        return result

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return self._scalar_mul(other)
        elif isinstance(other, SparseMatrix):
            return self._matrix_mul(other)
        else:
            raise NotImplementedError("Multiplication only supports scalar values or another SparseMatrix.")
        
    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return self.__mul__(other)
        elif isinstance(other, SparseMatrix):
            return other.__mul__(self)
        else:
            raise NotImplementedError("Multiplication only supports scalar values or another SparseMatrix.")