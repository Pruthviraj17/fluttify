import uuid
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session
from database import get_db
from middleware.auth_middleware import auth_middlware
import cloudinary 
import cloudinary.uploader
from models.favorite import Favorite
from models.song import Song
from sqlalchemy.orm import joinedload

from pydantic_schemas.favorite_song import FavoriteSong

router= APIRouter()

# Configuration       
cloudinary.config( 
    cloud_name = "ddrjzrrax", 
    api_key = "139682826478568", 
    api_secret = "YDCoz_Qcen2gdg75jSAgDcY-98o", # API secret
    secure=True
)

@router.post('/upload', status_code=201)
def upload_song(song: UploadFile = File(...), 
                thumbnail: UploadFile = File(...), 
                artist: str = Form(...), 
                song_name: str = Form(...), 
                hex_code: str = Form(...),
                db: Session = Depends(get_db),
                auth_dict = Depends(auth_middlware)
                ):

    # upload files on cloudinary
    print('uploading song')

    song_id = str(uuid.uuid4())
    song_res = cloudinary.uploader.upload(song.file, resource_type='auto', folder=f'songs/{song_id}')
    thumbnail_res = cloudinary.uploader.upload(thumbnail.file, resource_type='image', folder=f'songs/{song_id}')
    
    print(f'Response of the song: \n {song_res}')
    print(f'Response of the thumbnail: \n {thumbnail_res}')

    # store data in database

    new_song= Song(
        id= song_id,
        song_url= song_res['url'],
        thumbnail_url= thumbnail_res['url'],
        artist= artist,
        song_name= song_name,
        hex_code= hex_code,
    )

    db.add(new_song)
    db.commit()
    db.refresh(new_song);

    return new_song

@router.get('/list')
def get_all_songs(db: Session= Depends(get_db),
                  auth_dict= Depends(auth_middlware)
                  ):
    all_songs= db.query(Song).all()
    return all_songs

@router.post('/favorite')
def favorite_song(song: FavoriteSong, 
                  db: Session=Depends(get_db), 
                  auth_details=Depends(auth_middlware)):
    # song is already favorited by the user
    user_id = auth_details['uid']

    fav_song = db.query(Favorite).filter(Favorite.song_id == song.song_id, Favorite.user_id == user_id).first()

    if fav_song:
        db.delete(fav_song)
        db.commit()
        return {'message': False}
    else:
        new_fav = Favorite(id=str(uuid.uuid4()), song_id=song.song_id, user_id=user_id)
        db.add(new_fav)
        db.commit()
        return {'message': True}
    
@router.get('/list/favorites')
def list_fav_songs(db: Session=Depends(get_db), 
               auth_details=Depends(auth_middlware)):
    user_id = auth_details['uid']
    fav_songs = db.query(Favorite).filter(Favorite.user_id == user_id).options(
        joinedload(Favorite.song),
    ).all()
    
    return fav_songs