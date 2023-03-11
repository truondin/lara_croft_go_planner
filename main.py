from model.Game import Game
import sys


def main():
    game = Game()
    path = sys.argv[1]
    # game.play("./levels/level1.json")
    game.play(path)
    pass


if __name__ == '__main__':
    main()

