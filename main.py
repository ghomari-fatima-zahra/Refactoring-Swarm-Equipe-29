import argparse
import os
from src.swarm import RefactoringSwarm

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_dir", type=str, required=True)
    args = parser.parse_args()

    abs_target = os.path.abspath(args.target_dir)
    if not os.path.isdir(abs_target):
        raise ValueError(f"Directory not found: {abs_target}")

    swarm = RefactoringSwarm(abs_target)
    swarm.run()

if __name__ == "__main__":
    main()