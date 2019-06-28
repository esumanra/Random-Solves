import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-a')
parser.add_argument('-p', '--psr', help="mani", default=False)#, action='store_false')
args = parser.parse_args()

b = eval(str(args.psr))
print(args.a)
print(b, type(b))
