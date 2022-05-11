class Util:
    @staticmethod
    def _lerp(i, j, k):
        return float((1 - k) * i + j * k)


    @staticmethod
    def _invlerp(i, j, k):
        return float((k - i) / (j - i))
