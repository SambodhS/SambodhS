import random
import numpy as np
import matplotlib.pyplot as plt
from pytictoc import TicToc

omega = 0.2
epsilon = 0.01
M_max = 100
alpha = 0.01
matrixSize = 201
iterations = 1

t = TicToc()

times = [
    0, 1, 2, 3, 4, 5, 6, 8, 10, 13, 16, 20, 25, 32, 40, 50, 63, 79, 100, 126, 158,
    200, 251, 316, 398, 501, 631, 794, 1000, 1259, 1585, 1995, 2512, 3162, 3981, 5012,
    6310, 7943, 10000, 12589, 15849, 19953, 25119, 31623, 39811, 50119, 63096, 79433,
    100000
]
values = {t: [] for t in times}

class App:
    @staticmethod
    def generateMatrix():
        mat = [[0] * matrixSize for _ in range(matrixSize)]
        return mat

    def memoryUpdate(mem, agentPosition):
        i = 0
        while i < len(mem):
            j = 0
            while j < len(mem[i]):
                if i == agentPosition[0] and j == agentPosition[1]:
                    delta = 1
                else:
                    delta = 0
                mem[i][j] += (alpha / M_max) * (M_max - mem[i][j]) ** 2 * delta - epsilon * mem[i][j]
                j += 1
            i += 1
        return mem

    def moveAgent(mat, agentPosition, pU, pD, pL, pR, wU, wD, wL, wR):
        r = random.uniform(0, 1)
        if r < pU:
            if agentPosition[0] != 0:
                mat[agentPosition[0] - 1][agentPosition[1]] = 1
                agentPosition[0] -= 1
            else:
                print("oh no!")
                App.moveAgent(mat, agentPosition, 0, wD / (wD + wL + wR), wL / (wD + wL + wR), wR / (wD + wL + wR), wU, wD, wL, wR)
        elif pU < r <= pU + pD:
            if agentPosition[0] != matrixSize - 1:
                mat[agentPosition[0] + 1][agentPosition[1]] = 1
                agentPosition[0] += 1
            else:
                print("oh no!")
                App.moveAgent(mat, agentPosition, wU / (wU + wL + wR), 0, wL / (wU + wL + wR), wR / (wU + wL + wR), wU, wD, wL, wR)
        elif pU + pD < r <= pU + pD + pL:
            if agentPosition[1] != 0:
                mat[agentPosition[0]][agentPosition[1] - 1] = 1
                agentPosition[1] -= 1
            else:
                print("oh no!")
                App.moveAgent(mat, agentPosition, wU / (wU + wD + wR), wD / (wU + wD + wR), 0, wR / (wU + wD + wR), wU, wD, wL, wR)
        elif pU + pD + pL < r <= pU + pD + pL + pR:
            if agentPosition[1] != matrixSize - 1:
                mat[agentPosition[0]][agentPosition[1] + 1] = 1
                agentPosition[1] += 1
            else:
                print("oh no!")
                App.moveAgent(mat, agentPosition, wU / (wU + wD + wL), wD / (wU + wD + wL), wL / (wU + wD + wL), 0, wU, wD, wL, wR)
        return mat, agentPosition

    def print2D(mat):
        for row in mat:
            print(row)

    @staticmethod
    def main():
        for iteration in range(iterations):
            print(iteration)
            mat = App.generateMatrix()
            mem = App.generateMatrix()
            evolution = App.generateMatrix()
            agentPosition = [int(matrixSize / 2), int(matrixSize / 2)]
            mat[agentPosition[0]][agentPosition[1]] = 1
            evolution[agentPosition[0]][agentPosition[1]] = 1
            for step in range(times[-1] + 1):
                try:
                    wU = np.exp(omega * mem[agentPosition[0] - 1][agentPosition[1]])
                except IndexError:
                    wU = 0
                try:
                    wD = np.exp(omega * mem[agentPosition[0] + 1][agentPosition[1]])
                except IndexError:
                    wD = 0
                try:
                    wL = np.exp(omega * mem[agentPosition[0]][agentPosition[1] - 1])
                except IndexError:
                    wL = 0
                try:
                    wR = np.exp(omega * mem[agentPosition[0]][agentPosition[1] + 1])
                except IndexError:
                    wR = 0
                mat[agentPosition[0]][agentPosition[1]] = 0
                mat, agentPosition = App.moveAgent(mat, agentPosition, wU / (wU + wD + wL + wR), wD / (wU + wD + wL + wR), wL / (wU + wD + wL + wR), wR / (wU + wD + wL + wR), wU, wD, wL, wR)
                mem = App.memoryUpdate(mem, agentPosition)
                evolution[agentPosition[0]][agentPosition[1]] = step
                if step in times:
                    values[step].extend([agentPosition[0] - matrixSize // 2, agentPosition[1] - matrixSize // 2])
            plt.imshow(evolution)
            plt.colorbar()
            plt.title("omega = " + str(omega) + ", epsilon = " + str(epsilon) + ", steps = " + str(times[-1]) + "")
            plt.show()
        for time in times:
            msd = np.mean([x ** 2 for x in values[time]])
            mstd = np.mean([x ** 4 for x in values[time]])
            merr = np.sqrt((mstd - msd ** 2) / iterations)
            print(time, msd, merr)

if __name__ == "__main__":
    t.tic()
    App.main()
    t.toc()