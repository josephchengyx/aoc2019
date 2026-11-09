from Refinery import Nanofactory

if __name__ == "__main__":
    with open("day14_input.txt") as file:
        data = list(map(lambda line: line.rstrip(), file.readlines()))

    nanofactory = Nanofactory(data)
