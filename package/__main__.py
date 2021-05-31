import argparse
from filehelper.FileProcessor import FileProcessor

parser = argparse.ArgumentParser()

# Add custom arguments to the the parser
parser.add_argument('--version', '-v',
                    help='Display the version of the application.', action='store_true')
parser.add_argument('--rcomment', '-rc',
                    help='Remove the comments from pre-processing.', action='store_true')
parser.add_argument(
    '--path', '-p', help='The path of the file you want to check.')


# Initialize
def processDocument(path, rcomment):
    document = open(path)
    fp = FileProcessor()
    fp.preprocess(document, rcomment)
    document.close()


# Driver function
def main():
    arguments = parser.parse_args()

    # CLI Version required
    if arguments.version:
        print('version=0.1.0')
        if arguments.rcomment == False and arguments.path == None:
            return

    # If path is not provided in the arguments
    if arguments.path == None:
        path = input('Path to file : ')

    # Check for path validity
    try:
        processDocument(arguments.path or path, arguments.rcomment)
    except Exception as ex:
        print(ex)
        return


if __name__ == '__main__':
    main()
