from django.urls import path
from play.views import *    

urlpatterns = [
    path('',HomePage,name='Homeplay'),
    path('watch/',HomePage,name='Homeplay'),
    path('playlist/',ExtractPlaylistVideos,name='Playlist'),
    path('newsong/',GetNewSong,name='Playlist'),
    path('login/',LogIn,name='login'),
    path('signup/',Signup,name='login'),
    path('createqr/',Signup,name='login'),
    path('search/',SearchNewItem,name='search'),
    path('relatedvideos/',GetRelatedVideos,name='search'),
    path('create_Qr/',CreateQrCode,name='search'),
    path('getimage/',generate_image,name='search'),
    path('get-pdf/', get_pdf, name='get_pdf'),

]