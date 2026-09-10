#!/usr/bin/env python3
"""Tests for the two-post shape in carnegie_post_preview.py.

The note — what became of the building — is a reply of its own since
11 September 2026, never on the first post. ⚠️ The trim tests are the point:
the note used to go out mid-sentence ("Originally a public library on the
Ohio…", Athens, Ohio) because a 96-character cap and the 300-character limit
each cut it on a word. A reply that is too long now loses whole sentences from
the end, and a sentence is not allowed to end on an initial or an abbreviation,
or "Frank L. Packard" is two sentences and the trim strands "Frank L."

Stdlib only, no network, no roster: every row is synthetic.

    python3 everycarnegie/test_carnegie_post_preview.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import carnegie_post_preview as cp

ROW = {
    "name": "Athens", "city": "Athens", "region": "Ohio", "country": "United States",
    "date_granted": "Dec 16, 1903", "grant": "$30,000", "date_opened": "",
    "address": "32 Park Place", "lat": "", "lon": "",
    "photographer": "Ed!(talk)(Hall of Fame)", "licence": "CC BY-SA 3.0",
}
NOTE = ("Designed by Columbus architect Frank L. Packard. Originally a public "
        "library on the Ohio University campus. Open 1905–1930, now Scripps Hall, "
        "used for classroom space")


class FirstPost(unittest.TestCase):
    def test_the_note_is_never_on_the_first_post(self):
        text = cp.build(ROW)
        self.assertNotIn("Packard", text)
        self.assertIn("$30,000 from Andrew Carnegie, December 16, 1903", text)
        self.assertIn("📷 Ed! (Hall of Fame) · CC BY-SA 3.0", text)
        self.assertTrue(text.endswith("#CarnegieLibraries #Libraries"))

    def test_no_double_blank_line_without_a_grant(self):
        row = dict(ROW, grant="", date_granted="")
        self.assertNotIn("\n\n\n", cp.build(row))


class NotePost(unittest.TestCase):
    def test_a_full_note_is_kept_whole_and_ends_with_a_full_stop(self):
        reply = cp.note_post(ROW, NOTE)
        self.assertEqual(reply, NOTE + ".")

    def test_no_note_means_no_reply(self):
        self.assertEqual(cp.note_post(ROW, ""), "")

    def test_a_lower_case_opening_is_capitalised(self):
        self.assertEqual(cp.note_post(ROW, "brick and stone construction"),
                         "Brick and stone construction.")

    def test_an_opening_date_is_rewritten_in_the_countrys_own_style(self):
        self.assertEqual(cp.note_post(ROW, "Opened 29 Feb 1916"), "Opened February 29, 1916.")
        uk = dict(ROW, country="England")
        self.assertEqual(cp.note_post(uk, "Opened Feb 29, 1916"), "Opened 29 February 1916.")

    def test_an_opening_date_with_prose_after_it_keeps_the_prose(self):
        self.assertEqual(
            cp.note_post(ROW, "Opened 19 Jan 1907, designed by Chicago architect Victor Andre Matteson"),
            "Opened January 19, 1907, designed by Chicago architect Victor Andre Matteson.")

    def test_quotes_are_curled(self):
        reply = cp.note_post(ROW, 'Sign reads "LIBRARY" and it\'s open')
        self.assertEqual(reply, "Sign reads “LIBRARY” and it’s open.")

    def test_a_long_note_loses_whole_sentences_never_words(self):
        s1 = "First sentence about the building, which goes on for a while."
        s2 = "Second sentence, also long enough to matter for the count here."
        s3 = "Third sentence that pushes the whole thing well past the limit."
        s4 = "Fourth sentence, which is the one that has to go, and then some more words."
        s5 = "Fifth sentence, more words again to be sure of it, and a few more still."
        note = " ".join([s1, s2, s3, s4, s5])
        self.assertGreater(len(note), cp.LIMIT)
        reply = cp.note_post(ROW, note)
        self.assertLessEqual(len(reply), cp.LIMIT)
        self.assertTrue(reply.endswith("."))
        self.assertNotIn("…", reply)
        self.assertEqual(reply, " ".join([s1, s2, s3, s4]))

    def test_an_initial_or_abbreviation_does_not_end_a_sentence(self):
        self.assertEqual(
            cp.sentences("Designed by Frank L. Packard. Opened c. 1905. Sold to Steel Co. and closed."),
            ["Designed by Frank L. Packard.", "Opened c. 1905.", "Sold to Steel Co. and closed."])
        self.assertEqual(cp.sentences("Site donated by R.C. Kerens. Now a museum."),
                         ["Site donated by R.C. Kerens.", "Now a museum."])

    def test_a_single_sentence_over_the_limit_is_the_only_case_that_gets_an_ellipsis(self):
        note = "A " + " ".join(["word"] * 200)
        reply = cp.note_post(ROW, note)
        self.assertLessEqual(len(reply), cp.LIMIT)
        self.assertTrue(reply.endswith("…"))
        self.assertNotIn("wor…", reply)          # cut on a space, not inside a word


class CleanNote(unittest.TestCase):
    def test_nothing_caps_the_note_any_more(self):
        long = "x" * 500
        self.assertEqual(cp.clean_note(long), long)

    def test_page_reference_residue_after_a_full_stop_is_dropped(self):
        self.assertEqual(cp.clean_note("Opened 1918. Designed by Ernest Coxhead. : 9, 12"),
                         "Opened 1918. Designed by Ernest Coxhead")
        self.assertEqual(cp.clean_note("Designed by G. Albert Lansburgh. : 9, 12 Today it is a library."),
                         "Designed by G. Albert Lansburgh. Today it is a library")

    def test_a_trailing_as_of_stamp_is_dropped_but_a_bare_year_note_is_not(self):
        self.assertEqual(cp.clean_note("Now the Academy of Visual Arts. (March 2015)"),
                         "Now the Academy of Visual Arts")
        self.assertEqual(cp.clean_note("Is still in use as the public library (July 2025)"),
                         "Is still in use as the public library")
        self.assertEqual(cp.clean_note("No longer a public library. (2013)"), "No longer a public library")
        self.assertEqual(cp.clean_note("Part of the Monteith Historic District (info)"),
                         "Part of the Monteith Historic District")
        self.assertEqual(cp.clean_note("(1929)"), "(1929)")
        self.assertEqual(cp.clean_note("Opened 1907 (Main library)"), "Opened 1907 (Main library)")

    def test_a_colon_that_is_not_a_page_reference_is_kept(self):
        self.assertEqual(cp.clean_note("Official name: Andrew Carnegie Free Library"),
                         "Official name: Andrew Carnegie Free Library")
        self.assertEqual(cp.clean_note("Opened: 1921"), "Opened: 1921")


if __name__ == "__main__":
    unittest.main()
