from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument("path")

parser.add_argument("-l",
                    "--long",
                    action="store_true")

args = parser.parse_args()

print(args)
