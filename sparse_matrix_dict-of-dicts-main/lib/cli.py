from typing import Dict
from .sparse_matrix import SparseMatrix

class CLI:
    def __init__(self):
        self.matrices: Dict[str, SparseMatrix] = {}

    def load_from_file(self, file_path: str, name: str) -> None:
        """Load a matrix from a file and store it in CSR format."""
        matrix = SparseMatrix.load_from_file(file_path)
        if matrix is not None:
            self.matrices[name] = matrix
            return matrix
        
        return None

    def show_help(self):
        # Rewrite the lines below in one print statement
        print(
            "\nAvailable commands:\n"
            "  load <file_path> <matrix>        - Load matrix from file\n"
            "  access <matrix> <i> <j>          - Access element at position (i,j)\n"
            "  insert <matrix> <i> <j> <value>  - Insert/update element at position (i,j)\n"
            "  transpose <matrix>               - Transpose matrix and store as result\n"
            "  sum <matrix1> <matrix2>          - Sum two matrices\n"
            "  smult <matrix> <scalar>          - Multiply matrix by scalar\n"
            "  mmult <matrix1> <matrix2>        - Multiply two matrices\n"
            "  print <matrix>                   - Print matrix information\n"
            "  help                             - Show this help message\n"
            "  exit                             - Exit the program\n\n"
        )   

    def process_command(self, command: str) -> None:
        """Process a single command from the user."""
        tokens = command.split()
        if not tokens:
            return

        cmd = tokens[0].lower()

        if cmd == "load" and len(tokens) == 3:
            file_path = tokens[1]
            matrix_name = tokens[2]
            if self.load_from_file(file_path, matrix_name) is not None:
                print(f"Matrix '{matrix_name}' loaded successfully.")
                return

        elif cmd == "access" and len(tokens) == 4:
            matrix_key = tokens[1]
            if not self._check_matrix_exists(matrix_key):
                return
            
            i = int(tokens[2])
            j = int(tokens[3])

            value = self.matrices[matrix_key].access(i, j)
            print(f"Value at position ({i}, {j}): {value}")

        elif cmd == "insert" and len(tokens) == 5:
            matrix_key = tokens[1]
            if not self._check_matrix_exists(matrix_key):
                return
            
            i = int(tokens[2])
            j = int(tokens[3])
            value = float(tokens[4])

            self.matrices[matrix_key].insert(i, j, value)

        elif cmd == "transpose" and len(tokens) == 2:
            matrix_key = tokens[1]
            if not self._check_matrix_exists(matrix_key):
                return

            self.matrices[matrix_key].transpose()

        elif cmd == "sum" and len(tokens) == 3:
            matrix1_key = tokens[1]
            if not self._check_matrix_exists(matrix1_key):
                return
            matrix1 = self.matrices[matrix1_key]
            
            matrix2_key = tokens[2]
            if not self._check_matrix_exists(matrix2_key):
                return
            matrix2 = self.matrices[matrix2_key]

            result = matrix1 + matrix2
            print(f'result:')
            result.show()
            
        elif cmd == "smult" and len(tokens) == 3:
            matrix_key = tokens[1]
            if not self._check_matrix_exists(matrix_key):
                return

            scalar = float(tokens[2])
            result = scalar * self.matrices[matrix_key]
            print(f'result:')
            result.show()

        elif cmd == "mmult" and len(tokens) == 3:
            matrix1_key = tokens[1]
            if not self._check_matrix_exists(matrix1_key):
                return
            matrix2_key = tokens[2]

            if not self._check_matrix_exists(matrix2_key):
                return
            result = self.matrices[matrix1_key] * self.matrices[matrix2_key]

            print(f'result:')
            result.show()

        elif cmd == "print" and len(tokens) == 2:
            matrix_key = tokens[1]
            if not self._check_matrix_exists(matrix_key):
                return
            
            self.matrices[matrix_key].show()

        else:
            print("Invalid command or incorrect number of arguments. Type 'help' for a list of commands.")

    def _check_matrix_exists(self, key: str) -> bool:
        if key not in self.matrices:
            print(f"Error: Matrix '{key}' not found.")
            return False
        return True
