from raven.utils.testutils import TestCase

from raven.base import Client
from raven.events import Exception as ExceptionEvent


class ExceptionTest(TestCase):

    # Handle compatibility.
    if hasattr(Exception, '__suppress_context__'):
        # Then exception chains are supported.
        def transform_expected(self, expected):
            return expected
    else:
        # Otherwise, we only report the first element.
        def transform_expected(self, expected):
            return expected[:1]

    def check_capture(self, expected):
        """
        Check the return value of capture().

        Args:
          expected: the expected "type" values.
        """
        c = Client()
        event = ExceptionEvent(c)
        result = event.capture()
        info = result['exception']
        values = info['values']

        type_names = [value['type'] for value in values]
        expected = self.transform_expected(expected)

        self.assertEqual(type_names, expected)

    def test_simple(self):
        try:
            raise ValueError()
        except Exception:
            self.check_capture(['ValueError'])

    def test_nested(self):
        try:
            raise ValueError()
        except Exception:
            try:
                raise KeyError()
            except Exception:
                self.check_capture(['KeyError', 'ValueError'])

    def test_raise_from(self):
        try:
            raise ValueError()
        except Exception as exc:
            try:
                raise KeyError() from exc
            except Exception:
                self.check_capture(['KeyError', 'ValueError'])

    def test_raise_from_different(self):
        try:
            raise ValueError()
        except Exception as exc:
            try:
                raise KeyError() from TypeError()
            except Exception:
                self.check_capture(['KeyError', 'TypeError'])
