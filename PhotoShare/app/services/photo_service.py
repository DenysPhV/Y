import hashlib

import cloudinary
import cloudinary.uploader

from PhotoShare.app.core.config import settings


class CloudinaryService:

    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    @staticmethod
    def get_public_id(filename: str) -> str:

        """
        The get_public_id function takes a filename as an argument and returns the public_id of that file.
        The public_id is used to identify files in Cloudinary's database. The function uses SHA256 hashing to
        generate a unique hash for each file, then truncates it down to 10 characters.

        :param filename: str: Specify the name of the file that is being uploaded
        :return: A string that is the filename hashed with sha256 and then sliced to 10 characters
        :doc-author: Trelent
        """
        public_id = hashlib.sha256(filename.encode()).hexdigest()[:10]
        return f"Y/{public_id}"

    @staticmethod
    def upload_photo(file, public_id):

        """
        The upload_photo function takes in a file and public_id as arguments.
        It then uploads the file to cloudinary using the public_id provided.
        The function returns a photo object.

        :param file: Specify the path to the image file
        :param public_id: Specify the name of the file that is uploaded to cloudinary
        :return: A dictionary with the following keys:
        :doc-author: Trelent
        """
        photo = cloudinary.uploader.upload(file, public_id=public_id)
        return photo

    @staticmethod
    def get_photo(public_id: str, version: str) -> str:

        """
        The get_photo function takes in a public_id and version number, and returns the url of the photo.
            The function uses Cloudinary's build_url method to create a url for an image with specific parameters.
            The parameters are: width=200, height=200, crop='fill', version=&lt;the inputted version&gt;.


        :param public_id: str: Specify the public id of the image
        :param version: str: Specify the version of the image to be used
        :return: The url of the image
        :doc-author: Trelent
        """
        photo_url = cloudinary.CloudinaryImage(public_id).build_url(width=200, height=200, crop='fill', version=version)
        return photo_url

    @staticmethod
    def edit_photo(photo: str, gravity: str, height: int, width: int, crop: str, radius: str, color: str,
                   effect: str, zoom: float, angle: int) -> str:

        """
        The edit_photo function takes in a photo, and returns the edited version of that photo.
        The function uses Cloudinary's image() method to edit the photo using transformations.
        The transformations are specified as a list of dictionaries, where each dictionary is one transformation.

        :param photo: str: Pass the photo to be edited
        :param gravity: str: Set the position of the image
        :param height: int: Set the height of the image
        :param width: int: Set the width of the image
        :param crop: str: Crop the image
        :param radius: str: Round the corners of the image
        :param color: str: Change the color of the image
        :param effect: str: Add an effect to the image
        :param zoom: float: Zoom in on the image
        :param angle: int: Rotate the image by a certain degree
        :return: A string
        :doc-author: Trelent
        """
        photo_edit = cloudinary.CloudinaryImage(photo).image(transformation=[
            {'gravity': gravity, 'height': height, 'width': width, 'crop': crop},
            {'radius': radius},
            {'width': width, 'crop': "scale"},
            {'fetch_format': "auto"}
        ])
        return photo_edit
