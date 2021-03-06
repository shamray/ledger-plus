import unittest
from ledger_core import *


class Parse(unittest.TestCase):
    def test_one_transaction(self):
        journal = '2015/10/16 bought food\n expenses:food  $10\n assets:cash'
        transactions = ['bought food']
        accounts = {
            'expenses': {
                'food': None
            },
            'assets': {
                'cash': None
            }
        }
        self.assertEqual(parse(journal), (transactions, accounts))


class ParsePayee(unittest.TestCase):
    def test_transaction_with_payee(self):
        self.assertEqual(parse_payee('2015/10/16 bought food'), 'bought food')

    def test_transaction_without_payee_space(self):
        self.assertEqual(parse_payee('2015/10/16 '), None)

    def test_transaction_without_payee(self):
        self.assertEqual(parse_payee('2015/10/16'), None)

    def test_transaction_wrong_string(self):
        self.assertEqual(parse_payee(' expenses:food  $10'), None)


class ParseAccountString(unittest.TestCase):
    def test_account_with_amount(self):
        self.assertEqual(parse_account_string(' expenses:food  $10'), 'expenses:food')

    def test_account_without_amount(self):
        self.assertEqual(parse_account_string(' expenses:food'), 'expenses:food')

    def test_account_wide_indent(self):
        self.assertEqual(parse_account_string('    expenses:food  $10'), 'expenses:food')

    def test_account_wide_spacing(self):
        self.assertEqual(parse_account_string(' expenses:food    $10'), 'expenses:food')

    def test_account_with_spaces_with_amount(self):
        self.assertEqual(parse_account_string(' expenses:fast food  $10'), 'expenses:fast food')

    def test_account_with_spaces_without_amount(self):
        self.assertEqual(parse_account_string(' expenses:fast food'), 'expenses:fast food')

    def test_empty_string(self):
        self.assertEqual(parse_account_string(''), None)


class ToAccount(unittest.TestCase):
    def test_1_level(self):
        self.assertEqual(to_account('expenses'), {'expenses': None})

    def test_2_levels(self):
        self.assertEqual(to_account('expenses:food'), {'expenses': {'food': None}})


class MergeDict(unittest.TestCase):
    def test_1_level_no_intersection(self):
        left = {'apples': None}
        right = {'oranges': None}

        self.assertEqual(merge_dict(left, right), {'apples': None, 'oranges': None})

    def test_2_levels_1_level(self):
        left = {'fruits': {'apples': None, 'oranges': None}}
        right = {'veggies': None}

        self.assertEqual(merge_dict(left, right), {'fruits': {'apples': None, 'oranges': None}, 'veggies': None})

    def test_1_levels_2_levels(self):
        left = {'veggies': None}
        right = {'fruits': {'apples': None, 'oranges': None}}

        self.assertEqual(merge_dict(left, right), {'fruits': {'apples': None, 'oranges': None}, 'veggies': None})

    def test_empty_list(self):
        left = {'veggies': None}
        right = {}

        self.assertEqual(merge_dict(left, right), {'veggies': None})


class SuggestCompletionPayee(unittest.TestCase):
    def test_partially_written(self):
        journal = '2015/10/16 bought food\n expenses:food  $10\n assets:cash\n2015/10/17 bo'
        line = '2015/10/17 bo'
        self.assertEqual(sorted(suggest_completion(journal, [line])), ['bo', 'bought food'])

    def test_empty(self):
        journal = '2015/10/16 bought food\n expenses:food  $10\n assets:cash\n2015/10/17 '
        line = '2015/10/17 bo'
        self.assertEqual(sorted(suggest_completion(journal, [line])), ['bought food'])


class SuggestCompletionAccount(unittest.TestCase):
    def test_partially_written(self):
        journal = '2015/10/16 bought food\n expenses:food  $10\n assets:cash\n2015/10/17\n '
        line = ' '
        self.assertEqual(sorted(suggest_completion(journal, [line])), ['assets', 'expenses'])

    def test_partially_written_doublespace(self):
        journal = '2015/10/16 bought food\n expenses:food  $10\n assets:cash\n2015/10/17\n  '
        line = '  '
        self.assertEqual(sorted(suggest_completion(journal, [line])), ['assets', 'expenses'])

    def test_partially_written_1levle(self):
        journal = '2015/10/16 bought food\n expenses:food  $10\n assets:cash\n2015/10/17\n assets:\n '
        line = ' assets:'
        print(suggest_completion(journal, [line]))
        self.assertEqual(sorted(suggest_completion(journal, [line])), ['cash'])

    def test_partially_written_2levels(self):
        journal = '2015/10/16 bought food\n expenses:food  $10\n assets:cards:primary\n2015/10/17\n assets:cards:\n '
        line = ' assets:cards:'
        print(suggest_completion(journal, [line]))
        self.assertEqual(sorted(suggest_completion(journal, [line])), ['primary'])


if __name__ == '__main__':
    unittest.main()