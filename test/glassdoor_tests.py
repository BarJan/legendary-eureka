import unittest
import legendary_eureka


class GlassdoorTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.glassdoor = legendary_eureka.Glassdoor()

    def tearDown(self) -> None:
        self.glassdoor = None

    def test_get_jobs(self):
        """
        Test all get_jobs function with all possible parameters.
        """

        def all_params():
            return self.assertIsInstance(
                self.glassdoor.get_jobs(
                    job_title='Engineer',
                    job_location='Haifa',
                    job_type='fulltime'),
                dict
            )

        def title_and_location():
            return self.assertIsInstance(
                self.glassdoor.get_jobs(
                    job_title='Java',
                    job_location='Tel Aviv'),
                dict
            )

        def only_title():
            return self.assertIsInstance(
                self.glassdoor.get_jobs(
                    job_title='Python Developer'),
                dict
            )

        def wrong_location():
            return self.assertFalse(
                self.glassdoor.get_jobs(
                    job_title='Engineer',
                    job_location='Miami'
                )
            )

        def sub_tests(key):
            switcher = {
                0: all_params,
                1: title_and_location,
                2: only_title,
                3: wrong_location,
            }
            return switcher.get(key, 'Invalid test key')

        for i in range(4):

            with self.subTest(sub_tests(i).__name__):
                func = sub_tests(i)
                func()


if __name__ == '__main__':
    unittest.main()
