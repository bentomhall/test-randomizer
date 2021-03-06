import sys,os
import argparse
import testwriter
from subprocess import call


parser = argparse.ArgumentParser(description="Create a set of permuted assessments in pdf format")
parser.add_argument('filename', metavar='input', help='the path to the text file containing the assessment data')
parser.add_argument('-p', '--permutations', dest='permute', nargs='?', 
                    action='store', default=1, type=int, help='the number of separate test forms to make.')
parser.add_argument('-s', '--subject', dest='subject', nargs='?', 
                    default='', action='store', help='the subject (chemistry, physics, etc) to be printed at the top of the assessment.')
parser.add_argument('-n', '--name', dest='name', nargs='?', action='store', default='',
                    help='The name of the assessment, to be printed in the header.')
parser.add_argument('-d', '--date', nargs='?', action='store', default='', help="The date of the assessment.")
parser.add_argument('-c', '--condensed', action='store_true', default=False, help="Use condensed output for multiple-choice. Default: each option on a new line (false)")
parser.add_argument('-v', '--verbose', 
                    action='store_true', default=False, 
                    help="print diagnostic information about the parsing process and exit after parsing.")
parser.add_argument('-i', '--include', action="store", default=None, help="Include a pdf file in each output. files should be base_name.n.pdf, where base_name is the argument here.")
parser.add_argument('--showBlank', action="store_true", default=False, help="show answer blank for MC and matching questions.")
args = parser.parse_args()

if args.subject == '':
    args.subject = input("What class is this for (this will appear in the assessment header, can be empty)? ")

while args.name == '':
    args.name = input("What should be printed as the name of the assessment (cannot be empty)? ")

if args.date == '':
    args.date = input("What is the date of the assessment (<enter> for no date)? ")

i = 0
latex = {"posix": "latexmk", "nt": "latexmk.exe"}
script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
while i < args.permute:
    fname, key_name = testwriter.main(args.filename, args.subject, args.name, args.date, index=i, condensed=args.condensed, verbose=args.verbose, includeFile=args.include, showBlank=args.showBlank, scriptDir=script_directory)
    i += 1