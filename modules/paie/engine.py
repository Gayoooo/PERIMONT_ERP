class PayrollEngine:
    @staticmethod
    def calculer_net(salaire_base, primes, avances, retenues):
        try:
            sb = float(salaire_base) if salaire_base else 0
            p = float(primes) if primes else 0
            a = float(avances) if avances else 0
            r = float(retenues) if retenues else 0
            return (sb + p) - (a + r)
        except ValueError:
            return 0