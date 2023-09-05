import unittest
from unittest.mock import AsyncMock
from sqlalchemy.orm import Session

from PhotoShare.app.models.photo import Photo
from PhotoShare.app.models.user import User
from PhotoShare.app.repositories.photo import get_photos, get_photo, create_photo, update_photo, remove_photo
from PhotoShare.app.schemas.photo import PhotoModel


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=Session)
        self.user = User(id=1)

    async def test_get_photos_found(self):
        expect_res = [Photo(), ]
        self.session.query().filter().order_by().limit().offset().all.return_value = expect_res
        result = await get_photos(limit=10, offset=0, user=self.user, db=self.session)
        self.assertEqual(result, expect_res)
        self.assertListEqual(result, expect_res)

    async def test_get_photo_found(self):
        expect_res = Photo()
        self.session.query().filter().order_by().first.return_value = expect_res
        result = await get_photo(photo_id=1, user=self.user, db=self.session)
        self.assertEqual(result, expect_res)

    async def test_get_photo_not_found(self):
        self.session.query().filter().order_by().first.return_value = None
        result = await get_photo(photo_id=100, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_found(self):
        body = PhotoModel(tags_text="last, python", description="test description test test")
        result = await create_photo(body=body, url="photo_url", user=self.user,
                                    db=self.session)
        self.assertEqual(result.description, body.description)
        self.assertListEqual(result.tags, [])
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_found(self):
        expect_res = Photo()
        self.session.query().filter().first.return_value = expect_res
        result = await remove_photo(photo_id=1, user=self.user, db=self.session)
        self.assertEqual(result, expect_res)

    async def test_remove_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_photo(photo_id=100, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_photo_found(self):
        expect_res = Photo(description="old_desc")
        self.session.query().filter().first.return_value = expect_res
        update_data = PhotoModel(description="new_desc")
        result = await update_photo(photo_id=1, body=update_data, user=self.user,
                                    db=self.session)
        self.assertEqual(result.description, "new_desc")
        self.assertTrue(hasattr(result, "updated_at"))


if __name__ == '__main__':
    unittest.main()
