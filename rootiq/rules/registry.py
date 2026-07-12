class RuleRegistry:

    def __init__(self):

        self._rules = []

    def register(self, rule):

        self._rules.append(rule)

    def all(self):

        return self._rules