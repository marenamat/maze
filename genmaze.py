import maze

if __name__ == "__main__":
    maze.PDF().draw([maze.Maze(35,50,seed) for seed in range(100)])
#    maze.PDF().draw([maze.Maze(35,50,1)])
#    maze.PDF().draw([maze.Maze(10,15,1)])
