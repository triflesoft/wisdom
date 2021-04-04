from babel.core import Locale
from babel.dates import format_datetime
from babel.dates import format_date
from babel.dates import format_interval
from babel.dates import format_time
from babel.dates import format_timedelta
from babel.numbers import format_decimal
from babel.numbers import format_currency
from babel.numbers import format_percent
from babel.numbers import format_scientific
from copy import deepcopy
from csv import reader
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from decimal import Decimal
from io import StringIO
from logging import error
from os.path import abspath
from os.path import dirname
from os.path import normpath
from os.path import join
from re import compile
from re import UNICODE
from unicodedata import digit

from .base import embed_extension


NATURAL_SORT_SPLIT_PATTERN = compile('\d+', UNICODE)


class TCellBase:
    __slots__ = ('content', 'datatype', 'options', 'sort_order')

    def __init__(self, content, thead_cell=None):
        content = content.strip()

        self.content = content
        self.data_type = thead_cell.data_type if thead_cell else 'text'
        self.options = deepcopy(thead_cell.options) if thead_cell else {}
        self.sort_order = 0

        if content.startswith('|'):
            options_end = content.find('|', 1)

            if options_end > 0:
                self.content = content[options_end + 1:].strip()

                for option in content[1:options_end].split(' '):
                    if option.startswith('currency-'):
                        self.data_type = 'currency'
                        self.options['currency'] = option[9:].upper()
                    elif option.startswith('date-'):
                        self.data_type = 'date'
                        self.options['format'] = option[5:]
                    elif option.startswith('datetime-'):
                        self.data_type = 'datetime'
                        self.options['format'] = option[9:]
                    elif option == 'decimal':
                        self.data_type = 'decimal'
                    elif option.startswith('interval-'):
                        self.data_type = 'interval'
                        self.options['format'] = option[9:]
                    elif option == 'number':
                        self.data_type = 'number'
                    elif option == 'percent':
                        self.data_type = 'percent'
                    elif option == 'scientific':
                        self.data_type = 'scientific'
                    elif option.startswith('time-'):
                        self.data_type = 'time'
                        self.options['format'] = option[5:]
                    elif option.startswith('timedelta-'):
                        self.data_type = 'timedelta'
                        self.options['format'] = option[10:]

    def to_data(self):
        return self.content.replace('\t', '    ')


class THeadCellBase(TCellBase):
    def to_html(self, locale_code):
        return f'<th scope="col" class="data-type-{self.data_type}">{self.content}<span class="sort-icon"></span></th>'


class TBodyCellBase(TCellBase):
    __slots__ = ('datavalue',)

    def __init__(self, content, thead_cell):
        super().__init__(content, thead_cell)

        if self.data_type in ('currency', 'decimal', 'percent', 'scientific'):
            self.data_value = Decimal(self.content)
        elif self.data_type == 'date':
            self.data_value = date.fromisoformat(self.content)
        elif self.data_type == 'datetime':
            self.data_value = datetime.fromisoformat(self.content)
        elif self.data_type == 'time':
            self.data_value = time.fromisoformat(self.content)
        elif self.data_type == 'timedelta':
            if '.' in self.content:
                temp1, temp2 = self.content.split('.', 1)
                temp1, temp2 = int(temp1), time.fromisoformat(temp2)
            else:
                temp1, temp2 = 0, time.fromisoformat(self.content)

            self.data_value = timedelta(days=temp1, seconds=60 * (60 * temp2.hour + temp2.minute) + temp2.second)
        elif self.data_type == 'interval':
            temp1, temp2 = self.content.split('-')
            self.data_value = datetime.fromisoformat(temp1), datetime.fromisoformat(temp2)


class THeadCell(THeadCellBase):
    pass


class TBodyCell(TBodyCellBase):
    def to_html(self, locale_code):
        if self.data_type == 'currency':
            return '<td data-sort-order="{0:0=8X}" class="data-type-{1}"><data value="{2}">{3}</data></td>'.format(
                self.sort_order,
                self.data_type,
                self.data_value,
                format_currency(self.data_value, currency=self.options['currency'], locale=locale_code))
        elif self.data_type == 'date':
            return '<td data-sort-order="{0:0=8X}" class="data-type-{1}"><time datetime="{2}">{3}</time></td>'.format(
                self.sort_order,
                self.data_type,
                self.data_value.isoformat(),
                format_date(self.data_value, format=self.options['format'], locale=locale_code))
        elif self.data_type == 'datetime':
            return '<td data-sort-order="{0:0=8X}" class="data-type-{1}"><time datetime="{2}">{3}</time></td>'.format(
                self.sort_order,
                self.data_type,
                self.data_value.isoformat(),
                format_datetime(self.data_value, format=self.options['format'], locale=locale_code))
        elif self.data_type == 'decimal':
            return '<td data-sort-order="{0:0=8X}" class="data-type-{1}"><data value="{2}">{3}</data></td>'.format(
                self.sort_order,
                self.data_type,
                self.data_value,
                format_decimal(self.data_value, locale=locale_code))
        elif self.data_type == 'interval':
            return '<td data-sort-order="{0:0=8X}" class="data-type-{1}"><data value="{2}">{3}</data></td>'.format(
                self.sort_order,
                self.data_type,
                self.data_value,
                format_interval(self.data_value[0], self.data_value[1], locale=locale_code))
        elif self.data_type == 'percent':
            return '<td data-sort-order="{0:0=8X}" class="data-type-{1}"><data value="{2}">{3}</data></td>'.format(
                self.sort_order,
                self.data_type,
                self.data_value,
                format_percent(self.data_value, locale=locale_code))
        elif self.data_type == 'scientific':
            return '<td data-sort-order="{0:0=8X}" class="data-type-{1}"><data value="{2}">{3}</data></td>'.format(
                self.sort_order,
                self.data_type,
                self.data_value,
                format_scientific(self.data_value, locale=locale_code))
        elif self.data_type == 'time':
            return '<td data-sort-order="{0:0=8X}" class="data-type-{1}"><time datetime="{2}">{3}</time></td>'.format(
                self.sort_order,
                self.data_type,
                self.data_value.isoformat(),
                format_time(self.data_value, format=self.options['format'], locale=locale_code))
        elif self.data_type == 'timedelta':
            temp = int(self.data_value.total_seconds())

            return '<td data-sort-order="{0:0=8X}" class="data-type-{1}"><time datetime="PT{2}H{3}M{4}S">{5}</time></td>'.format(
                self.sort_order,
                self.data_type,
                temp % 60,
                (temp // 60) % 60,
                (temp // 3600),
                format_timedelta(self.data_value, format=self.options['format'], locale=locale_code))

        return '<td data-sort-order="{0:0=8X}" class="data-type-{1}">{2}</td>'.format(
            self.sort_order,
            self.data_type,
            self.content)


class TLineCell(TBodyCellBase):
    def to_html(self, locale_code):
        return f'<th scope="row" data-sort-order="{self.sort_order}" class="data-type-{self.data_type}">{self.data_value}</th>'


class TFootCell(THeadCellBase):
    pass


class TableCells:
    def __init__(self):
        self.thead = []
        self.tbody = []
        self.tfoot = []

    def _postprocess(self):
        def number_natural_sortkey(content):
            key = []
            last_index = 0

            for digit_match in NATURAL_SORT_SPLIT_PATTERN.finditer(content):
                if digit_match.start() > last_index:
                    key.append(content[last_index:digit_match.start()])

                value = 0

                for symbol in digit_match.group():
                    value = 10 * value + digit(symbol)

                key.append(value)
                last_index = digit_match.end()

            if last_index < len(content):
                key.append(content[last_index:])

            return key

        for column_index, thead_cell in enumerate(self.thead):
            sort_column = []

            if thead_cell.data_type == 'number':
                for tbody_row_index, tbody_row in enumerate(self.tbody):
                    sort_column.append((number_natural_sortkey(tbody_row[column_index].content), tbody_row_index))
            elif thead_cell.data_type in ('currency', 'decimal', 'percent', 'scientific'):
                for tbody_row_index, tbody_row in enumerate(self.tbody):
                    sort_column.append((tbody_row[column_index].data_value, tbody_row_index))
            else:
                for tbody_row_index, tbody_row in enumerate(self.tbody):
                    sort_column.append((tbody_row[column_index].content, tbody_row_index))

            sort_column = sorted(sort_column, key=lambda c: c[0])

            for sort_order, sort_cell in enumerate(sort_column):
                self.tbody[sort_cell[1]][column_index].sort_order = sort_order

    def load_csv(self, csv_rows, linenumber_column):
        if len(csv_rows) > 0:
            head_row = csv_rows[0]
            data_rows = csv_rows[1:]

            self.thead.append(THeadCell(linenumber_column))
            self.tfoot.append(TFootCell(linenumber_column))

            for head_cell in head_row:
                self.thead.append(THeadCell(head_cell))
                self.tfoot.append(TFootCell(head_cell))

            for data_row_index, data_row in enumerate(data_rows):
                tbody_row: list[TCellBase] = [TLineCell(f'{data_row_index + 1}', self.thead[0])]

                for column_index, thead_cell in enumerate(self.thead[1:]):
                    body_cell = data_row[column_index] if column_index < len(data_row) else ''
                    tbody_row.append(TBodyCell(body_cell, thead_cell))

                self.tbody.append(tbody_row)

            self._postprocess()

    def to_data(self):
        data_lines = []
        data_line = []

        for thead_cell in self.thead:
            data_line.append(thead_cell.to_data())

        data_lines.append('\t'.join(data_line))

        for tbody_row in self.tbody:
            data_line = []

            for tbody_cell in tbody_row:
                data_line.append(tbody_cell.to_data())

            data_lines.append('\t'.join(data_line))

        data_line = []

        for tfoot_cell in self.thead:
            data_line.append(tfoot_cell.to_data())

        data_lines.append('\t'.join(data_line))

        return '\r\n'.join(data_lines)

    def to_html(self, locale_code, table_data):
        html_lines = []
        html_lines.append('<div class="data-table-outer">')
        html_lines.append(f'<button class="original-code-copy" data-original-code="{table_data}">')
        html_lines.append('<img class="original-code-copy" src="static/images/icon-source-code-copy.svg" alt="" />')
        html_lines.append('</button>')
        html_lines.append('<div class="data-table-inner">')
        html_lines.append('<table class="data-table" data-sort-column="0" data-sort-direction="asc">')
        html_lines.append('<thead class="data-table-head">')
        html_lines.append('<tr class="data-table-head">')

        for thead_cell in self.thead:
            html_lines.append(thead_cell.to_html(locale_code))

        html_lines.append('</tr>')
        html_lines.append('</thead>')
        html_lines.append('<tbody>')

        for tbody_row in self.tbody:
            html_lines.append('<tr class="data-table-body">')

            for tbody_cell in tbody_row:
                html_lines.append(tbody_cell.to_html(locale_code))

            html_lines.append('</tr>')

        html_lines.append('</tbody>')
        html_lines.append('<tfoot>')
        html_lines.append('<tr class="data-table-foot">')

        for tfoot_cell in self.thead:
            html_lines.append(tfoot_cell.to_html(locale_code))

        html_lines.append('</tr>')
        html_lines.append('</tfoot>')
        html_lines.append('</table>')
        html_lines.append('</div>')
        html_lines.append('</div>')

        return ''.join(html_lines)


class DataTableDiscoverExtension(embed_extension('DataTableDiscoverExtensionBase', 'data_table')):
    def _process_markup(
            self,
            context,
            source_path,
            source_line,
            caller,
            content_path=None,
            linenumber_column='|decimal|#',
            cvs_dialect='excel'):

        return ''


class DataTableGenerateExtension(embed_extension('DataTableGenerateExtensionBase', 'data_table')):
    def _process_markup(
            self,
            context,
            source_path,
            source_line,
            caller,
            content_path=None,
            linenumber_column='|decimal|#',
            cvs_dialect='excel'):
        this = context['this']
        locale = Locale.parse(this.culture.code, sep='-')
        locale_code = '_'.join(part for part in (locale.language, locale.script, locale.territory) if part)
        csv_rows = []

        if content_path:
            with open(content_path, 'r', newline='') as csv_file:
                csv_reader = reader(csv_file, dialect=cvs_dialect)
                csv_rows = [csv_row for csv_row in csv_reader]
        else:
            with StringIO(str(caller())) as csv_file:
                csv_reader = reader(csv_file, dialect=cvs_dialect)
                csv_rows = [csv_row for csv_row in csv_reader]

        table_cells = TableCells()
        table_cells.load_csv(csv_rows, linenumber_column)
        table_data = table_cells.to_data()

        return table_cells.to_html(locale_code, table_data)
