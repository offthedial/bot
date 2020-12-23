from firebase_admin import credentials, firestore
import firebase_admin

cred = credentials.Certificate("service_account.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
