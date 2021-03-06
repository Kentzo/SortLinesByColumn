import sublime
import sublime_plugin
import re


class SortLinesByColumnCommand(sublime_plugin.TextCommand):
    settings = sublime.load_settings(__name__ + '.sublime-settings')

    def run(self, edit, case_sensitive):
        split_regexp = self.settings.get('sortlinesbycolumn_split_regexp', '\W+')
        should_strip = self.settings.get('sortlinesbycolumn_should_strip', True)

        for selection in self.view.sel():
            if(selection is None or selection.empty()):
                continue

            selection_lines = self.view.lines(selection)

            if len(selection_lines) < 2:
                continue

            last_line_region = self.view.line(selection.end())
            last_word_region = self.view.word(selection.end())
            last_line_selection_str = self.view.substr(sublime.Region(last_line_region.begin(), last_word_region.end()))

            if should_strip:
                last_line_selection_str = last_line_selection_str.strip()

            column = len(re.split(split_regexp, last_line_selection_str)) - 1

            # Turn selected lines into tuple of full line (including new line char) and splitted line using regexp.
            lines = []
            for line_region in selection_lines:
                line_str = self.view.substr(line_region)

                if should_strip:
                    line_str = line_str.strip()

                row = re.split(split_regexp, line_str)

                if len(row):
                    lines.append([self.view.substr(self.view.full_line(line_region)), row])

            # Sort lines by the `column` item of row. If length of that row is less than `column`, consider key value as ''.
            if case_sensitive:
                sorted_lines = sorted(lines, key=lambda x: x[1][column] if len(x[1]) > column else '')
            else:
                sorted_lines = sorted(lines, key=lambda x: x[1][column].lower() if len(x[1]) > column else '')
            # Turn our sorted lines back to string
            sorted_lines_str = ''.join(line[0] for line in sorted_lines)

            # Write back sorted lines
            first_full_line_region = self.view.full_line(selection.begin())
            last_full_line_region = self.view.full_line(selection.end())
            self.view.replace(edit, sublime.Region(first_full_line_region.begin(), last_full_line_region.end()), sorted_lines_str)
