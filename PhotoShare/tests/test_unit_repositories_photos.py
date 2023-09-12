import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from PhotoShare.app.models.photo import Photo
from PhotoShare.app.models.user import User
from PhotoShare.app.repositories.photo import get_photos, get_photo, create_photo, update_photo, remove_photo
from PhotoShare.app.schemas.photo import PhotoModel


class TestPhoto(unittest.TestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    def test_get_photos_found(self):
        expect_res = [Photo(), Photo()]
        self.session.execute().scalars().all.return_value = expect_res
        result = get_photos(limit=2, offset=0, db=self.session)
        self.assertEqual(result, expect_res)

    def test_get_photo_found(self):
        expect_res = Photo()
        self.session.execute().scalar_one_or_none.return_value = expect_res
        result = get_photo(photo_id="photo_id", user=self.user, db=self.session)
        self.assertEqual(result, expect_res)

    def test_get_photo_not_found(self):
        self.session.execute.return_value.scalar_one_or_none.return_value = None
        result = get_photo(photo_id="photo_id", user=self.user, db=self.session)
        self.assertIsNone(result)

    def test_create_found(self):
        body = PhotoModel(name="Test Photo", description="new_desc", photo_url="test_url")
        result = create_photo(body=body, photo_url="photo_url", user=self.user, db=self.session)
        self.assertEqual(result.description, body.description)
        self.assertTrue(hasattr(result, "id"))

    def test_get_photo_from_id_found(self):
        expect_res = Photo()
        self.session.execute().scalar_one_or_none.return_value = expect_res
        result = get_photo(photo_id="photo_id", user=self.user, db=self.session)
        self.assertEqual(result, expect_res)

    def test_get_photo_from_id_not_found(self):
        self.session.execute().scalar_one_or_none.return_value = None
        result = get_photo(photo_id="photo_id", user=self.user, db=self.session)
        self.assertIsNone(result)

    def test_get_photo_from_url_found(self):
        expect_res = Photo()
        self.session.execute().scalar_one_or_none.return_value = expect_res
        result = get_photo(photo_id="photo_id", user=self.user, db=self.session)
        self.assertEqual(result, expect_res)

    def test_get_photo_from_url_not_found(self):
        self.session.execute().scalar_one_or_none.return_value = None
        result = get_photo(photo_id="", user=self.user, db=self.session)
        self.assertIsNone(result)

    def test_remove_found(self):
        expect_res = Photo()
        self.session.execute().scalar_one_or_none.return_value = expect_res
        result = remove_photo(photo_id=1, user=self.user, db=self.session)
        self.assertEqual(result, expect_res)

    def test_remove_not_found(self):
        self.session.execute().scalar_one_or_none.return_value = None
        result = remove_photo(photo_id=100, user=self.user, db=self.session)
        self.assertIsNone(result)

    def test_update_photo_found(self):
        expect_res = Photo(description="old_desc")
        body = PhotoModel(name="test_name", description="new_desc", tags="last, python", photo_url="test_url")
        self.session.query().filter().first.return_value = expect_res
        self.session.commit.return_value = None
        result = update_photo(photo_id=1, body=body, user=self.user, db=self.session)
        self.assertEqual(result.description, "new_desc")
        self.assertTrue(hasattr(result, "updated_at"))

    def test_change_description_not_found(self):
        body = PhotoModel(name="test_name", description="test description test test", tags="last, python",
                          photo_url="test_url")
        self.session.execute().scalar_one_or_none.return_value = None
        self.session.commit.return_value = None
        result = update_photo(body=body, photo_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
