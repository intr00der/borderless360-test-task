from rich.theme import Theme


class DefaultConsoleTheme(Theme):
    """
    Project's default theme with style mappings for the rich console.
    """
    TYPE_CREATED = 'type_created'
    TYPE_UPDATED = 'type_updated'
    TYPE_TRANSITION = 'type_transition'
    STATUS_OK = 'status_ok'
    STATUS_WARNING = 'status_warning'
    OK = 'ok'
    WARNING = 'warning'
    MAJOR_WARNING = 'major_warning'
    REPORT_HEADER = 'report_header'
    REPORT_SUMMARY_FIELD = 'report_summary_field'
    EVENT_FIELD = 'event_field'
    FINAL_SUMMARY_HEADER = 'final_summary_header'
    FINAL_SUMMARY_FIELD = 'final_summary_field'
    UNPARSED_FILES_FIELD = 'unparsed_files_field'

    THEME_DICT = {
        TYPE_CREATED: 'pale_green1 bold',
        TYPE_UPDATED: 'khaki3 bold',
        TYPE_TRANSITION: 'medium_purple2 bold',
        STATUS_OK: 'light_green bold underline',
        STATUS_WARNING: 'yellow bold underline',
        OK: 'light_green',
        WARNING: 'yellow bold',
        MAJOR_WARNING: 'red bold',
        REPORT_HEADER: 'white on dark_green bold',
        REPORT_SUMMARY_FIELD: 'bright_green bold',
        EVENT_FIELD: 'cyan bold',
        FINAL_SUMMARY_HEADER: 'white on bright_blue bold',
        FINAL_SUMMARY_FIELD: 'bright_blue bold',
        UNPARSED_FILES_FIELD: 'red bold underline',
    }

    def __init__(self) -> None:
        super().__init__(self.THEME_DICT, inherit=False)
