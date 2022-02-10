import argparse
from conf import settings
from modules.printer import ReportPrinter

# CLI for the printing program

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='command')
    print_parser = subparser.add_parser('print')

    print_parser.add_argument('-f',
                              '--files',
                              type=str,
                              nargs='+',
                              default=settings.DEFAULT_INPUT_PATH_PATTERN,
                              help=f'Specify input file pattern.\n'
                                   f'Every file that matches specified file pattern will be read.\n'
                                   f'Supports wildcards. Default path pattern is "{settings.DEFAULT_INPUT_PATH_PATTERN}"')
    print_parser.add_argument('-e',
                              '--do-export',
                              action='store_true',
                              help='Create HTML file which contains the report.\n'
                                   'Specify the output file path as an argument. (not required)'
                                   'Default output path is f"./output/{datetime.now()}_export.html"')
    print_parser.add_argument('-d',
                              '--dest-path',
                              type=str,
                              default=settings.DEFAULT_OUTPUT_PATH,
                              help=f'Specify output destination file path. Only works in -e(--export) argument is True.\n'
                                   f'Specified file must be an HTML file. Default path is "{settings.DEFAULT_OUTPUT_PATH}"\n'
                                   f' (file name depends on the time of command call)')

    args = parser.parse_args()
    if args.command == 'print':
        printer = ReportPrinter(file_path_patterns=args.files,
                                do_export=args.do_export,
                                export_dest_path=args.dest_path)
        printer.print()
        if args.do_export:
            printer.export_to_html()
