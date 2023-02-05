
import os
import csv
import sys
import unittest
from unittest.mock import patch
sys.path.append('..')
import db_utils

test_users = {
    "ivan": ["123, 456, 789", "hi"],
}

class Test_init_db(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Started init_db_tests")
        return
    
    def test_creates_db_file(self):
        db_fn = "test"
        db_utils.init_db(db_fn)
        self.assertTrue(os.path.exists(f"{db_fn}.csv"))
        os.remove(f"{db_fn}.csv")
    
    @classmethod
    def tearDownClass(cls):
        print("Finished init_db_tests")
        return

class Test_save_db_to_disk(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Started save_db_to_disk_tests")
        return
    
    def setUp(self) -> None:
        db_utils.users = test_users
        return

    def test_saves_users_to_disk(self):
        db_fn = "test"
        db_utils.init_db(db_fn)
        db_utils.save_db_to_disk(db_fn)
        saved_users = {}
        with open(f"{db_fn}.csv", "r+") as f:
            db_reader = csv.reader(
                f, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True
            )
            for line in db_reader:
                saved_users[line[0]] = line[1:]
        self.assertEqual(saved_users, test_users)
        os.remove(f"{db_fn}.csv")
    
    @classmethod
    def tearDownClass(cls):
        print("Finished save_db_to_disk_tests")
        return

if __name__ == '__main__':
    unittest.main()