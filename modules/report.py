from dataclasses import dataclass, field
from datetime import datetime
import json
from typing import Union


class Report:
    """
    Object that represents the Report about specified event records.
    """

    @dataclass
    class EventMetaData:
        """
        Object that represents the metadata (or summary) of an event record.
        """
        event_type: str
        event_time: str = field(default='')
        username: str = field(default='')
        serial_number: str = field(default='')
        status_display: str = field(default='')
        order_issues_count: int = field(default=0)
        errors_exist: bool = field(default=False)
        event_raw_data: Union[str, None] = field(default=None)

    def __init__(self, event_payload_full: dict) -> None:
        self._event_full_payload = event_payload_full
        self.context = {
            'event_count': len(self._event_full_payload.get('results', [])),
            'events_with_errors': 0,
            'events_with_order_issues': 0,
            'event_metadata_payload': {},
            'file_path': self._event_full_payload.get('file_path', '')
        }
        self._populate_context_event_metadata()

    def _populate_context_event_metadata(self) -> None:
        """
        Generates context dictionary by creating EventMetaData objects
        and puts them into self.context dictionary.
        :return: None
        """
        results = self._event_full_payload.get('results')
        for event_data in results:
            event_metadata = self._build_event_metadata(event_data)
            self.context['event_metadata_payload'][event_data['id']] = event_metadata

    def _build_event_metadata(self, event_data: dict) -> EventMetaData:
        """
        Cleans passed event_data dictionary and creates EventMetaData object from it.
        :param dict event_data: Dictionary with uncleaned event data from the full event payload
        :return EventMetaData: EventMetaData object
        """
        cleaned_event_data = self._clean_event_data(event_data)
        event_metadata = self.EventMetaData(**cleaned_event_data)
        self._increment_context_count_metrics(event_metadata)
        return event_metadata

    @classmethod
    def _clean_event_data(cls, event_data: dict) -> dict:
        """
        Clears passed event_data dictionary and returns dictionary with cleaned data.
        :param dict event_data: Uncleaned dictionary of an event object's fields.
        :return dict : Cleaned dictionary
        """
        user_data = (event_data.get('user', ''))
        username = user_data.get('username') if isinstance(user_data, dict) else ''
        timestamp = cls._format_timestamp_string(event_data.get('event_time', ''))
        event_model_data = event_data.get('model_data', '')
        event_model_data_is_dict = isinstance(event_model_data, dict)
        serial_number = event_model_data.get('reference', '') if event_model_data_is_dict else ''
        status_display = event_model_data.get('status_display', '') if event_model_data_is_dict else ''
        event_type = cls._clean_event_type_str(event_data.get('event_type', ''))
        order_issues = event_model_data.get('order_issues')
        order_issues_count = len(order_issues) if event_model_data_is_dict and isinstance(order_issues, list) else 0
        extra_data = event_data.get('extra_data', {})
        errors_exist = 'error' in extra_data if isinstance(extra_data, dict) else False
        cleaned_event_data = dict(event_type=event_type,
                                  event_time=timestamp,
                                  username=username,
                                  serial_number=serial_number,
                                  status_display=status_display,
                                  order_issues_count=order_issues_count,
                                  errors_exist=errors_exist,
                                  event_raw_data=json.dumps(event_data))
        return cleaned_event_data

    @staticmethod
    def _format_timestamp_string(timestamp_str: str) -> str:
        """
        Reforms passed timestamp string.
        :param str timestamp_str: string that's supposed to be formatted.
        :return str: formatted timestamp string
        """
        try:
            formatted_timestamp_str = datetime.strftime(
                datetime.strptime(
                    timestamp_str,
                    '%Y-%m-%dT%H:%M:%S.%fZ'
                ), '%d.%m.%Y, %H:%M')
        except ValueError:
            formatted_timestamp_str = ''
        return formatted_timestamp_str

    @staticmethod
    def _clean_event_type_str(event_type: str) -> str:
        """
        Returns the result of a lookup in valid_event_types dict by the.
        passed event_type, which is an empty string
        if the event_type key is not in valid_event_types.
        :param str event_type: Passed string
        :return str: Cleaned event type string
        """
        valid_event_types = {'created': 'CREATION',
                             'updated': 'UPDATE',
                             'transition': 'TRANSITION'}
        cleaned_event_type = valid_event_types.get(event_type, '')
        return cleaned_event_type

    def _increment_context_count_metrics(self, event_metadata: EventMetaData) -> None:
        """
        Increments values of EventMetaData's context
        from keys 'events_with_order_issues' and 'events_with_errors' by 1.
        :param EventMetaData event_metadata: EventMetaData object
        :return None
        """
        if event_metadata.order_issues_count:
            self.context['events_with_order_issues'] += 1
        if event_metadata.errors_exist:
            self.context['events_with_errors'] += 1
