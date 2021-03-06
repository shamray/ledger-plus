import re


def is_transaction_header(line):
    date = '(?P<date>[\\d\\./-]+)'
    return re.match('^' + date + '.*', line) is not None


def is_posting(line):
    return re.match('^' + ' |\\t' + '.*', line) is not None


def parse_payee(line):
    date = '(?P<date>[\\d\\./-]+)'
    mark = '([!|*] )?'
    payee = '(?P<payee>.*)'
    m = re.match('^' + date + '(' + ' ' + mark + payee + ')?', line)
    if not m:
        return None

    parsed = m.group('payee')

    return None if parsed == '' else parsed


def parse_account_string(line):
    if line == '':
        return None

    if line[0] != ' ' and line[0] != '\t':
        return None

    tokens = re.split('  +|\t', line.lstrip())
    if len(tokens) < 1 or tokens[0] == '':
        return None

    return tokens[0]


def to_account(line):
    if line is None:
        return {}

    parts = line.split(':')
    acc = None

    for part in reversed(parts):
        acc = {part: acc}

    return acc


def merge_dict(left, right):
    assert(isinstance(left, dict) or left is None)
    assert(isinstance(right, dict) or right is None)

    if left is None:
        return right
    elif right is None:
        return left

    for key, value in right.items():
        if key not in left:
            left[key] = value
        else:
            left[key] = merge_dict(left[key], value)

    return left


def parse(journal):
    payees = set()
    accounts = {}

    for line in journal.splitlines():
        if not parse_payee(line) is None:
            payees.add(parse_payee(line))
        elif not parse_account_string(line) is None:
            accounts = merge_dict(accounts, to_account(parse_account_string(line)))

    return sorted(list(payees)), accounts


def get_first_key(dic):
    keys = list(dic.keys())
    if len(keys) == 0:
        return None
    else:
        return keys[0]


def normalize(keys):
    return [x.strip() for x in keys if x.strip() != '']


def suggest_completion(content, locations):
    __is_transaction_header = True
    __is_posting = True

    for loc in locations:
        __is_transaction_header = False if not is_transaction_header(loc) else is_transaction_header
        __is_posting = False if not is_posting(loc) else __is_posting

    if __is_posting == __is_transaction_header:
        return None

    payees, accounts = parse(content)
    if __is_transaction_header:
        return normalize(payees)
    elif __is_posting:
        for loc in locations:
            if parse_account_string(loc) is None:
                return normalize(accounts.keys())

            account = to_account(parse_account_string(loc[:loc.rfind(':')]))
            while True:
                if accounts is None:
                    return normalize(accounts.keys())

                if account is None or get_first_key(account) not in accounts.keys():
                    return normalize(accounts.keys())
                else:
                    accounts = accounts[get_first_key(account)]
                    account = account[get_first_key(account)]
    else:
        assert False
