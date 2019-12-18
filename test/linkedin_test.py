import unittest.test
import legendary_eureka


class linkedinTest(unittest.TestCase):
    def setUp(self) -> None:
        self.linkedin = legendary_eureka.Linkedin()

    def tearDown(self) -> None:
        self.linkedin = None

    def test_jobs(self):
        return self.assertIsInstance(
            self.linkedin.get_jobs(
                url='https://www.linkedin.com/jobs/search/?geoId=101620260&keywords=student%20developer&location=Israel'),
            dict
        )


if __name__ == '__main__':
    unittest.main()
