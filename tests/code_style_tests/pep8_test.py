import pep8
import os
import os.path
import unittest

import pep8

from module_tests.base_test_object import BaseTestObject


def ignore(string):
    """
    is the string in the list of ignored patterns
    """
    patterns = ('.svn', 'bin', 'htmlcov', '.egg-info', 'setup', '.idea', '.xml', '.iml', '.txt', '.jar', '.keystore',
                '.vscode', '.pyc', '.coverage', '.cfg', '.noseids', '.gitignore', '.html', 'README', 'shakedown.py',
                '.sql', '.sh', '.json', '.DS_Store', '.swp', 'psql', '.git', 'venv', '.yaml', '.yml', 'cover', 'dist')
    for pattern in patterns:
        if pattern in string:
            return True
    return False


class TestCodeFormat(BaseTestObject):
    def test_pep8(self):
        """
        verify our codebase complies with code style guidelines
        """
        style = pep8.StyleGuide(quiet=False)
        # accepted pep8 guideline deviances
        style.options.max_line_length = 122  # generally accepted limit
        style.options.ignore = ('W503', 'E402')  # operator at start of line

        errors = 0
        for root, _not_used, files in os.walk(os.getcwd()):
            if ignore(root):
                continue
            if not isinstance(files, list):
                files = [files]
            for f in files:
                if ignore(f):
                    continue
                file_path = ['{}/{}'.format(root, f)]
                result = style.check_files(file_path)  # type: pep8.BaseReport
                errors = result.total_errors

        self.assertEqual(0, errors, 'PEP8 style errors: {}'.format(errors))
