class MatrizEsparsa:
    def __init__(self, linhas: int, colunas: int):
        self.colunas = colunas
        self.linhas = linhas
        self.corpo = (linhas, colunas)
        self.dado: dict[int, dict[int, float]] = {}  # linha -> {coluna -> valor}
        self.e_transposta = False

    @classmethod
    def carrega_do_arquivo(cls, caminho):
        with open(caminho, 'r') as f:
            linhas = f.readlines()

        linhas = len(linhas)
        colunas = len(linhas[0].strip().split())
        matriz = cls(linhas, colunas) 

        for i, linha in enumerate(linhas):
            for j, valor in enumerate(linha.strip().split()):
                matriz.inserir(i, j, float(valor))

        return matriz

    @classmethod
    def random(cls, linhas, colunas, densidade = 0.2, intervalo_valor=(1, 10)):
        import random
        matriz = cls(linhas, colunas)
        elementos_nao_nulos = int(linhas * colunas * densidade)

        for _ in range(elementos_nao_nulos):
            while True:
                i = random.randint(0, linhas - 1)
                j = random.randint(0, colunas - 1)
                if matriz.acessar(i, j) == 0:
                    valor = random.uniform(intervalo_valor[0], intervalo_valor[1])
                    matriz.inserir(i, j, valor)
                    break

        return matriz           
    
    # display matriz in a human-readable format
    def show(self, dense=False):
        if dense:
            for i in range(self.linhas):
                linha_valors = []
                for j in range(self.colunas):
                    linha_valors.append(str(self.acessar(i, j)))
                print(" ".join(linha_valors))
        else:
            for linha, colunas_dict in self.dado.items():
                for col, valor in colunas_dict.items():
                    print(f"({linha}, {col}): {valor}")

    # OPERAÇÕES DA MATRIZ
    def acessar(self, i, j):
        l, c = self.get_coordenadas(i, j)
        return self.dado.get(l, {}).get(c, 0.0)

    def inserir(self, i, j, valor):
        l, c = self.get_coordenadas(i, j)
        if valor == 0:
            if l in self.dado and c in self.dado[l]:
                del self.dado[l][c]
                if not self.dado[l]:
                    del self.dado[l]
        else:
            if l not in self.dado:
                self.dado[l] = {}
            self.dado[l][c] = valor

    def transpose(self):
        self.e_transposta = not self.e_transposta
        self.corpo = (self.corpo[1], self.corpo[0])

    def get_coordenadas(self, linha, coluna):
        if self.e_transposta:
            return coluna, linha
        return linha, coluna

    def soma(self, other): # TODO: Testa os zeros depois de somar.
        if not isinstance(other, MatrizEsparsa):
            raise ValueError("Só é possível somar matrizes do mesmo tipo.")

        if self.corpo != other.corpo:
            raise ValueError("As matrizes tem que ter a mesma dimenção para seram somadas.")
        
        resultado = MatrizEsparsa(self.linhas, self.colunas)
        
        for linha, colunas_dict in self.dado.items(): # Copia todos os elementos da primeira matriz
            resultado.dado[linha] = colunas_dict.copy()
        
        for linha, colunas_dict in other.dado.items(): # Soma os elementos das matrizes
            if linha not in resultado.dado:
                resultado.dado[linha] = {}
            for col, valor in colunas_dict.items():
                novo_valor = resultado.dado[linha].get(col, 0) + valor
                if novo_valor == 0:
                    if col in resultado.dado[linha]:
                        del resultado.dado[linha][col]
                else:
                    resultado.dado[linha][col] = novo_valor
            
            if not resultado.dado[linha]: # Deleta as linhas vazias
                del resultado.dado[linha]
        return resultado
        
    def __radd__(self, other):
        return self.soma(other)
        
    def mult_escalar(self, escalar):
        resultado = MatrizEsparsa(self.linhas, self.colunas)

        for linha, colunas_dict in self.dado.items():
            resultado.dado[linha] = {}
            for col, valor in colunas_dict.items():
                novo_valor = valor * escalar
                if novo_valor != 0:
                    resultado.dado[linha][col] = novo_valor
            
            if not resultado.dado[linha]:
                del resultado.dado[linha]

        return resultado

    def mult_matriz(self, other):
        if self.colunas != other.linhas:
            raise ValueError("Dimensões diferentes")
        
        resultado = MatrizEsparsa(self.linhas, other.colunas)
        
        for a_linha, a_colunas in self.dado.items():
            resultado_linha = {}
            
            for a_col, a_val in a_colunas.items():
                if a_col in other.dado:
                    for b_col, b_val in other.dado[a_col].items():
                        resultado_linha[b_col] = resultado_linha.get(b_col, 0) + a_val * b_val
            
            resultado_linha = {col: val for col, val in resultado_linha.items() if val != 0}
            if resultado_linha:
                resultado.dado[a_linha] = resultado_linha
        
        return resultado

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return self.mult_escalar(other)
        elif isinstance(other, MatrizEsparsa):
            return self.mult_matriz(other)
        else:
            raise NotImplementedError("Multiplication only supports escalar valors or another MatrizEsparsa.")
        
    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return self.__mul__(other)
        elif isinstance(other, MatrizEsparsa):
            return other.__mul__(self)
        else:
            raise NotImplementedError("Multiplication only supports escalar valors or another MatrizEsparsa.")