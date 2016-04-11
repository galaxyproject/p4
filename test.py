# -*- coding: utf-8 -*-
import unittest
from process import PullRequestFilter, UPVOTE_REGEX, DOWNVOTE_REGEX
import datetime
import parsedatetime
from attrdict import AttrDict


class TestYaml(unittest.TestCase):

    def test_readable_yaml(self):
        import yaml
        with open('conf.yaml', 'r') as handle:
            data = yaml.load(handle)

        self.assertTrue('meta' in data)


class TestPullRequestFilter(unittest.TestCase):

    def setUp(self):
        pass

    def _get_dt_from_relative(self, relative):
        calendar = parsedatetime.Calendar()
        adj, parsed_as = calendar.parseDT(relative, datetime.datetime.now())
        return adj

    def test_created_at(self):
        prf = PullRequestFilter("test_filter", [], [])
        fakepr = AttrDict({
            'created_at': self._get_dt_from_relative("1 day ago")
        })

        self.assertFalse(
            prf.evaluate(
                fakepr,
                'created_at__lt',
                "relative::7 days ago"
            )
        )

        self.assertTrue(
            prf.evaluate(
                fakepr,
                'created_at__gt',
                "precise::2016-01-01",
            )
        )

        self.assertTrue(
            prf.evaluate(
                fakepr,
                'created_at__lt',
                "relative::tomorrow"
            )
        )

        prf = PullRequestFilter("test_filter", [], [])
        fakepr = AttrDict({
            'created_at': self._get_dt_from_relative("10 days ago")
        })

        self.assertTrue(
            prf.evaluate(
                fakepr,
                'created_at__lt',
                "relative::7 days ago"
            )
        )

        prf = PullRequestFilter("test_filter", [], [])
        fakepr = AttrDict({
            'created_at': self._get_dt_from_relative("1 day ago")
        })

        self.assertTrue(
            prf.evaluate(
                fakepr,
                'created_at__lt',
                "relative::today"
            )
        )

        self.assertFalse(
            prf.evaluate(
                fakepr,
                'created_at__lt',
                "relative::2 days ago"
            )
        )

    def test_check_to_branch(self):
        prf = PullRequestFilter("test_filter", [], [])
        fakepr = AttrDict({
            'base': {
                'ref': 'dev'
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
                'created_at__ge',
                'relative::3 days ago',
            )
        )

        self.assertTrue(
            prf.evaluate(
                fakepr,
                'created_at__lt',
                'relative::today',
            )
        )

    def test_find_in_comments(self):
        comments_container = [
            [AttrDict({'body': '+1', 'expect': True})],
            [AttrDict({'body': ':+1:', 'expect': True})],
            [AttrDict({'body': 'asdf +1 asdf', 'expect': False})],
            [AttrDict({'body': 'asdf :+1: asdf', 'expect': True})],
            [AttrDict({'body': 'asdf\n+1\nasdf', 'expect': True})],
            [AttrDict({'body': 'asdf\n:+1:\nasdf', 'expect': True})],
            [AttrDict({'body': """Yeah, dunno about travis either, but I'm a bit nervous to break the build for everyone else.
You have my :+1:, but I'd like a second pair of eyes merging this.""", 'expect': True})],
        ]
        for x in comments_container:
            # Get comments needs to return a callable, so we shoehorn in a
            # closure to return 'x'
            prf = PullRequestFilter("test_filter", [], [])

            def q():
                return x

            # Then set up as function on fpr. There's probably an easier way to
            # do this but whatever.
            prf.issue = AttrDict({
                'get_comments': q
            })
            fpr = AttrDict({
            })
            result = len(list(prf._find_in_comments(fpr, UPVOTE_REGEX))) > 0,
            self.assertEquals(
                result[0],
                x[0]['expect'],
                msg="body: '%s' did not produce the expected result." % x[0]['body']
            )

    def test_check_minus_member(self):
        prf = PullRequestFilter("test_filter", [], [], committer_group=['erasche'])
        test_cases = [
            {'body': '-1', 'user': {'login': 'erasche'}, 'counts': 1},
            {'body': '-1  ', 'user': {'login': 'erasche'}, 'counts': 1},
            {'body': ':-1:', 'user': {'login': 'erasche'}, 'counts': 1},
            {'body': 'asdf  -1   asdf', 'user': {'login': 'erasche'}, 'counts': 0},
            {'body': 'asdf  :-1: asdf', 'user': {'login': 'erasche'}, 'counts': 1},
            {'body': 'asdf\n -1\n asdf', 'user': {'login': 'erasche'}, 'counts': 1},
            {'body': 'asdf\n:-1:\nasdf', 'user': {'login': 'erasche'}, 'counts': 1},
        ]

        for case in test_cases:
            tmppr = AttrDict({
                'state': 'open',
                'memo_comments': [case]
            })

            self.assertEquals(
                case['counts'],
                prf.check_minus(
                    tmppr
                ),
                msg="'%s' failed" % case['body']
            )

    def test_check_minus_nonmember(self):
        prf = PullRequestFilter("test_filter", [], [], committer_group=[''])
        test_cases = [
            {'body': '-1', 'user': {'login': 'erasche'}, 'counts': 0},
            {'body': '-1  ', 'user': {'login': 'erasche'}, 'counts': 0},
            {'body': ':-1:', 'user': {'login': 'erasche'}, 'counts': 0},
            {'body': 'asdf  -1   asdf', 'user': {'login': 'erasche'}, 'counts': 0},
            {'body': 'asdf  :-1: asdf', 'user': {'login': 'erasche'}, 'counts': 0},
            {'body': 'asdf\n -1\n asdf', 'user': {'login': 'erasche'}, 'counts': 0},
            {'body': 'asdf\n:-1:\nasdf', 'user': {'login': 'erasche'}, 'counts': 0},
        ]

        for case in test_cases:
            tmppr = AttrDict({
                'state': 'open',
                'memo_comments': [case]
            })

            self.assertEquals(
                case['counts'],
                prf.check_minus(
                    tmppr
                ),
                msg="'%s' failed" % case['body']
            )

    def test_check_plus_member(self):
        prf = PullRequestFilter("test_filter", [], [], committer_group=['erasche'])
        test_cases = [
            {'body': '+1', 'user': {'login': 'erasche'}, 'counts': 1},
            {'body': '+1  ', 'user': {'login': 'erasche'}, 'counts': 1},
            {'body': ':+1:', 'user': {'login': 'erasche'}, 'counts': 1},
            {'body': 'asdf  +1   asdf', 'user': {'login': 'erasche'}, 'counts': 0},
            {'body': 'asdf  :+1: asdf', 'user': {'login': 'erasche'}, 'counts': 1},
            {'body': 'asdf\n +1\n asdf', 'user': {'login': 'erasche'}, 'counts': 1},
            {'body': 'asdf\n:+1:\nasdf', 'user': {'login': 'erasche'}, 'counts': 1},
            {'body': """Yeah, dunno about travis either, but I'm a bit nervous to break the build for everyone else.
             You have my :+1:, but I'd like a second pair of eyes merging this.""",
             'counts': 1, 'user': {'login': 'erasche'}},
        ]

        for case in test_cases:
            tmppr = AttrDict({
                'state': 'open',
                'memo_comments': [case]
            })

            self.assertEquals(
                case['counts'],
                prf.check_plus(
                    tmppr
                ),
                msg="'%s' failed" % case['body']
            )

    def test_check_plus_nonmember(self):
        prf = PullRequestFilter("test_filter", [], [], committer_group=[''])
        test_cases = [
            {'body': '+1', 'user': {'login': 'erasche'}, 'counts': 0},
            {'body': '+1  ', 'user': {'login': 'erasche'}, 'counts': 0},
            {'body': ':+1:', 'user': {'login': 'erasche'}, 'counts': 0},
            {'body': 'asdf  +1   asdf', 'user': {'login': 'erasche'}, 'counts': 0},
            {'body': 'asdf  :+1: asdf', 'user': {'login': 'erasche'}, 'counts': 0},
            {'body': 'asdf\n +1\n asdf', 'user': {'login': 'erasche'}, 'counts': 0},
            {'body': 'asdf\n:+1:\nasdf', 'user': {'login': 'erasche'}, 'counts': 0},
        ]

        for case in test_cases:
            tmppr = AttrDict({
                'state': 'open',
                'memo_comments': [case]
            })

            self.assertEquals(
                case['counts'],
                prf.check_plus(
                    tmppr
                ),
                msg="'%s' failed" % case['body']
            )

    def test_prf_apply_eval(self):
        prf = PullRequestFilter(
            "test_filter",
            {
                'state': 'open',
                'title_contains': '[PROCEDURES]',
                'title_contains__not': 'Blah',
                'to_branch': 'dev',
                'created_at__lt': 'relative::0 days ago',
                'created_at__ge': 'relative::2 days ago',
            },
            []
        )

        fakepr = AttrDict({
            u'title': u'[PROCEDURES] Testing…',
            u'state': u'open',
            u'base': {
                u'ref': u'dev'
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
                {'to_branch': 'dev', 'created_at__lt': 'relative::0 days ago'},
                {'title_contains__not': 'Blah'},
                {'created_at__ge': 'relative::2 days ago'},
            ],
            []
        )

        self.assertEquals(
            sorted(list(prf._condition_it())),
            sorted([
                ('state', 'open'),
                ('title_contains', '[PROCEDURES]'),
                ('title_contains__not', 'Blah'),
                ('to_branch', 'dev'),
                ('created_at__lt', 'relative::0 days ago'),
                ('created_at__ge', 'relative::2 days ago'),
            ])
        )
