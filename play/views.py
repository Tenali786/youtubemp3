# |||||||||||||||||||||||||||| These are the django modules |||||||||||||||||||||||||||||||||||
from django.shortcuts import render,redirect
from django.shortcuts import render,HttpResponse
from django.conf import settings
# ||||||||||||||||||||||||||||| These are the comman python modules |||||||||||||||||||||||||||||||||||
from contextlib import suppress
from urllib.parse import urlparse, parse_qs
from PIL import Image
import io,segno,os
import yt_dlp,requests
import json

# this is the home page without any song loaded
def HomePage(request):
    
    context = {}
    PlaylistUrls = []
    
    
    if request.method=="GET":
        videoId = request.GET.get('v')
        playlistId = request.GET.get('list')
        
        
        context['playlist'] = PlaylistUrls
        context['VideoId'] = videoId
        context['isPlaylist'] = False if playlistId is None else True
        context['cards'] = range(20)
            
        return render(request=request,template_name='index2.html',context=context)
   
    return render(request,'index2.html',context)

# @csrf_exempt
def GetNewSong(request):
    if request.method=='POST':
        videoUrl = request.POST.get('url')
        print('hello')
        url,title = ExtractOneVideo(videoUrl)
        print('hi')
        return HttpResponse(json.dumps({'url':url,'title':title,'videoid':videoUrl,'filename':title+'.mp3'}))

    return HttpResponse(json.dumps({}))
     
def ExtractOneVideo(url):
    """Gets the YouTube video MP3 download URL using yt-dlp.

    Args:
        youtube_video_url: The URL of the YouTube video.

    Returns:
        The MP3 download URL, or None if the video cannot be downloaded.
    """
    ydl = yt_dlp.YoutubeDL({'format': 'bestaudio'})
    info = ydl.extract_info(url, download=False)

    # If the video cannot be downloaded, return None.
    if not info:
        return None

    # Get the MP3 download URL.
    title = info.get('title')
    mp3_download_url = info.get('formats')
    DownloadUrl = None
    for videos in mp3_download_url:
        if videos.get("audio_ext")== "m4a":
            DownloadUrl = videos.get('url')
            break

    return DownloadUrl,title


def get_yt_id(url, ignore_playlist=False):
    # Examples:
    # - http://youtu.be/SA2iWivDJiE
    # - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    # - http://www.youtube.com/embed/SA2iWivDJiE
    # - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US

    query = urlparse(url)
    if query.hostname == 'youtu.be': return query.path[1:]
    if query.hostname in {'www.youtube.com', 'youtube.com', 'music.youtube.com'}:
        if not ignore_playlist:
        # use case: get playlist id not current video in playlist
            with suppress(KeyError):
                return parse_qs(query.query)['list'][0]
            
        if query.path == '/watch': return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/watch/': return query.path.split('/')[1]
        if query.path[:7] == '/embed/': return query.path.split('/')[2]
        if query.path[:3] == '/v/': return query.path.split('/')[2]
   # returns None for invalid YouTube url

contentUrls = []
def ExtractPlaylistVideos(request):
    global contentUrls
    contentUrls = []
    # _-------------------------------------------- Methos First ----------------------------------------------
    # dataUrls = {}
    # PlaylistVideos = []
    
    # if request.method=="POST":

    #     playlistId = request.POST.get('videoid')
    #     print("Video id  ",playlistId) #https://www.youtube.com/playlist?list=PL9bw4S5ePsEEqCMJSiYZ-KTtEjzVy0YvK
    #     PlaylistVideos = Playlist(url=f"https://www.youtube.com/watch?list={playlistId}")
    #     PlaylistVideos._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")
    #     print("Video id  ",PlaylistVideos)
        
    #     VideoUrls =  PlaylistVideos.video_urls if len(PlaylistVideos)>0 else []

    #     data = {}  
    #     for i,item in enumerate(VideoUrls):
    #         data[i] = item

    #     dataUrls['title'] = PlaylistVideos.title if len(PlaylistVideos)>0 else '' 
    #     dataUrls['length'] = PlaylistVideos.length if len(PlaylistVideos)>0 else '' 
    #     dataUrls['Views'] = PlaylistVideos.views if len(PlaylistVideos)>0 else '' 
    #     dataUrls['Urls'] = data
    #     return HttpResponse(json.dumps(dataUrls))

    # return HttpResponse(json.dumps(dataUrls))
    
    # _-------------------------------------------- Methos Second ----------------------------------------------
    def GetNext(playlistid,next=None):
        global contentUrls
        
        if next is None:
            querystring = {"id":playlistid}
        else:
            querystring = {"id":playlistid,'next':next}

        url = "https://youtube-search-and-download.p.rapidapi.com/playlist"

        

        headers = {
            "X-RapidAPI-Key": "8cacaff4e4msh4fee6493b9185f4p1fec8cjsna481c4a0f8b0",
            "X-RapidAPI-Host": "youtube-search-and-download.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)


        urlData = response.json()
        print("Platlist data is : ",urlData)
        contentUrls = contentUrls+urlData.get('contents')

        if urlData.get('next')!=None:
            GetNext(playlistid=playlistid,next=urlData.get('next'))
            

        urlData['contents'] = contentUrls
        return urlData
    
    
    mainContentData = {}
    
    if request.method=="POST":
        
        playlistid = request.POST.get('videoid')
        print("playlist id : ",playlistid)

        if playlistid!=None:

            
            urlData = GetNext(playlistid=playlistid)

            content = urlData.get('contents')
            print("The len of content : ",len(content))
            
            if len(content)>0:
                    mainContentData['title'] = urlData.get('title')
                    mainContentData['length'] = urlData.get('videosCount')
                    mainContentData['Views'] = urlData.get('views')
                    mainContentData['lastUpdated'] = urlData.get('lastUpdated')

                    urlsDict = {}
                    for i,item in enumerate(content):
                        newVideo ={}
                        Oldvideo = item.get('video')
                        newVideo['title'] = Oldvideo.get('title')
                        newVideo['url'] = 'https://www.youtube.com/watch?v='+Oldvideo.get('videoId')
                        urlsDict[i] = newVideo
                        
                    mainContentData['Urls'] = urlsDict
            # print(mainContentData)
                    
            return HttpResponse(json.dumps(mainContentData))          
                    
                
    return HttpResponse(json.dumps(mainContentData))

def SearchNewItem(request):
    if request.method=="POST":
        NewdataItem = {}
        query = request.POST.get("query")


        url = "https://yt-api.p.rapidapi.com/search"

        querystring = {"query":query}

        headers = {
            "X-RapidAPI-Key": "8cacaff4e4msh4fee6493b9185f4p1fec8cjsna481c4a0f8b0",
            "X-RapidAPI-Host": "yt-api.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        newdata = response.json()

        NewdataItem['videos'] = [item for item in newdata['data'] if item['type']=='video']

        return HttpResponse(json.dumps(NewdataItem))

    return HttpResponse(json.dumps({}))


def GetRelatedVideos(request):
    if request.method=="POST":
        videoid = request.POST.get('id')
        url = "https://youtube-search-and-download.p.rapidapi.com/video/related"

        querystring = {"id":videoid}

        headers = {
            "X-RapidAPI-Key": "8cacaff4e4msh4fee6493b9185f4p1fec8cjsna481c4a0f8b0",
            "X-RapidAPI-Host": "youtube-search-and-download.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        related_data = response.json()
        print("Related data is : ",related_data)
        return HttpResponse(json.dumps(related_data)) 
            
        

    return HttpResponse(json.dumps({})) 

def LogIn(request):
    return render(request,'login.html')

def Signup(request):
    return render(request,'signup.html')


def CreateQrCode(request):
    if request.method=="GET":
        # Import QRCode from pyqrcode 
        import segno,os

        data_url = request.GET.get("data_url")
        
        print("the data url is : ",data_url)
        filepath = os.path.join(settings.BASE_DIR,'static','files','qrcode.png')
        
        
        qr = segno.make_qr(data_url.replace('__',"&"))
        qr.save(filepath,
                scale=8,
                border=1,
                )
        
        return redirect(f'/static/files/qrcode.png?data_url={data_url}')

    return HttpResponse(json.dumps({}))

def generate_image(request):
    # Create a blank image
    if request.method=='GET':
        data_url = request.GET.get("data_url")
        filepath = os.path.join(settings.BASE_DIR,'static','files','qrcode.png')
        if data_url is not None:
            # data_url = data_url.replace('-','\n')
                
            qr = segno.make_qr(data_url.replace('__',"&"))
            qr.save(filepath,scale=8,border=1,)
            
        if not os.path.exists(filepath):
            filepath = os.path.join(settings.BASE_DIR,'static','files','icon1.png')
            
        image = Image.open(filepath)
        image = Image.open(filepath)
        # Save the image to a byte buffer
        image_buffer = io.BytesIO()
        image.save(image_buffer, format='PNG')
        image_buffer.seek(0)

        # Return the image as an HTTP response
        return HttpResponse(image_buffer, content_type='image/png')


    return {}

def get_pdf(request):
    # Path to the PDF file on your server
    pdf_file_path = os.path.join(settings.BASE_DIR, 'static','Lover (2022) {Hindi + Punjabi} Dual Audio Full Movie HD 720p ESub.mkv')

    # Open the PDF file for reading
    # with open(pdf_file_path, 'rb') as pdf_file:
    #     response = HttpResponse(pdf_file.read(), content_type='application/zip')
        
    #     response['Content-Disposition'] = f'filename=""'

    #     return response
    return redirect('/static/Lover (2022) {Hindi + Punjabi} Dual Audio Full Movie HD 720p ESub.mkv')