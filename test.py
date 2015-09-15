# -*- coding: utf-8 -*-
import unittest
from process import PullRequestFilter
import datetime
import parsedatetime
from attrdict import AttrDict


class TestPullRequestFilter(unittest.TestCase):

    def setUp(self):
        pass

    def _get_dt_from_relative(self, relative):
        calendar = parsedatetime.Calendar()
        adj, parsed_as = calendar.parseDT(relative, datetime.datetime.now())
        return adj

    def test_check_older_than(self):
        prf = PullRequestFilter("test_filter", [], [])
        fakepr = AttrDict({
            'created_at': self._get_dt_from_relative("1 day ago")
        })

        self.assertFalse(
            prf.check_older_than(
                fakepr,
                cv="7 days ago"
            )
        )

        self.assertTrue(
            prf.check_older_than(
                fakepr,
                cv="tomorrow"
            )
        )

        prf = PullRequestFilter("test_filter", [], [])
        fakepr = AttrDict({
            'created_at': self._get_dt_from_relative("10 days ago")
        })

        self.assertTrue(
            prf.check_older_than(
                fakepr,
                cv="7 days ago"
            )
        )

        prf = PullRequestFilter("test_filter", [], [])
        fakepr = AttrDict({
            'created_at': self._get_dt_from_relative("1 day ago")
        })

        self.assertTrue(
            prf.check_older_than(
                fakepr,
                cv="today"
            )
        )

        self.assertFalse(
            prf.check_older_than(
                fakepr,
                cv="2 days ago"
            )
        )

    def test_check_to_branch(self):
        prf = PullRequestFilter("test_filter", [], [])
        fakepr = AttrDict({
            'resource': {
                'base': {
                    'ref': 'dev'
                }
            }
        })

        self.assertTrue(
            prf.check_to_branch(
                fakepr,
                cv="dev"
            )
        )

        self.assertFalse(
            prf.check_to_branch(
                fakepr,
                cv="notdev"
            )
        )

    def test_check_state(self):
        prf = PullRequestFilter("test_filter", [], [])
        fakepr = AttrDict({
            'state': 'open'
        })

        self.assertTrue(
            prf.check_state(
                fakepr,
                cv="open"
            )
        )

        self.assertFalse(
            prf.check_state(
                fakepr,
                cv="closed"
            )
        )

    def test_check_title_contains(self):
        prf = PullRequestFilter("test_filter", [], [])
        fakepr = AttrDict({
            u'title': u'[PROCEDURES] Testing…'
        })

        self.assertTrue(
            prf.check_title_contains(
                fakepr,
                cv="[PROCEDURES]"
            )
        )

        self.assertFalse(
            prf.check_title_contains(
                fakepr,
                cv="anything-else"
            )
        )
    def test_pr_evaluate(self):
        prf = PullRequestFilter("test_filter", [], [])
        fakepr = AttrDict({
            u'title': u'[PROCEDURES] Testing…',
            u'state': u'open',
            u'resource': {
                u'base': {
                    u'ref': u'dev'
                }
            },
            u'created_at': self._get_dt_from_relative("1 day ago")
        })

        self.assertTrue(
            prf.evaluate(
                fakepr,
                'older_than__not',
                '3 days ago',
            )
        )

        self.assertTrue(
            prf.evaluate(
                fakepr,
                'older_than',
                'today',
            )
        )

    def test_prf_apply_eval(self):
        prf = PullRequestFilter(
            "test_filter",
            {
                'state': 'open',
                'title_contains': '[PROCEDURES]',
                'title_contains__not': 'Blah',
                'to_branch': 'dev',
                'older_than': '0 days ago',
                'older_than__not': '2 days ago',
            },
            []
        )

        fakepr = AttrDict({
            u'title': u'[PROCEDURES] Testing…',
            u'state': u'open',
            u'resource': {
                u'base': {
                    u'ref': u'dev'
                }
            },
            u'created_at': self._get_dt_from_relative("1 day ago")
        })

        for (condition_key, condition_value) in prf.conditions.items():
            self.assertTrue(prf.evaluate(fakepr, condition_key, condition_value))

    def test_prf_condition_iterator(self):
        prf = PullRequestFilter(
            "test_filter",
            [
                {'state': 'open', 'title_contains': '[PROCEDURES]'},
                {'to_branch': 'dev', 'older_than': '0 days ago'},
                {'title_contains__not': 'Blah'},
                {'older_than__not': '2 days ago'},
            ],
            []
        )

        self.assertEquals(
            sorted(list(prf.condition_it())),
            sorted([
                ('state', 'open'),
                ('title_contains', '[PROCEDURES]'),
                ('title_contains__not', 'Blah'),
                ('to_branch', 'dev'),
                ('older_than', '0 days ago'),
                ('older_than__not', '2 days ago'),
            ])
        )
