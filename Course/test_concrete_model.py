import unittest

from concrete_model import predict_strength, train_model


class ConcreteModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Обучаем модель один раз для всех проверок
        cls.model = train_model()

    def setUp(self):
        self.recipe = {
            "cement": 326,
            "slag": 90,
            "fly_ash": 75,
            "water": 182,
            "superplasticizer": 6,
            "coarse_aggregate": 1000,
            "fine_aggregate": 770,
            "age": 28,
        }

    def test_valid_recipe(self):
        strength = predict_strength(self.model, self.recipe)
        self.assertIsInstance(strength, float)
        self.assertGreater(strength, 0)
        print(f"Тест прошёл")

    def test_field_order_does_not_change_prediction(self):
        reversed_recipe = dict(reversed(list(self.recipe.items())))
        self.assertEqual(
            predict_strength(self.model, self.recipe),
            predict_strength(self.model, reversed_recipe),
        )
        print(f"Тест прошёл")

    def test_zero_additive_is_allowed(self):
        recipe = dict(self.recipe, fly_ash=0)
        self.assertGreater(predict_strength(self.model, recipe), 0)
        print(f"Тест прошёл")

    def test_missing_field(self):
        del self.recipe["water"]
        with self.assertRaisesRegex(ValueError, "water"):
            predict_strength(self.model, self.recipe)
        print(f"Тест прошёл")

    def test_negative_amount(self):
        recipe = dict(self.recipe, cement=-10)
        with self.assertRaisesRegex(ValueError, "cement"):
            predict_strength(self.model, recipe)
        print(f"Тест прошёл")

    def test_invalid_age(self):
        for age in (0, 2.5):
            with self.subTest(age=age):
                recipe = dict(self.recipe, age=age)
                with self.assertRaisesRegex(ValueError, "Возраст"):
                    predict_strength(self.model, recipe)
        print(f"Тест прошёл")

    def test_invalid_number(self):
        for water in ("вода", float("nan"), float("inf")):
            with self.subTest(water=water):
                recipe = dict(self.recipe, water=water)
                with self.assertRaisesRegex(ValueError, "water"):
                    predict_strength(self.model, recipe)
        print(f"Тест прошёл")


if __name__ == "__main__":
    unittest.main(verbosity=0)
