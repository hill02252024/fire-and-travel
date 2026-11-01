import unittest


def fire_target(monthly_spending, withdrawal_rate):
    return monthly_spending * 12 / withdrawal_rate


def real_return(nominal_return, inflation):
    return (1 + nominal_return) / (1 + inflation) - 1


def travel_budget(months, travel_monthly, home_monthly, one_off, buffer):
    return months * (travel_monthly + home_monthly) + one_off + buffer


class CalculatorTests(unittest.TestCase):
    def test_fire_target(self):
        self.assertEqual(fire_target(20000, 0.04), 6000000)

    def test_real_return(self):
        self.assertAlmostEqual(real_return(0.05, 0.02), 0.02941176470588236)

    def test_travel_budget(self):
        self.assertEqual(travel_budget(3, 18000, 8000, 12000, 30000), 120000)


if __name__ == "__main__":
    unittest.main()
