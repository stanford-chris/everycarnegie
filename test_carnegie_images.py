#!/usr/bin/env python3
"""Tests for the image re-sweep in carnegie_images.py.

⚠️ The tests that matter here are the ones asserting the sweep does NOTHING.
A recheck that finds new photographs is easy; one that quietly swaps the
photograph under an already-written description is the failure this rule
exists to prevent, and nothing downstream can detect it — alt_text.json is
keyed by library, and carnegie_describe.py only fills entries with no text, so
the old description simply keeps being served for a different building.

Stdlib only, no network, no state file on disk: state is a dict and the rows
are synthetic.

    python3 everycarnegie/test_carnegie_images.py
"""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import carnegie_images as ci


def row(key, name="Carnegie Library", image_file="", city="Springfield",
        region="Ohio"):
    return {"_key": key, "name": name, "city": city, "region": region,
            "image_file": image_file}


def meta(url="https://example.org/a.jpg"):
    return {"url": url, "artist": "A Photographer", "licence": "CC BY-SA 4.0"}


class ResolveSource(unittest.TestCase):

    def test_hand_approved_outranks_the_wikipedia_list(self):
        r = row("0:x", image_file="List.jpg")
        state = {"imageinfo": {"File:List.jpg": meta(), "File:Hand.jpg": meta()},
                 "geo": {}, "name": {}}
        approved = {"Carnegie Library|Springfield|Ohio": "Hand.jpg"}
        self.assertEqual(ci.resolve_source(r, state, approved),
                         ("hand-approved", "File:Hand.jpg"))

    def test_falls_through_when_the_list_file_does_not_resolve(self):
        r = row("0:x", image_file="Missing.jpg")
        state = {"imageinfo": {"File:Missing.jpg": None, "File:Geo.jpg": meta()},
                 "geo": {"0:x": {"title": "File:Geo.jpg"}}, "name": {}}
        self.assertEqual(ci.resolve_source(r, state, {}),
                         ("commons-geosearch", "File:Geo.jpg"))

    def test_nothing_anywhere_is_none(self):
        r = row("0:x")
        self.assertEqual(ci.resolve_source(r, {"imageinfo": {}, "geo": {},
                                               "name": {}}, {}),
                         (None, None))


class ExpireMisses(unittest.TestCase):

    def expire(self, state, rows, approved=None):
        with mock.patch.object(ci, "save_state"), mock.patch.object(ci, "log"):
            ci.expire_misses(state, rows, approved or {})
        return state

    def test_a_library_with_nothing_has_its_geo_miss_forgotten(self):
        state = {"imageinfo": {}, "geo": {"0:x": None}, "name": {}}
        self.expire(state, [row("0:x")])
        self.assertEqual(state["geo"], {})

    def test_a_library_with_a_picture_is_left_alone(self):
        """Its memos stay, so no stage re-asks and nothing can outrank."""
        state = {"imageinfo": {"File:Geo.jpg": meta()},
                 "geo": {"0:x": {"title": "File:Geo.jpg"}},
                 "name": {"0:x": {"title": None}}}
        self.expire(state, [row("0:x")])
        self.assertIn("0:x", state["geo"])
        self.assertIn("0:x", state["name"])

    def test_an_illustrated_librarys_unresolved_filename_is_protected(self):
        """⚠️ The subtle one, and the reason candidate_titles() exists.

        This library ships a geosearch photograph because its wikipedia-list
        filename resolved to None. Forgetting that None lets stage 1 re-resolve
        it, and wikipedia-list OUTRANKS geosearch: the picture changes, the
        description does not, and nothing reports it.
        """
        state = {"imageinfo": {"File:List.jpg": None, "File:Geo.jpg": meta()},
                 "geo": {"0:x": {"title": "File:Geo.jpg"}}, "name": {}}
        self.expire(state, [row("0:x", image_file="List.jpg")])
        self.assertIn("File:List.jpg", state["imageinfo"],
                      "an illustrated library's other candidates must survive")

    def test_an_unilluminated_librarys_filename_miss_is_forgotten(self):
        state = {"imageinfo": {"File:List.jpg": None}, "geo": {}, "name": {}}
        self.expire(state, [row("0:x", image_file="List.jpg")])
        self.assertEqual(state["imageinfo"], {})

    def test_namesearch_miss_is_forgotten_only_when_unilluminated(self):
        state = {"imageinfo": {"File:Geo.jpg": meta()},
                 "geo": {"1:y": {"title": "File:Geo.jpg"}},
                 "name": {"0:x": {"title": None}, "1:y": {"title": None}}}
        self.expire(state, [row("0:x"), row("1:y", name="Other")])
        self.assertNotIn("0:x", state["name"])
        self.assertIn("1:y", state["name"])

    def test_a_hand_approved_library_counts_as_illustrated(self):
        state = {"imageinfo": {"File:Hand.jpg": meta()},
                 "geo": {"0:x": None}, "name": {}}
        approved = {"Carnegie Library|Springfield|Ohio": "Hand.jpg"}
        self.expire(state, [row("0:x")], approved)
        self.assertIn("0:x", state["geo"],
                      "a hand-approved picture must not be swept over")

    def test_expiry_never_removes_a_working_image(self):
        """Whatever else it forgets, no resolvable file may be dropped."""
        state = {"imageinfo": {"File:A.jpg": meta(), "File:B.jpg": None},
                 "geo": {"0:x": {"title": "File:A.jpg"}, "1:y": None},
                 "name": {}}
        self.expire(state, [row("0:x"), row("1:y", name="Other")])
        self.assertEqual(state["imageinfo"]["File:A.jpg"], meta())

    def test_the_two_readers_cannot_disagree(self):
        """expire_misses asks resolve_source, so 'already has one' means the
        same thing to the sweep and to the manifest."""
        import inspect
        self.assertIn("resolve_source", inspect.getsource(ci.expire_misses))


if __name__ == '__main__':
    unittest.main()
