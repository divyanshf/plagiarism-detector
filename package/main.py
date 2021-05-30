import argparse

parser = argparse.ArgumentParser()

# Add custom arguments to the the parser
parser.add_argument('--version', '-v',
                    help='Display the version of the application.', action='store_true')
parser.add_argument('--rcomment', '-rc',
                    help='Remove the comments from pre-processing.', action='store_true')
parser.add_argument(
    '--path', '-p', help='The path of the file you want to check.')


def main():
    arguments = parser.parse_args()
    document = None

    # CLI Version required
    if arguments.version:
        print('version=0.1.0')

    # If path is not provided in the arguments
    if arguments.path == None:
        path = input('Path : ')

    # Check for path validity
    try:
        document = open(arguments.path or path).read()
        print(document)
    except:
        print('Invalid path detected!')
        return


if __name__ == '__main__':
    main()
