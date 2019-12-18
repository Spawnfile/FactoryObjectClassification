
from google.cloud import storage
from firebase import firebase

firebase = firebase.FirebaseApplication('https://bitirme-projesi-alper.firebaseio.com/')
client = storage.Client()
bucket = client.get_bucket('gs://bitirme-projesi-alper.appspot.com')

imageBlob = bucket.blob("/")
imagePaths = "/home/alper/Desktop/FactoryObjectClassification/dataset/makas/"
num = 0

for image in imagePaths:
    imageBlob.upload_from_filename(image)