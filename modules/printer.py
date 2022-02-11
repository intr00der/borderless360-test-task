from typing import Union

from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateError
from pathlib import Path
from rich.console import Console

from datetime import datetime
import glob
import json
import natsort

from conf import settings
from modules.report import Report

# rich console theme
_theme = settings.DEFAULT_CONSOLE_THEME()
# rich console
_console = Console(theme=_theme, width=settings.DEFAULT_CONSOLE_WIDTH)
# rich console print name replacement
_print = _console.print


class ReportPrinter:
    """
    Object that handles printing of the reports.
    """

    def __init__(self,
                 file_path_patterns: str,
                 do_export: bool,
                 export_dest_path: str) -> None:
        self._file_paths = self._get_sorted_abs_path_list_from_pattern_list(file_path_patterns)
        self._check_file_count()
        self.do_export = do_export
        self.export_dest_path = self._get_abs_path_str(export_dest_path)
        self._context = {'template_filename': self.export_dest_path,
                         'created_at': datetime.now().strftime('%d.%m.%Y, %H:%M'),
                         'reports': [],
                         'event_count': 0,
                         'events_with_errors': 0,
                         'events_with_order_issues': 0,
                         'file_count': len(self._file_paths),
                         'unparsed_file_paths': []}

    @staticmethod
    def _get_abs_path_str(file_path: str) -> str:
        """
        Returns converted to string absolute PosixPath made out of passed path string.
        :param str file_path: Passed file path string
        :return str: Absolute file path string
        """
        return str(Path(file_path).absolute())

    @classmethod
    def _get_sorted_abs_path_list_from_pattern_list(cls, file_path_patterns: str) -> list[str]:
        """
        Searches for files for each pattern in passed file path patterns, converts to absolute paths,
        formulates a sorted list of those paths.
        :param str file_path_patterns: File path pattern by which files will be searched
        :return list[str]: Natural-sorted absolute file paths list
        """
        abs_path_set = set()
        for pattern in file_path_patterns:
            abs_pattern_matches = [cls._get_abs_path_str(match) for match in (glob.glob(pattern))]
            abs_path_set.update(abs_pattern_matches)
        sorted_abs_path_list = natsort.natsorted(abs_path_set)
        return sorted_abs_path_list

    def _check_file_count(self) -> None:
        """
        Checks if the amount of file paths that were found after pattern matching
        is not bigger than 0, quits the program if that's not the case.
        :return None:
        """
        if not len(self._file_paths) > 0:
            _print('No files match the specified/default file pattern.',
                   style=_theme.MAJOR_WARNING)
            exit(1)

    def print(self) -> None:
        """
        Prints reports and final summary on those reports
        from ReportPrinter object's self._context dictionary.
        :return None:
        """
        self._generate_and_print_reports()
        self._print_final_summary()

    def _generate_and_print_reports(self) -> None:
        """
        Reads files that matched the specified file pattern,
        formulates a Report object for each one that was decoded,
        prints report metadata and summary with metrics.
        :return None:
        """
        for file_path in self._file_paths:
            self._print_report_title(file_path)
            event_payload_full = self._read_event_json_data(file_path)
            if event_payload_full and isinstance(event_payload_full, dict):
                event_payload_full['file_path'] = file_path
                report = Report(event_payload_full)
                self._update_context_count_metrics(report)
                self._print_report(report)
                self._context['reports'].append(report.context)
            else:
                self._add_file_path_to_context_unparsed_list(file_path)

    @staticmethod
    def _print_report_title(file_path):
        _print('\n\n')
        ln = len(file_path)
        if ln > 30:
            file_path_end_slice = file_path[ln - 30: ln]
            _console.rule(f'[{_theme.REPORT_HEADER}]...{file_path_end_slice}[/{_theme.REPORT_HEADER}]',
                          style=_theme.REPORT_HEADER)
        else:
            _console.rule(f'[{_theme.REPORT_HEADER}]{file_path}[/{_theme.REPORT_HEADER}]',
                          style=_theme.REPORT_HEADER)
        _print('\n')

    @staticmethod
    def _read_event_json_data(file_path: str) -> dict:
        """
        Reads and JSON-decodes specified file path.
        :param str file_path: Passed file path for reading
        :return dict: Decoded event data dictionary
        """

        with open(file_path, 'r') as f:
            if file_path.endswith('.json'):
                try:
                    return json.loads(f.read())
                except (json.decoder.JSONDecodeError, FileNotFoundError):
                    _print(f"Skipping '{file_path}' (not found/corrupted/wrongly formulated/could not be decoded).",
                           style=_theme.WARNING)
            else:
                _print(f"Skipping '{file_path}' (non-JSON file).",
                       style=_theme.WARNING)

    def _print_final_summary(self) -> None:
        """
        Prints Final Summary of the created reports with global metrics.
        :return None:
        """
        event_count = self._context['event_count']
        events_with_order_issues = self._context['events_with_order_issues']
        events_with_order_issues_percentage = round(events_with_order_issues * 100 / event_count, 1)
        events_with_errors = self._context['events_with_errors']
        events_with_errors_percentage = round(events_with_errors * 100 / event_count, 1)

        _print('\n\n')
        _console.rule('[final_summary_header]FINAL SUMMARY[/final_summary_header]',
                      style=_theme.FINAL_SUMMARY_HEADER)
        _print('\n')

        _print(f"Reports: ", style=_theme.FINAL_SUMMARY_FIELD, end="")
        _print(len(self._context['reports']), style='bold')

        _print(f"Read files: ", style=_theme.FINAL_SUMMARY_FIELD, end="")
        _print(self._context['file_count'], style='bold')

        _print(f"Events: ", style=_theme.FINAL_SUMMARY_FIELD, end="")
        _print(event_count, style='bold')

        _print(f"Events with order issues: ", style=_theme.FINAL_SUMMARY_FIELD, end="")
        _print(events_with_order_issues,
               style=_theme.WARNING if events_with_order_issues > 0 else _theme.OK, end="")
        _print(f" ({events_with_order_issues_percentage}%)",
               style=_theme.WARNING if events_with_order_issues_percentage > 0 else _theme.OK)

        _print(f"Events with errors: ", style='final_summary_field', end="")
        _print(events_with_errors,
               style=_theme.WARNING if events_with_errors > 0 else _theme.OK, end="")
        _print(f" ({events_with_errors_percentage}%)",
               style=_theme.WARNING if events_with_errors_percentage > 0 else _theme.OK)

        _print(f"Read files: ", style=_theme.FINAL_SUMMARY_FIELD, end="")
        _print(self._context['file_count'], style='bold')

        unparsed_file_paths = self._context['unparsed_file_paths']
        if unparsed_file_paths:
            _print(f"\nUnparsed files ({len(unparsed_file_paths)}):", style=_theme.UNPARSED_FILES_FIELD)
            for unparsed_file_path in unparsed_file_paths:
                _print(f"- {unparsed_file_path}", style=_theme.MAJOR_WARNING)

        _print('\n')

    def export_to_html(self) -> None:
        """
        Renders ReportPrinter object's self._context dictionary as the string of html content,
        writes the content to the specified file destination.
        :return None
        """
        template_loader = FileSystemLoader(searchpath=settings.DEFAULT_TEMPLATES_DIR_PATH)
        template_env = Environment(loader=template_loader)
        template = template_env.get_template('index.html')

        self._clean_export_path()

        try:
            export_content = template.render(self._context)
            with open(self.export_dest_path, 'w') as f:
                f.write(export_content)
                self._print_export_success_message()
        except (IOError, AttributeError, TemplateError) as ex:
            self._print_export_failure_message(ex)

    def _print_export_success_message(self) -> None:
        """
        Prints HTML export success message.
        :return None
        """
        _print(f'Successfully exported reports to\n{self.export_dest_path}\n',
               style=_theme.OK)

    @staticmethod
    def _print_export_failure_message(exception: Union[IOError, AttributeError, TemplateError]) -> None:
        """
        Prints HTML export failure message.
        :param exception: Exception that took place during the export
        :return None
        """
        _print('Something went wrong while the program was trying to write the reports to the HTML template.',
               style=_theme.MAJOR_WARNING)
        _print(exception, style=_theme.WARNING)

    def _clean_export_path(self) -> None:
        """
        Appends '.html' to 'export_dest_path' if's not ending with it.
        :return None
        """
        if not self.export_dest_path.endswith('.html'):
            self.export_dest_path = f'{self.export_dest_path}.html'

    @classmethod
    def _print_report(cls, report: Report) -> None:
        """
        Prints Report summary and report's event metadata payload
        from Report object's self.context dictionary
        :param Report report: Report object
        :return None
        """
        cls._print_report_summary(report)
        cls._print_event_metadata_payload(report)

    @staticmethod
    def _print_report_summary(report: Report) -> None:
        """
        Prints report's summary from Report object's 'context' dictionary.
        :param Report report: Report object
        :return None
        """
        event_count = report.context['event_count']
        events_with_order_issues = report.context['events_with_order_issues']
        events_with_order_issues_percentage = round(events_with_order_issues * 100 / event_count, 1)
        events_with_errors = report.context['events_with_errors']
        events_with_errors_percentage = round(events_with_errors * 100 / event_count, 1)

        _console.rule('REPORT SUMMARY', style='bold')
        _print('\n')

        _print(f"Events: ", style=_theme.REPORT_SUMMARY_FIELD,
               end="")
        _print(event_count, style='bold')

        _print(f"Events with order issues: ", style=_theme.REPORT_SUMMARY_FIELD,
               end="")
        _print(events_with_order_issues,
               style=_theme.WARNING if events_with_order_issues > 0 else _theme.OK,
               end="")
        _print(f" ({events_with_order_issues_percentage}%)",
               style=_theme.WARNING if events_with_order_issues_percentage > 0 else _theme.OK)

        _print(f"Events with errors: ", style=_theme.REPORT_SUMMARY_FIELD,
               end="")
        _print(events_with_errors,
               style=_theme.WARNING if events_with_errors > 0 else _theme.OK,
               end="")
        _print(f" ({events_with_errors_percentage}%)",
               style=_theme.WARNING if events_with_errors_percentage > 0 else _theme.OK)

    @classmethod
    def _print_event_metadata_payload(cls, report):
        event_metadata_payload = report.context['event_metadata_payload']

        _print('\n')
        _console.rule('EVENT LIST', style='bold')
        _print('\n')

        for e_metadata in event_metadata_payload.values():
            cls._print_event_metadata(e_metadata)

    @staticmethod
    def _print_event_metadata(e_metadata: Report.EventMetaData) -> None:
        """
        Prints EventMetaData object's fields.
        :param Report.EventMetaData e_metadata: EventMetaData object
        :return None
        """
        _console.rule()

        event_type_theme_mapping = {'CREATION': _theme.TYPE_CREATED,
                                    'UPDATE': _theme.TYPE_UPDATED,
                                    'TRANSITION': _theme.TYPE_TRANSITION}
        _print(f"{e_metadata.event_type}",
               style=event_type_theme_mapping[e_metadata.event_type],
               justify='center')

        _print("Event time: ", style=_theme.EVENT_FIELD, end="")
        _print(e_metadata.event_time)

        _print("Username: ", style=_theme.EVENT_FIELD, end="")
        _print(e_metadata.username)

        _print("Status: ", style=_theme.EVENT_FIELD, end="")
        _print(f"{e_metadata.status_display}",
               style=_theme.STATUS_WARNING if e_metadata.status_display == 'Action Required' else _theme.STATUS_OK)

        _print("Issues count: ", style=_theme.EVENT_FIELD, end="")
        _print(e_metadata.order_issues_count,
               style=_theme.WARNING if e_metadata.order_issues_count > 0 else _theme.OK)

        _print(f"Errors exist: ", style=_theme.EVENT_FIELD, end="")
        if e_metadata.errors_exist:
            _print('Yes', style=_theme.WARNING)
        else:
            _print('No', style=_theme.OK)

    def _add_file_path_to_context_unparsed_list(self, file_path: str) -> None:
        """
        Adds specified file path to ReportPrinter object's self._context
        by the key of 'unparsed_file_paths'.
        :param str file_path: Specified file path
        :return None
        """
        self._context['unparsed_file_paths'].append(file_path)

    def _update_context_count_metrics(self, report: Report) -> None:
        """
        Adds values of keys 'event_count', 'events_with_errors' and 'events_with_order_issues'
        of a Report object's self.context to ReportPrinter object's self._context by the same keys.
        :param Report report: Report object
        :return None
        """
        self._context['event_count'] += report.context['event_count']
        self._context['events_with_errors'] += report.context['events_with_errors']
        self._context['events_with_order_issues'] += report.context['events_with_order_issues']
