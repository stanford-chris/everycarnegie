#!/usr/bin/env python3
"""Tests for the per-country spelling in carnegie_describe.py.

Before this, every Carnegie photo — American, Canadian, Trinidadian, whatever
— was described using everylibrary_describe.py's default prompt, which is
unconditionally British (right for everylibrary's own 100%-UK roster, wrong
for this one: 79% American, 13% UK/Ireland). 152 of 1,399 stored descriptions
already showed it. spelling_for() is the fix: British only for UK/Ireland
rows, American for everyone else.

Stdlib only, no network:

    python3 everycarnegie/test_carnegie_describe.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import carnegie_describe as cd


class SpellingForCountry(unittest.TestCase):

    def test_uk_gets_british(self):
        subject, spelling = cd.spelling_for({'country': 'United Kingdom'})
        self.assertEqual(spelling, 'British')

    def test_ireland_gets_british(self):
        subject, spelling = cd.spelling_for({'country': 'Ireland'})
        self.assertEqual(spelling, 'British')

    def test_united_states_gets_american(self):
        subject, spelling = cd.spelling_for({'country': 'United States'})
        self.assertEqual(spelling, 'American')

    def test_other_countries_get_american(self):
        # The default, not a second exception list: Canada, New Zealand,
        # South Africa, Trinidad and Tobago, etc. all fall through to it.
        for country in ('Canada', 'New Zealand', 'South Africa',
                        'Trinidad and Tobago', 'Mauritius'):
            subject, spelling = cd.spelling_for({'country': country})
            self.assertEqual(spelling, 'American', country)

    def test_missing_or_blank_country_gets_american(self):
        # Never silently fall through to the imported module's own British
        # default just because a row is missing its country field.
        self.assertEqual(cd.spelling_for({})[1], 'American')
        self.assertEqual(cd.spelling_for({'country': ''})[1], 'American')

    def test_subject_also_varies(self):
        uk_subject = cd.spelling_for({'country': 'United Kingdom'})[0]
        us_subject = cd.spelling_for({'country': 'United States'})[0]
        self.assertNotEqual(uk_subject, us_subject)


if __name__ == '__main__':
    unittest.main()
